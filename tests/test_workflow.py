import io
import re
import time
import pytest
from tutor import create_app
from tutor.storage import db


@pytest.fixture
def client(tmp_path):
    app = create_app({'TESTING':True,'DATABASE':str(tmp_path / 'test.sqlite')})
    return app.test_client()


def token(client):
    client.get('/')
    with client.session_transaction() as s:
        return s['csrf']


def start(client):
    return client.post('/practice',data={'csrf':token(client),'subject':'Mathematics','topic':'Algebra','difficulty':'Foundation','duration':'5'}).location


def test_upload_search_and_citations(client):
    data = dict(csrf=token(client), title='Algebra notes', subject='Mathematics', board='Cambridge', specification='0580', topic='Algebra', document_type='School notes', year='2026', source='Teacher', rights='Permission granted', authorised='yes', file=(io.BytesIO(b'Expand brackets by multiplication.'),'notes.txt'))
    assert client.post('/resources',data=data).status_code == 302
    page = client.get('/resources?q=brackets').text
    assert 'Expand brackets by multiplication.' in page
    assert 'Algebra notes' in page and 'page 1' in page and 'Teacher' in page
    assert client.get('/resources?q=%22%20OR%20*').status_code == 200


def test_permissions_and_bad_file(client):
    assert client.post('/resources',data={'csrf':token(client)}).status_code == 200
    with client.application.app_context():
        assert db().execute('SELECT count(*) FROM documents').fetchone()[0] == 0
    assert client.post('/practice',data={}).status_code == 400


def test_practice_marks_persists_and_hides_answers(client):
    path = start(client)
    page = client.get(path).text
    assert 'Model answer:' not in page
    sid = path.split('/')[-1]
    with client.application.app_context():
        qs = db().execute("SELECT id,answer FROM questions WHERE topic='Algebra' AND difficulty='Foundation'").fetchall()
    data = {str(q['id']):q['answer'] for q in qs}
    data['csrf'] = token(client)
    assert client.post(path,data=data).status_code == 302
    assert 'Model answer:' in client.get(path).text
    with client.application.app_context():
        row = db().execute('SELECT * FROM sessions WHERE id=?',(sid,)).fetchone()
        assert row['score'] == row['total'] == 2
    client.post(path,data={'csrf':token(client)})
    assert '2 / 2' in client.get('/').text
    # New app/client uses the same persisted database.
    other = create_app({'TESTING':True,'DATABASE':client.application.config['DATABASE']}).test_client()
    assert '2 / 2' in other.get('/').text


def test_expiry_enforced_on_server(client):
    path = start(client)
    with client.application.app_context():
        db().execute('UPDATE sessions SET started=?',(time.time()-400,))
        db().commit()
    client.post(path,data={'csrf':token(client),'1':'5','2':'2x + 6'})
    with client.application.app_context():
        assert db().execute('SELECT score FROM sessions').fetchone()[0] == 0


def test_numeric_invalid_and_tolerance():
    from tutor.questions import mark
    q = {'kind':'numerical','answer':'28.27','tolerance':0.005,'marks':1}
    assert mark(q,'28.274') == 1
    for answer in ['NaN','Infinity','text','28.28']:
        assert mark(q,answer) == 0


def test_pdf_extraction_and_rejection():
    from tutor.resources import extract
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
    writer = PdfWriter()
    page = writer.add_blank_page(300, 300)
    font = DictionaryObject({NameObject('/Type'):NameObject('/Font'), NameObject('/Subtype'):NameObject('/Type1'), NameObject('/BaseFont'):NameObject('/Helvetica')})
    page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
    stream = DecodedStreamObject()
    stream.set_data(b'BT /F1 12 Tf 20 100 Td (Algebra revision) Tj ET')
    page[NameObject('/Contents')] = writer._add_object(stream)
    output = io.BytesIO()
    writer.write(output)
    pdf = output.getvalue()
    assert 'Algebra revision' in extract('notes.pdf',pdf)[0][1]
    with pytest.raises(ValueError):
        extract('empty.txt',b' ')
    with pytest.raises(ValueError):
        extract('bad.exe',b'bad')


def test_translated_pdf_spreads_keep_correct_page_citations():
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
    from tutor.resources import extract
    writer=PdfWriter()
    font=writer._add_object(DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')}))
    for shift in (0,-600):
        page=writer.add_blank_page(600,800)
        page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):font})})
        stream=DecodedStreamObject()
        stream.set_data(f'q 1 0 0 1 {shift} 0 cm BT /F1 12 Tf 40 600 Td (LEFT PAGE) Tj ET BT /F1 12 Tf 640 600 Td (RIGHT PAGE) Tj ET Q'.encode())
        page[NameObject('/Contents')]=writer._add_object(stream)
    output=io.BytesIO();writer.write(output)
    chunks=extract('spread.pdf',output.getvalue())
    first=''.join(text for page,text in chunks if page==1)
    second=''.join(text for page,text in chunks if page==2)
    assert 'LEFT PAGE' in first and 'RIGHT PAGE' not in first
    assert 'RIGHT PAGE' in second and 'LEFT PAGE' not in second
