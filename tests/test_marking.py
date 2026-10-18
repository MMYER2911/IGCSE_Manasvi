import copy
import json
import secrets
import pytest
from tutor import create_app
from tutor.marking import eligible, parse_pages, prepare, validate_assessment
from tutor.storage import db
from test_tutor import FakeTutor, form, Response


class AssessmentTutor(FakeTutor):
    def __init__(self):
        super().__init__()
        self.assess_calls=[]
        self.override=None

    def assess(self,instructions,messages):
        self.assess_calls.append((instructions,messages))
        task=json.loads(instructions.split('SELECTED TASK (JSON):\n')[1].split('\nRUBRIC DATA (JSON):\n')[0])
        sources=json.loads(instructions.split('RUBRIC DATA (JSON):\n')[1])
        return copy.deepcopy(self.override) if self.override is not None else {
            'assessable':True,'mark':3,'max_marks':task['max_marks'],
            'justification':'The response supports an interpretation but needs closer analysis.',
            'strength':'A clear point.','improvement':'Explain the effect of a specific method.',
            'revision_task':'Revise one analytical sentence.', 'scheme_references':[sources[0]['label']]}


@pytest.fixture
def marking_client(tmp_path,monkeypatch):
    monkeypatch.delenv('TUTOR_MODEL_API_KEY',raising=False)
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    provider=AssessmentTutor()
    app=create_app({'TESTING':True,'DATABASE':str(tmp_path/'marking.sqlite'),'TUTOR_PROVIDER':provider})
    client=app.test_client()
    with app.app_context():
        doc=db().execute('''INSERT INTO documents(title,subject,board,specification,topic,document_type,year,source,rights,allow_ai)
            VALUES (?,?,?,?,?,?,?,?,?,?)''',('2022 scheme','English Literature','Pearson Edexcel','4ET1','Responsibility','Mark scheme','2022','https://qualifications.pearson.com/example.pdf','Parent confirms authorised use',1)).lastrowid
        db().execute('INSERT INTO chunks VALUES (?,?,?)',(doc,1,'Original test rubric: general marking instructions.'))
        db().execute('INSERT INTO chunks VALUES (?,?,?)',(doc,8,'Original test rubric: question 1, levels, descriptors and allocation.'))
        db().commit()
    return client,provider,doc


def registration(client,doc,**changes):
    data={'csrf':form(client)['csrf'],'document_id':str(doc),'component':'4ET1/01',
        'exam_session':'May/June','question_number':'1','max_marks':'5','pages':'1,8',
        'question_text':'Explain a character’s attitude to responsibility.','confirmed':'yes'}
    data.update(changes)
    return data


def register(client,doc):
    assert client.post('/marking',data=registration(client,doc)).status_code==302
    with client.application.app_context():
        return db().execute('SELECT id FROM marking_rubrics').fetchone()[0]


def test_marking_pins_paper_question_pages_and_persists_provisional_result(marking_client):
    client,provider,doc=marking_client
    rubric_id=register(client,doc)
    data=form(client)
    data.update(mode='mark',rubric_id=str(rubric_id),message='My analytical answer about responsibility.')
    assert client.post('/tutor/literature',data=data).status_code==302
    instructions,messages=provider.assess_calls[0]
    assert '"year": "2022"' in instructions and '"question_number": "1"' in instructions
    assert 'general marking instructions' in instructions and 'levels, descriptors' in instructions
    assert len(messages)==1 and messages[0]['content']==data['message']
    assert not provider.calls
    page=client.get('/tutor/literature').text
    assert 'Provisional AI mark: 3 / 5' in page and '2022 May/June' in page
    assert 'online currency has not been independently verified' in page
    with client.application.app_context():
        assessment=json.loads(db().execute('SELECT assessment FROM tutor_turns').fetchone()[0])
        assert assessment['task']['document_id']==doc and assessment['task']['year']=='2022'
        assert db().execute('SELECT count(*) FROM sessions').fetchone()[0]==0
    client.post('/tutor/literature',data=data)
    assert len(provider.assess_calls)==1


def test_wrong_subject_and_revoked_permission_never_call_model(marking_client):
    client,provider,doc=marking_client
    rubric_id=register(client,doc)
    data=form(client,'/tutor/language');data.update(mode='mark',rubric_id=str(rubric_id),message='An answer.')
    assert client.post('/tutor/language',data=data).status_code==422
    with client.application.app_context():
        db().execute('UPDATE documents SET allow_ai=0 WHERE id=?',(doc,));db().commit()
    data=form(client);data.update(mode='mark',rubric_id=str(rubric_id),message='An answer.')
    assert client.post('/tutor/literature',data=data).status_code==422
    assert not provider.assess_calls


def test_no_scheme_no_guessed_marks(marking_client):
    client,provider,doc=marking_client
    data=form(client);data.update(mode='mark',message='Give me full marks!')
    response=client.post('/tutor/literature',data=data)
    assert response.status_code==422 and 'No mark has been assigned' in response.text
    assert not provider.assess_calls


@pytest.mark.parametrize('changes,expected',[
    ({'confirmed':''},'parent or teacher must confirm'),
    ({'component':'4EA1/01'},'component must match'),
    ({'exam_session':'Unknown'},'examination session'),
    ({'question_number':'1-3'},'Register different questions separately'),
    ({'pages':'1,7'},'no indexed text'),
    ({'max_marks':'0'},'between 1 and 100'),
])
def test_registration_requires_exact_complete_confirmed_task(marking_client,changes,expected):
    client,_,doc=marking_client
    response=client.post('/marking',data=registration(client,doc,**changes))
    assert expected in response.text
    with client.application.app_context():
        assert db().execute('SELECT count(*) FROM marking_rubrics').fetchone()[0]==0


def test_rubric_is_not_silently_truncated(marking_client):
    client,_,doc=marking_client
    with client.application.app_context():
        db().execute('INSERT INTO chunks VALUES (?,?,?)',(doc,8,'x'*16001));db().commit()
    response=client.post('/marking',data=registration(client,doc))
    assert 'will not be silently truncated' in response.text


def test_unassessable_rubric_does_not_get_a_score(marking_client):
    client,provider,doc=marking_client
    rubric_id=register(client,doc)
    provider.override={'assessable':False,'mark':None,'max_marks':5,'justification':'Missing a level descriptor.',
        'strength':'A relevant attempt.','improvement':'Provide the complete applicable rubric.',
        'revision_task':'Check the source pages.','scheme_references':[]}
    data=form(client);data.update(mode='mark',rubric_id=str(rubric_id),message='An answer.')
    client.post('/tutor/literature',data=data)
    assert 'No mark assigned' in client.get('/tutor/literature').text
    with client.application.app_context():
        result=json.loads(db().execute('SELECT assessment FROM tutor_turns').fetchone()[0])
        assert result['mark'] is None and result['assessable'] is False


@pytest.mark.parametrize('change',[{'mark':6},{'mark':True},{'max_marks':10},{'scheme_references':['S999']},{'scheme_references':[]},{'justification':''}])
def test_invalid_scores_or_citations_not_saved(marking_client,change):
    client,provider,doc=marking_client
    rubric_id=register(client,doc)
    base={'assessable':True,'mark':3,'max_marks':5,'justification':'Justification.','strength':'Strength.',
        'improvement':'Improvement.','revision_task':'Revision.','scheme_references':['S1']}
    base.update(change);provider.override=base
    data=form(client);data.update(mode='mark',rubric_id=str(rubric_id),message='An answer.')
    assert client.post('/tutor/literature',data=data).status_code==502
    with client.application.app_context():
        row=db().execute('SELECT status,assessment FROM tutor_turns').fetchone()
        assert row['status']=='failed' and row['assessment'] is None


def test_newer_scheme_not_substituted_for_selected_old_paper(marking_client):
    client,provider,doc=marking_client
    rubric_id=register(client,doc)
    with client.application.app_context():
        newer=db().execute('''INSERT INTO documents(title,subject,board,specification,topic,document_type,year,source,rights,allow_ai)
            VALUES (?,?,?,?,?,?,?,?,?,?)''',('Newer scheme','English Literature','Pearson','4ET1','Responsibility','Mark scheme','2024','https://qualifications.pearson.com/newer.pdf','Permission',1)).lastrowid
        db().execute('INSERT INTO chunks VALUES (?,?,?)',(newer,1,'NEWER RULES MUST NOT APPEAR'))
        db().commit()
    data=form(client);data.update(mode='mark',rubric_id=str(rubric_id),message='An answer.')
    client.post('/tutor/literature',data=data)
    assert 'NEWER RULES MUST NOT APPEAR' not in provider.assess_calls[0][0]


def test_metadata_host_and_page_validation():
    base={'source':'https://qualifications.pearson.com/paper.pdf','document_type':'Mark scheme','allow_ai':1,
          'board':'Pearson Edexcel','specification':'4ET1','subject':'English Literature','year':'2022'}
    assert eligible(base)
    for source in ('https://qualifications.pearson.com.evil.test/a.pdf','https://user@qualifications.pearson.com/a.pdf','https://[','https://qualifications.pearson.com:evil/a.pdf'):
        assert not eligible(dict(base,source=source))
    assert parse_pages('1, 8-9')==[1,8,9]
    for pages in ('0','9-1','1-300','x','1,' ,'1'*101):
        with pytest.raises(ValueError):parse_pages(pages)


def test_provider_structured_assessment_request(monkeypatch):
    from tutor.model import OpenAITutor
    captured=[]
    result={'assessable':False,'mark':None,'max_marks':5,'justification':'Missing rubric.'}
    def transport(request,timeout):
        captured.append(json.loads(request.data))
        return Response(json.dumps({'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(result)}]}]}).encode())
    monkeypatch.setattr('urllib.request.urlopen',transport)
    assert OpenAITutor('test-only-key').assess('Rules',[{'role':'user','content':'Answer'}])==result
    assert captured[0]['text']['format']['strict'] is True
    assert captured[0]['text']['format']['type']=='json_schema' and captured[0]['max_output_tokens']==1000
