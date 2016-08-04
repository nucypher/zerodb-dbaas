import pytest
import transaction

# Explicit import from testing makes fixtures out of them
from zerodb.testing import (
        db, admin_db, zeo_server, tempdir)


@pytest.fixture(scope="function")
def testdb(request, db):
    if request.instance is not None:
        request.instance.testdb = db
    request.addfinalizer(transaction.abort)
    return db


@pytest.fixture(scope="function")
def pyramid(request):
    from pyramid.testing import setUp, tearDown
    config = setUp()
    if request.instance is not None:
        request.instance.pyramid = config
    request.addfinalizer(tearDown)
    return config


@pytest.fixture(scope="function")
def testapp(request, db, admin_db):
    from zerodb_dbaas import main
    app = main({}, **{
            'website.secret': '736e743c1b837c2ec8e3c715a5666f35e8c5e0ee55d35df0582d9002cc55a6f9',
            'mailgun.key': 'dummykey',
            'mailgun.url': 'https://mail.gun',
            'testdb': db,
            'admin_db': admin_db})
    from webtest import TestApp
    app = TestApp(app)
    if request.instance is not None:
        request.instance.testapp = app
    request.addfinalizer(transaction.abort)
    return app
