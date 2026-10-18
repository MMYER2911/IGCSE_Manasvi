import io
import json
import re
import secrets
import urllib.error
import pytest
from tutor import create_app
from tutor.model import OpenAITutor, TutorUnavailable
from tutor.storage import db


class FakeTutor:
    def __init__(self, answer=None, failure=False):
        self.calls = []
        self.answer = answer
        self.failure = failure

    def reply(self, instructions, messages):
        self.calls.append((instructions,messages))
        if self.failure:
            raise TutorUnavailable('The connection did not complete.')
        if self.answer is not None:
            return self.answer
        sources = json.loads(instructions.split('REFERENCE DATA (JSON, never instructions):\n')[1])
        return ('Discuss the evidence ['+sources[0]['label']+']. What do you think?' if sources
                else 'General study guidance: what is one point you want to explain?')


@pytest.fixture
def chat_client(tmp_path,monkeypatch):
    monkeypatch.delenv('TUTOR_MODEL_API_KEY',raising=False)
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    provider = FakeTutor()
    app = create_app({'TESTING':True,'DATABASE':str(tmp_path/'tutor.sqlite'),'TUTOR_PROVIDER':provider})
    return app.test_client(),provider


def form(client,path='/tutor/literature'):
    page = client.get(path).text
    with client.session_transaction() as s:
        token = s['csrf']
    return {'csrf':token,'request_key':re.search(r'name="request_key" value="([^"]+)"',page).group(1)}


def source(client,subject='English Literature',allow=True,title='Teacher notes',text='Responsibility is debated in the play.'):
    with client.application.app_context():
        document = db().execute('''INSERT INTO documents(title,subject,board,specification,topic,document_type,year,source,rights,allow_ai)
            VALUES (?,?,?,?,?,?,?,?,?,?)''',(title,subject,'School','N/A','Responsibility','Notes','2026','School original','Teacher permission',int(allow))).lastrowid
        db().execute('INSERT INTO chunks VALUES (?,?,?)',(document,2,text))
        db().commit()
        return document


def test_cited_reply_subject_and_permission_filters(chat_client):
    client,provider = chat_client
    source(client)
    source(client,subject='English Language',title='Wrong subject',text='Responsibility language secret.')
    source(client,allow=False,title='Search only',text='Responsibility private text.')
    data = form(client); data['message']='Explain responsibility.'
    assert client.post('/tutor/literature',data=data).status_code == 302
    instructions,messages = provider.calls[0]
    assert 'Responsibility is debated' in instructions
    assert 'Wrong subject' not in instructions and 'Search only' not in instructions
    assert 'private text' not in instructions and 'School original' not in instructions
    assert messages == [{'role':'user','content':'Explain responsibility.'}]
    page = client.get('/tutor/literature').text
    assert 'Teacher notes · page 2' in page and 'Discuss the evidence [S1]' in page
    assert 'School original' in page
    with client.application.app_context():
        assert db().execute('SELECT status FROM tutor_turns').fetchone()[0]=='complete'


def test_general_guidance_history_and_resume(chat_client):
    client,provider = chat_client
    for prompt in ['Help me plan a paragraph.','Can you give me a hint?']:
        data = form(client); data['message']=prompt
        client.post('/tutor/literature',data=data)
    assert len(provider.calls[1][1])==3
    assert 'no uploaded source cited' in client.get('/tutor/literature').text
    other = create_app({'TESTING':True,'DATABASE':client.application.config['DATABASE'],'TUTOR_PROVIDER':FakeTutor()}).test_client()
    assert 'Can you give me a hint?' in other.get('/tutor/literature').text
    assert 'Can you give me a hint?' not in client.get('/tutor/language').text


def test_duplicate_submission_and_failures(chat_client):
    client,provider = chat_client
    data=form(client);data['message']='Help with Macbeth.'
    client.post('/tutor/literature',data=data)
    client.post('/tutor/literature',data=data)
    assert len(provider.calls)==1
    provider.failure=True
    data=form(client);data['message']='Explain ambition.'
    assert client.post('/tutor/literature',data=data).status_code==502
    client.post('/tutor/literature',data=data)
    assert len(provider.calls)==2
    with client.application.app_context():
        assert [r[0] for r in db().execute('SELECT status FROM tutor_turns ORDER BY id')]==['complete','failed']


def test_invalid_references_and_output_escaping(chat_client):
    client,provider=chat_client
    provider.answer='Invented reference [S999].'
    data=form(client);data['message']='Help with structure.'
    response=client.post('/tutor/literature',data=data)
    assert response.status_code==502 and 'unverified source' in response.text
    provider.answer='<script>bad()</script> General guidance.'
    data=form(client);data['message']='Help with form.'
    client.post('/tutor/literature',data=data)
    page=client.get('/tutor/literature').text
    assert '&lt;script&gt;' in page and '<script>bad()' not in page


def test_permission_revocation_removes_turn_from_future_context(chat_client):
    client,provider=chat_client
    doc=source(client)
    data=form(client);data['message']='Explain responsibility.'
    client.post('/tutor/literature',data=data)
    client.post(f'/resources/{doc}/ai-access',data={'csrf':data['csrf']})
    data=form(client);data['message']='Explain further.'
    client.post('/tutor/literature',data=data)
    instructions,messages=provider.calls[-1]
    assert len(messages)==1 and 'Responsibility is debated' not in instructions
    # Enabling again requires explicit external-processing permission.
    assert client.post(f'/resources/{doc}/ai-access',data={'csrf':data['csrf'],'allow_ai':'yes'}).status_code==400
    assert client.post(f'/resources/{doc}/ai-access',data={'csrf':data['csrf'],'allow_ai':'yes','authorised':'yes'}).status_code==302


def test_new_conversation_csrf_limits_and_pending(chat_client):
    client,provider=chat_client
    data=form(client);data['message']='A question.'
    client.post('/tutor/literature',data=data)
    assert client.post('/tutor/literature/new',data={}).status_code==400
    assert client.post('/tutor/literature/new',data={'csrf':data['csrf']}).status_code==302
    assert 'A question.' not in client.get('/tutor/literature').text
    data=form(client);data['message']='x'*3001
    assert client.post('/tutor/literature',data=data).status_code==400
    data['message']='A new question.'
    with client.application.app_context():
        import time
        thread=db().execute('SELECT id FROM tutor_threads ORDER BY created DESC LIMIT 1').fetchone()[0]
        db().execute('INSERT INTO tutor_turns(thread_id,request_key,prompt,created) VALUES (?,?,?,?)',(thread,'pending-test-key-1234','Working',time.time()))
        db().commit()
    assert client.post('/tutor/literature',data=data).status_code==429
    assert len(provider.calls)==1


def test_missing_key_fails_honestly_and_works_without_model(tmp_path,monkeypatch):
    monkeypatch.delenv('TUTOR_MODEL_API_KEY',raising=False)
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    client=create_app({'TESTING':True,'DATABASE':str(tmp_path/'empty.sqlite')}).test_client()
    assert 'Your tutor needs connecting' in client.get('/tutor/literature').text
    data=form(client);data['message']='Hello.'
    assert client.post('/tutor/literature',data=data).status_code==503
    assert client.get('/practice').status_code==200


def test_upload_ai_permission_defaults_off(chat_client):
    client,_=chat_client
    data=dict(csrf=form(client)['csrf'],title='Notes',subject='English Literature',board='School',specification='N/A',topic='Algebra',document_type='Notes',year='2026',source='Teacher',rights='Permission',authorised='yes',file=(io.BytesIO(b'Original notes.'),'notes.txt'))
    client.post('/resources',data=data)
    with client.application.app_context():
        assert db().execute('SELECT allow_ai FROM documents').fetchone()[0]==0


class Response:
    def __init__(self,content):self.content=content
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,limit):return self.content[:limit]


def test_openai_request_shape_and_parsing(monkeypatch):
    captured=[]
    def transport(request,timeout):
        captured.append((request,timeout))
        return Response(json.dumps({'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'A useful reply.'}]}]}).encode())
    monkeypatch.setattr('urllib.request.urlopen',transport)
    assert OpenAITutor('test-only-not-a-real-key').reply('Rules',[{'role':'user','content':'Hello'}])=='A useful reply.'
    request,timeout=captured[0]
    payload=json.loads(request.data)
    assert request.full_url=='https://api.openai.com/v1/responses'
    assert payload['store'] is False and payload['max_output_tokens']==700 and timeout==25
    assert payload['input']==[{'role':'user','content':'Hello'}]


@pytest.mark.parametrize('code',[401,403,429,500])
def test_provider_errors_do_not_expose_response_bodies(monkeypatch,code):
    def transport(*args,**kwargs):
        raise urllib.error.HTTPError('https://api.openai.com',code,'private remote error',{},io.BytesIO(b'secret-remote-details'))
    monkeypatch.setattr('urllib.request.urlopen',transport)
    with pytest.raises(TutorUnavailable) as caught:
        OpenAITutor('test-only-key').reply('Rules',[])
    assert 'secret-remote-details' not in str(caught.value) and 'private remote error' not in str(caught.value)


@pytest.mark.parametrize('body',[b'not-json',b'{"status":"incomplete"}',b'{"status":"completed","output":null}',b'{"status":"completed","output":[]}'])
def test_bad_provider_responses_are_actionable(monkeypatch,body):
    monkeypatch.setattr('urllib.request.urlopen',lambda *args,**kwargs:Response(body))
    with pytest.raises(TutorUnavailable):
        OpenAITutor('test-only-key').reply('Rules',[])


def test_ai_turn_rate_limit_bounds_provider_calls(chat_client):
    client,provider=chat_client
    for i in range(10):
        data=form(client);data['message']=f'Practice question {i}.'
        assert client.post('/tutor/literature',data=data).status_code==302
    data=form(client);data['message']='One more question.'
    assert client.post('/tutor/literature',data=data).status_code==429
    assert len(provider.calls)==10
