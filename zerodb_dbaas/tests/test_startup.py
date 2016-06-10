import pytest

from pyramid.exceptions import ConfigurationError
from zerodb.testing import TEST_PASSPHRASE


def test_parse_socket():
    from zerodb_dbaas import parse_socket
    assert parse_socket('localhost:8001') == ('localhost', 8001)
    assert parse_socket('zerodb.com:8001') == ('zerodb.com', 8001)
    assert parse_socket('/foo/bar/baz') == '/foo/bar/baz'
    assert parse_socket('') == ''
    assert parse_socket(None) == None
    assert parse_socket('foo:bar:8001') == ('foo:bar', 8001)
    assert parse_socket(':8001') == ('', 8001)

    with pytest.raises(ConfigurationError):
        parse_socket('zerodb.com')
    with pytest.raises(ConfigurationError):
        parse_socket('8001')


def test_noconfig(pyramid):
    from zerodb_dbaas import make_db
    with pytest.raises(ConfigurationError):
        make_db(pyramid)


def test_testconfig(pyramid):
    from zerodb_dbaas import make_db
    testdb = object()
    pyramid.registry.settings.update({'testdb': testdb})
    db = make_db(pyramid)
    assert db is testdb


def test_appconfig(pyramid, zeo_server):
    from zerodb_dbaas import make_db
    settings = {
        'zerodb.sock': zeo_server,
        'zerodb.username': 'root',
        'zerodb.password': TEST_PASSPHRASE
    }
    pyramid.registry.settings.update(settings)
    db = make_db(pyramid)
    assert db._root is not None
