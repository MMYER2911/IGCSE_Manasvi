import io
import json
import time
from tutor import create_app
from tutor.english import POEMS, FRAMEWORK
from tutor.storage import db
from test_workflow import client, token


def begin(client, subject='English Literature', topic='An Inspector Calls', difficulty=''):
    response = client.post('/practice', data={'csrf':token(client), 'subject':subject,
        'topic':topic, 'difficulty':difficulty, 'duration':'20'})
    assert response.status_code == 302
    return response.location


def test_subject_studios_and_seed(client):
    assert 'English Literature' in client.get('/').text
    assert '4ET1' in client.get('/study/literature').text
    assert '4EA1' in client.get('/study/language').text
    assert client.get('/study/unknown').status_code == 404
    with client.application.app_context():
        counts = dict(db().execute('SELECT subject,count(*) FROM questions GROUP BY subject'))
        assert counts == {'English Literature':15,'English Language':6,'Mathematics':7}
    page = client.get('/practice?subject=English%20Language').text
    assert 'Audience and purpose' in page and 'Macbeth' not in page


def test_mixed_session_excludes_essay_from_automatic_marks(client):
    path = begin(client)
    with client.application.app_context():
        questions = db().execute("SELECT * FROM questions WHERE topic='An Inspector Calls'").fetchall()
    data = {'csrf':token(client)}
    for q in questions:
        data[str(q['id'])] = q['answer'] if q['kind']=='multiple_choice' else 'My interpretation needs supporting evidence.'
    before = client.get(path).text
    assert 'Review checklist:' not in before
    client.post(path,data=data)
    page = client.get(path).text
    assert 'Awaiting human review' in page and 'Review checklist:' in page
    assert 'ENGLISH LITERATURE' in page and 'MATHEMATICS' not in page
    with client.application.app_context():
        row = db().execute('SELECT * FROM sessions').fetchone()
        assert (row['score'],row['total']) == (1,1)
        essay = db().execute("SELECT * FROM responses WHERE status='awaiting_review'").fetchone()
        assert essay['score'] is None and essay['answer'] == 'My interpretation needs supporting evidence.'
    assert '1 awaiting review' in client.get('/').text
    client.post(path,data={'csrf':token(client)})
    with client.application.app_context():
        assert db().execute('SELECT count(*) FROM responses').fetchone()[0] == 2


def test_essay_only_and_late_work(client):
    path = begin(client, topic='Poem at Thirty-Nine')
    with client.application.app_context():
        qid = db().execute("SELECT id FROM questions WHERE topic='Poem at Thirty-Nine'").fetchone()[0]
        db().execute('UPDATE sessions SET started=?',(time.time()-1300,))
        db().commit()
    client.post(path, data={'csrf':token(client), str(qid):'An interpretation to review.'})
    page = client.get(path).text
    assert 'No automatic score' in page and '0 / 0' not in page and 'late work' in page
    with client.application.app_context():
        row = db().execute('SELECT * FROM responses').fetchone()
        assert row['score'] is None and row['status']=='awaiting_review'
    assert 'No auto-marked items' in client.get('/').text


def test_notebooks_persist_all_categories_and_escape(client):
    data = {'csrf':token(client),'poem':POEMS[0]}
    data.update({key:f'{label} <script>alert(1)</script>' for key,label in FRAMEWORK})
    assert client.post('/poetry',data=data).status_code == 302
    page = client.get('/poetry',query_string={'poem':POEMS[0]}).text
    assert '&lt;script&gt;' in page and '<script>alert(1)</script>' not in page
    other = create_app({'TESTING':True, 'DATABASE':client.application.config['DATABASE']}).test_client()
    page = other.get('/poetry',query_string={'poem':POEMS[0]}).text
    for key,label in FRAMEWORK:
        assert label in page
    page = other.get('/poetry',query_string={'poem':POEMS[1]}).text
    assert '&lt;script&gt;' not in page
    assert client.post('/poetry',data={'poem':POEMS[0]}).status_code == 400
    assert client.get('/poetry?poem=Unknown').status_code == 404


def test_notebook_overwrite_and_limits(client):
    data = {'csrf':token(client),'poem':POEMS[0],'meaning':'First idea'}
    client.post('/poetry',data=data)
    data['meaning']='Revised idea'
    client.post('/poetry',data=data)
    with client.application.app_context():
        assert db().execute('SELECT count(*) FROM poetry_notes').fetchone()[0] == 1
        assert json.loads(db().execute('SELECT notes FROM poetry_notes').fetchone()[0])['meaning']=='Revised idea'
    data['meaning']='x'*8001
    assert client.post('/poetry',data=data).status_code == 400


def test_subject_filtered_retrieval(client):
    for subject,title in [('English Literature','Literature notes'),('Mathematics','Maths notes')]:
        data = dict(csrf=token(client),title=title,subject=subject,board='School',specification='N/A',topic='Revision',document_type='School notes',year='2026',source='Teacher',rights='Permission',authorised='yes',file=(io.BytesIO(b'Revision evidence.'),'notes.txt'))
        assert client.post('/resources',data=data).status_code == 302
    page = client.get('/resources',query_string={'q':'evidence','subject':'English Literature'}).text
    assert 'Literature notes' in page and 'Maths notes' not in page and 'page 1' in page
    assert 'Maths notes' in client.get('/resources?q=evidence').text


def test_existing_database_upgrade_and_idempotence(client):
    # Reproduce the old schema and an existing mathematics result before reopening.
    with client.application.app_context():
        db().execute("DELETE FROM questions WHERE subject!='Mathematics'")
        db().execute('ALTER TABLE responses DROP COLUMN status')
        db().execute('ALTER TABLE sessions DROP COLUMN expired')
        db().execute("INSERT INTO sessions VALUES ('legacy',1,300,'[1]',2,1,1,1)")
        db().execute("INSERT INTO responses VALUES ('legacy',1,'5',1)")
        db().commit()
    for _ in range(2):
        app = create_app({'TESTING':True,'DATABASE':client.application.config['DATABASE']})
        with app.app_context():
            assert db().execute('SELECT count(*) FROM questions').fetchone()[0] == 28
            assert db().execute("SELECT status FROM responses WHERE session_id='legacy'").fetchone()[0]=='automatic'
            assert db().execute("SELECT score FROM sessions WHERE id='legacy'").fetchone()[0]==1
    assert app.test_client().get('/attempt/legacy').status_code == 200


def test_answer_limit_does_not_submit(client):
    path = begin(client)
    with client.application.app_context():
        qid = db().execute("SELECT id FROM questions WHERE topic='An Inspector Calls' AND kind='essay'").fetchone()[0]
    assert client.post(path,data={'csrf':token(client),str(qid):'x'*10001}).status_code == 400
    with client.application.app_context():
        assert db().execute('SELECT submitted FROM sessions').fetchone()[0] is None
