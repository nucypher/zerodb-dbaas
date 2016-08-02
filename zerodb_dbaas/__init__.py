import ZEO
import ZEO.tests.testssl

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationError
# from pyramid.settings import asbool

import zerodb.db
from zerodb import DB
from .models import make_app

default_settings = []
#    ('example_bool_setting', asbool, false),
# ]


def parse_settings(settings):
    parsed = {}
    for name, convert, default in default_settings:
        value = settings.get(name, default)
        if convert is not None:
            value = convert(value)
        parsed[name] = value
    return parsed


def parse_socket(sock):
    if not sock:
        return None
    if sock[0] == '/':
        return str(sock)
    if ':' not in sock:
        return None
    sock = sock.rsplit(':', 1)
    sock = (str(sock[0]), int(sock[1], 10))
    return sock


def make_db(config):
    zodb_dbs = getattr(config.registry, '_zodb_databases', None)
    if zodb_dbs is None:
        zodb_dbs = config.registry._zodb_databases = {}

    sock = config.registry.settings.get('zerodb.sock')
    username = config.registry.settings.get('zerodb.username')
    password = config.registry.settings.get('zerodb.password')
    server_cert = config.registry.settings.get('zerodb.server_cert')

    # Test certs
    # Maybe there is a better way?
    if server_cert == 'test_server_cert':
        server_cert = ZEO.tests.testssl.server_cert

    if sock is None:
        db = config.registry.settings.get('testdb')  # Testing
        if db is None:
            raise ConfigurationError('No zerodb.sock defined in Pyramid settings')
    else:
        sock = parse_socket(sock)
        if sock is None:
            raise ConfigurationError('Invalid zerodb.sock format in Pyramid settings')
        if username is None:
            raise ConfigurationError('No zerodb.username defined in Pyramid settings')
        if password is None:
            raise ConfigurationError('No zerodb.password defined in Pyramid settings')

        # Better to use client cert for the admin account?
        db = DB(sock, username=username, password=password,
                server_cert=server_cert)
        admin_db = ZEO.DB(
                sock,
                ssl=zerodb.db.make_ssl(server_cert=server_cert),
                credentials=dict(name=username, password=password),
                wait_timeout=10000)

    zodb_dbs[''] = db
    zodb_dbs['admin'] = admin_db

    return db


def get_connection(request, dbname=None):
    # Cribbed from pyramid_zodbconn
    primary_conn = getattr(request, '_primary_zodb_conn', None)
    if primary_conn is None:
        zodb_dbs = getattr(request.registry, '_zodb_databases', None)
        if zodb_dbs is None:
            raise ConfigurationError('No zerodb database configured')
        primary_db = zodb_dbs.get('')
        if primary_db is None:
            raise ConfigurationError('Error connecting to zerodb database')
        primary_conn = primary_db
        request._primary_zodb_conn = primary_conn
    return primary_conn


def session_factory(request):
    db = get_connection(request)
    return make_app(db)


def get_admin_db(request):
    zodb_dbs = getattr(request.registry, '_zodb_databases', None)
    if zodb_dbs is None:
        raise ConfigurationError('No zerodb database configured')
    admin_db = zodb_dbs.get('admin')
    return admin_db


def main(global_config, **settings):
    config = Configurator(settings=settings)

    # Parse config file settings
    settings = config.registry.settings
    settings.update(parse_settings(settings))

    config.include('pyramid_chameleon')
    config.include('pyramid_tm')

    # Authentication with single security group
    # http://docs.pylonsproject.org/projects/pyramid/en/latest/quick_tutorial/authentication.html
    authn_policy = AuthTktAuthenticationPolicy(
        settings['website.secret'],
        callback=lambda user: ['group:customers'],
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_request_method(session_factory, 'dbsession', reify=True)
    config.add_request_method(get_admin_db, 'admin_db', reify=True)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('count', '/count')
    config.add_route('count_json', '/count.json')

    config.add_route('_add_user', '/_add_user')
    config.add_route('_del_user', '/_del_user')
    config.add_route('_edit_user', '/_edit_user')

    config.add_static_view('assets', 'assets', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.add_route('register-email', '/register-email')
    config.add_route('register-confirm', '/register-confirm')
    config.add_route('register-success', '/register-success')

    config.add_route('_register', '/_register')
    config.add_route('_register_confirm', '/_register_confirm')
    config.add_route('_account_available', '/_account_available')

    config.add_route('registrations', '/registrations')

    config.scan(ignore='zerodb_dbaas.tests')
    config.commit()

    # Connect on startup
    make_db(config)

    return config.make_wsgi_app()
