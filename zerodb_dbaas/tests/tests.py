import unittest
import pytest

from pyramid.testing import DummyRequest


@pytest.mark.usefixtures('testdb')
class ModelTests(unittest.TestCase):

    def test_add_something_1(self):
        from zerodb_dbaas.models import Counter
        db = self.testdb
        db.add(Counter(name='foo', count=0))
        self.assertEqual(len(db[Counter]), 1)

    def test_add_something_2(self):
        from zerodb_dbaas.models import Counter
        db = self.testdb
        db.add(Counter(name='foo', count=0))
        db.add(Counter(name='foo', count=0))
        self.assertEqual(len(db[Counter]), 2)

    def test_add_something_3(self):
        from zerodb_dbaas.models import Counter
        db = self.testdb
        db.add(Counter(name='foo', count=0))
        db.add(Counter(name='foo', count=0))
        db.add(Counter(name='foo', count=0))
        self.assertEqual(len(db[Counter]), 3)


@pytest.mark.usefixtures('testdb')
@pytest.mark.usefixtures('pyramid')
class ViewTests(unittest.TestCase):

    def test_my_view_1(self):
        from zerodb_dbaas.views import my_view
        from zerodb_dbaas.models import make_app
        request = DummyRequest(dbsession=make_app(self.testdb))
        info = my_view(request)
        self.assertEqual(info['project'], 'zerodb-dbaas')
        self.assertEqual(info['count'], 1)

    def test_my_view_2(self):
        from zerodb_dbaas.views import my_view
        from zerodb_dbaas.models import make_app
        request = DummyRequest(dbsession=make_app(self.testdb))
        info = my_view(request)
        self.assertEqual(info['project'], 'zerodb-dbaas')
        self.assertEqual(info['count'], 1)

    def test_add_user_html(self):
        from zerodb_dbaas.views import add_user
        request = DummyRequest(
            content_type='multipart/form-data',
            params=dict(username='wilma', passphrase='secret'),
            dbsession=self.testdb)
        info = add_user(request)
        self.assertEqual(info['ok'], 1, info)

    def _test_add_user_json(self):
        from zerodb_dbaas.views import add_user
        request = DummyRequest(
            content_type='application/json',
            json_body=dict(username='wilma', passphrase='secret'),
            dbsession=self.testdb)
        info = add_user(request)
        self.assertEqual(info['ok'], 1, info)

    def _test_del_user(self):
        from zerodb_dbaas.views import del_user
        request = DummyRequest(
            content_type='multipart/form-data',
            params=dict(username='wilma'),
            dbsession=self.testdb)
        info = del_user(request)
        self.assertEqual(info['ok'], 1, info)


@pytest.mark.usefixtures('testapp')
class FunctionalTests(unittest.TestCase):

    def test_home(self):
        res = self.testapp.get('/', status=200)
        self.assertEqual(res.content_type, 'text/html')
        self.assertTrue(b'zerodb-dbaas' in res.body)

    def test_count_json_1(self):
        res = self.testapp.post_json('/count.json', {}, status=200)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json.get('project'), 'zerodb-dbaas')
        self.assertEqual(res.json.get('count'), 1)

    def test_count_json_2(self):
        res = self.testapp.post_json('/count.json', {}, status=200)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(res.json.get('project'), 'zerodb-dbaas')
        self.assertEqual(res.json.get('count'), 2)
