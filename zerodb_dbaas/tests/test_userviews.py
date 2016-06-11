from pyramid.testing import DummyRequest


def test_add_user_html(pyramid, testdb):
    from zerodb_dbaas.views import add_user
    request = DummyRequest(
        content_type='multipart/form-data',
        params=dict(username='wilma', passphrase='secret'),
        dbsession=testdb)
    info = add_user(request)
    assert info['ok'] == 1, info


def test_change_key_html(pyramid, testdb):
    from zerodb_dbaas.views import edit_user
    request = DummyRequest(
        content_type='multipart/form-data',
        params=dict(username='wilma', passphrase='more secret'),
        dbsession=testdb)
    info = edit_user(request)
    assert info['ok'] == 1, info


def test_del_user_html(pyramid, testdb):
    from zerodb_dbaas.views import del_user
    request = DummyRequest(
        content_type='multipart/form-data',
        params=dict(username='wilma'),
        dbsession=testdb)
    info = del_user(request)
    assert info['ok'] == 1, info


def test_add_user_json(pyramid, testdb):
    from zerodb_dbaas.views import add_user
    request = DummyRequest(
        content_type='application/json',
        json_body=dict(username='betty', passphrase='secret'),
        dbsession=testdb)
    info = add_user(request)
    assert info['ok'] == 1, info


def test_change_key_json(pyramid, testdb):
    from zerodb_dbaas.views import edit_user
    request = DummyRequest(
        content_type='application/json',
        json_body=dict(username='betty', passphrase='more secret'),
        dbsession=testdb)
    info = edit_user(request)
    assert info['ok'] == 1, info


def test_del_user_json(pyramid, testdb):
    from zerodb_dbaas.views import del_user
    request = DummyRequest(
        content_type='application/json',
        json_body=dict(username='betty',),
        dbsession=testdb)
    info = del_user(request)
    assert info['ok'] == 1, info
