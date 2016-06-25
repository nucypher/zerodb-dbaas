import pytest

from pyramid.exceptions import ConfigurationError
from zerodb.testing import TEST_PASSPHRASE


def test_parse_socket():
    from zerodb_dbaas import parse_socket
    assert parse_socket('localhost:8001') == ('localhost', 8001)
    assert parse_socket('zerodb.com:8001') == ('zerodb.com', 8001)
    assert parse_socket('/foo/bar/baz') == '/foo/bar/baz'
    assert parse_socket('') == None
    assert parse_socket(None) == None
    assert parse_socket('zerodb.com') == None
    assert parse_socket('8001') == None
    assert parse_socket('foo:bar:8001') == ('foo:bar', 8001)
    assert parse_socket(':8001') == ('', 8001)
    assert parse_socket('bar/baz') == None


def test_no_config(pyramid):
    from zerodb_dbaas import make_db
    with pytest.raises(ConfigurationError):
        make_db(pyramid)


def test_test_config(pyramid):
    from zerodb_dbaas import make_db
    testdb = object()
    pyramid.registry.settings.update({'testdb': testdb})
    db = make_db(pyramid)
    assert db is testdb


def test_bad_config(pyramid):
    from zerodb_dbaas import make_db
    pyramid.registry.settings.update({'zerodb.sock': ''})
    with pytest.raises(ConfigurationError):
        make_db(pyramid)
    pyramid.registry.settings.update({'zerodb.sock': 'zerodb.com'})
    with pytest.raises(ConfigurationError):
        make_db(pyramid)
    pyramid.registry.settings.update({'zerodb.sock': 'localhost:8001'})
    with pytest.raises(ConfigurationError):
        make_db(pyramid)
    pyramid.registry.settings.update({'zerodb.username': 'fred'})
    with pytest.raises(ConfigurationError):
        make_db(pyramid)


def test_good_config(pyramid, zeo_server):
    from zerodb_dbaas import make_db
    settings = {
        'zerodb.sock': zeo_server,
        'zerodb.username': 'root',
        'zerodb.password': TEST_PASSPHRASE
    }
    pyramid.registry.settings.update(settings)
    db = make_db(pyramid)
    assert db._root is not None
