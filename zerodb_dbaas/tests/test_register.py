import pytest
import re
import six

def decode(s):
    return s.decode('utf-8') if six.PY3 else s


def test_register_page(testapp):
    response = testapp.get('/register')
    assert response.status_code == 200
    assert response.content_type == 'text/html'
    assert b'Account Name' in response.body


def test_register_happy_path(testapp):
    form = dict(
        inputAccount='fred',
        inputEmail='fred@bedrock.com',
        inputPassword='secret',
        inputPasswordConfirmation='secret',
    )

    # Submit the registration form
    response = testapp.post('/register', form)
    assert response.status_code == 302
    assert response.content_type == 'text/plain'

    # Perform redirect to the email page
    response = testapp.get(response.location)
    assert response.status_code == 200
    assert response.content_type == 'text/html'
    assert b'Confirmation Email' in response.body, response.body

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
        inputAccount='barney',
        inputEmail='barney@bedrock.com',
        inputPassword='secret',
        inputPasswordConfirmation='secret',
    )
    response = testapp.post_json('/_register', form)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json_body.get('ok', 0) == 1, response.json_body
    assert response.json_body.get('hashcode')

    # Call _register_confirm API
    form = dict(
        hashcode=response.json_body.get('hashcode'),
    )
    response = testapp.post_json('/_register_confirm', form)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json_body.get('ok', 0) == 1, response.json_body
