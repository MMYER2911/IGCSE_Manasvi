import pytest
from tutor import create_app


@pytest.fixture
def protected(tmp_path):
    app = create_app({'TESTING':True,'DATABASE':str(tmp_path/'protected.sqlite'),
        'HOSTED':True,'SESSION_COOKIE_SECURE':True,'ACCESS_PASSWORD':'test-only-example-passphrase'})
    return app.test_client()


def csrf(client):
    client.get('/login', base_url='https://localhost')
    with client.session_transaction() as s:
        return s['csrf']


def test_all_private_workflows_require_login(protected):
    for path in ('/','/resources','/practice','/poetry','/study/literature','/attempt/unknown'):
        response = protected.get(path,base_url='https://localhost')
        assert response.status_code == 302 and response.location.endswith('/login')
    assert protected.get('/health').json == {'status':'ok'}
    assert 'Set-Cookie' not in protected.get('/health').headers
    assert protected.get('/static/style.css').status_code == 200


def test_login_logout_csrf_and_cookie(protected):
    assert protected.post('/login',data={'password':'test-only-example-passphrase'}).status_code == 400
    token = csrf(protected)
    wrong = protected.post('/login',data={'csrf':token,'password':'wrong'},base_url='https://localhost')
    assert 'Incorrect passphrase' in wrong.text
    assert protected.get('/resources').status_code == 302
    response = protected.post('/login',data={'csrf':token,'password':'test-only-example-passphrase'},base_url='https://localhost')
    assert response.status_code == 302 and response.location=='/'
    cookie = response.headers['Set-Cookie']
    assert 'Secure' in cookie and 'HttpOnly' in cookie and 'SameSite=Lax' in cookie
    with protected.session_transaction() as s:
        assert s['csrf'] != token
        token = s['csrf']
    assert 'Your subjects.' in protected.get('/',base_url='https://localhost').text
    assert protected.get('/logout').status_code == 405
    protected.post('/logout',data={'csrf':token},base_url='https://localhost')
    assert protected.get('/resources').status_code == 302


def test_login_rate_limit(protected):
    token = csrf(protected)
    for _ in range(5):
        assert protected.post('/login',data={'csrf':token,'password':'wrong'},base_url='https://localhost').status_code == 200
    assert protected.post('/login',data={'csrf':token,'password':'wrong'},base_url='https://localhost').status_code == 429


def test_render_requires_private_password(monkeypatch):
    monkeypatch.setenv('RENDER','true')
    monkeypatch.delenv('TUTOR_PASSWORD',raising=False)
    with pytest.raises(RuntimeError,match='TUTOR_PASSWORD'):
        create_app()
    monkeypatch.setenv('TUTOR_PASSWORD','short')
    with pytest.raises(RuntimeError,match='16 characters'):
        create_app()


def test_configured_data_directory(monkeypatch,tmp_path):
    monkeypatch.delenv('RENDER',raising=False)
    monkeypatch.delenv('TUTOR_PASSWORD',raising=False)
    monkeypatch.setenv('TUTOR_DATA_DIR',str(tmp_path/'data'))
    app = create_app({'TESTING':True})
    assert app.instance_path == str(tmp_path/'data')
    assert (tmp_path/'data'/'tutor.sqlite').exists()
    assert (tmp_path/'data'/'session.key').exists()
