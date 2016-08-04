import mock
import re
import six
import time


def decode(s):
    return s.decode('utf-8') if six.PY3 else s


def test_register_page(testapp):
    response = testapp.get('/register')
    assert response.status_code == 200
    assert response.content_type == 'text/html'
    assert b'Email' in response.body


def test_register_happy_path(testapp):
    form = dict(
        inputEmail='fred@bedrock.com',
        inputPassword='hash::' + '1a' * 64,
        inputPasswordConfirmation='hash::' + '1a' * 64,
    )

    # Submit the registration form
    m = mock.Mock()
    with mock.patch('requests.post', side_effect=m):
        response = testapp.post('/register', form)
    assert response.status_code == 302
    assert response.content_type == 'text/plain'

    time.sleep(0.2)
    args, kw = m.call_args
    assert args[0].startswith('http')
    assert 'auth' in kw
    assert 'data' in kw

    # Perform redirect to the email page
    response = testapp.get(response.location)
    assert response.status_code == 200
    assert response.content_type == 'text/html'
    assert b'Registration submitted' in response.body, response.body

    # Follow link to the confirmation page
    match = re.search(br'<a href="(.*)"', response.body)
    assert match, response.body
    response = testapp.get(decode(match.group(1)))
    assert response.status_code == 302
    assert response.content_type == 'text/plain'

    # Perform redirect to the success page
    response = testapp.get(response.location)
    assert response.status_code == 200
    assert response.content_type == 'text/html'
    assert b'Registration Complete' in response.body, response.body


def test_register_happy_path_json(testapp):
    # Call _register API
    form = dict(
        inputEmail='barney@bedrock.com',
        inputPassword='hash::' + '1a' * 64,
        inputPasswordConfirmation='hash::' + '1a' * 64,
    )

    m = mock.Mock()
    with mock.patch('requests.post', side_effect=m):
        response = testapp.post_json('/_register', form)

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json_body.get('ok') == 1, response.json_body
    assert response.json_body.get('hashcode')

    # Call _register_confirm API
    form = dict(
        hashcode=response.json_body.get('hashcode'),
    )
    response = testapp.post_json('/_register_confirm', form)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json_body.get('ok') == 1, response.json_body

    # Account is no longer available
    form = dict(
        inputEmail='barney@bedrock.com',
    )
    response = testapp.post_json('/_account_available', form)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json_body.get('ok') == 0, response.json_body


def test_account_available(testapp):
    form = dict(
        inputEmail='wilma@bedrock.com',
    )
    response = testapp.post_json('/_account_available', form)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json_body.get('ok') == 1, response.json_body
