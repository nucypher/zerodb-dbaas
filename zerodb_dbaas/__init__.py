from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationError

from zerodb import DB
from .models import make_app


def make_db(config):
    zodb_dbs = getattr(config.registry, '_zodb_databases', None)
    if zodb_dbs is None:
        zodb_dbs = config.registry._zodb_databases = {}

    db = config.registry.settings.get('testdb', None)
    if db is None:
        # TODO: Read config settings
        db = DB(('localhost', 8001), username='root', password='123')

    zodb_dbs[''] = db
    return db


def get_connection(request, dbname=None):
    # Cribbed from pyramid_zodbconn
    primary_conn = getattr(request, '_primary_zodb_conn', None)
    if primary_conn is None:
        zodb_dbs = getattr(request.registry, '_zodb_databases', None)
        if zodb_dbs is None:
            raise ConfigurationError('pyramid_zodbconn not included in configuration')
        primary_db = zodb_dbs.get('')
        if primary_db is None:
            raise ConfigurationError('No zodbconn.uri defined in Pyramid settings')
        primary_conn = primary_db
        request._primary_zodb_conn = primary_conn
    if dbname is None:
        return primary_conn
    try:
        conn = primary_conn.get_connection(dbname)
    except KeyError:
        raise ConfigurationError('No zodbconn.uri.%s defined in Pyramid settings' % dbname)
    return conn


def session_factory(request):
    db = get_connection(request)
    return make_app(db)


def main(global_config, **settings):
    config = Configurator(settings=settings)

    config.include('pyramid_chameleon')
    config.include('pyramid_tm')

    config.add_request_method(session_factory, 'dbsession', reify=True)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('count_json', '/count.json')

    config.add_route('_add_user', '/_add_user')
    config.add_route('_del_user', '/_del_user')
    config.add_route('_edit_user', '/_edit_user')

    config.scan()
    config.commit()

    # Connect on startup
    make_db(config)

    return config.make_wsgi_app()
