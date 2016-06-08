import pytest
import transaction

from zerodb.testing import *


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
def testapp(request, db):
    from zerodb_dbaas import main
    app = main({}, testdb=db)
    from webtest import TestApp
    app = TestApp(app)
    if request.instance is not None:
        request.instance.testapp = app
    request.addfinalizer(transaction.abort)
    return app
