from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from zerodb_dbaas.views.common import humansize
from zerodb_dbaas.models import UserRegistration
import zerodb.permissions.base
import stripe

from .common import decode_password_hex, nohashing


def manage_databases(request):
    db_users = []
    email = request.authenticated_userid

    with request.admin_db.transaction() as conn:
        admin = conn.root()['admin']
        db_users_it = iter(admin.users_by_name.keys(email))
        while True:
            next_email = next(db_users_it)
            if next_email.startswith(email):
                db_users.append(next_email)
            else:
                break

    db_ids = [i[len(email):].strip('-') for i in db_users]
    next_db_id = max([int(i) for i in db_ids if i.isnumeric()] + [0]) + 1
    next_db_id = '{0}-{1}'.format(email, next_db_id)

    return {'db_users': db_users, 'next_db_id': next_db_id}


@view_config(
        route_name='home',
        renderer='zerodb_dbaas:templates/index-unregistered.pt',
        effective_principals=[])
@view_config(
        route_name='home',
        renderer='zerodb_dbaas:templates/index.pt',
        effective_principals=['group:customers'])
def home(request):
    """Home page"""
    if request.authenticated_userid:
        return manage_databases(request)
    else:
        return {}


@view_config(
        route_name='instance',
        renderer='zerodb_dbaas:templates/instance.pt',
        effective_principals=['group:customers'])
def instance(request):
    username = request.matchdict['name']

    with request.admin_db.transaction() as conn:
        admin = conn.root()['admin']
        if username not in admin.users_by_name:
            raise HTTPNotFound('No such username: %s' % username)

        size = 0
        if hasattr(admin, 'user_stats'):
            if username in admin.user_stats:
                size = admin.user_stats[username]

    return {'username': username, 'size': humansize(size)}


@view_config(route_name='add_subdb', renderer='json',
             effective_principals=['group:customers'])
def add_subdb(request):
    db = request.dbsession
    form = request.params

    email = request.authenticated_userid
    username = form.get('next_db_id')

    if not username.startswith(email + '-') and not (username == email):
        return {'ok': 0}

    password = form.get('password')
    password_hash = decode_password_hex(password)
    # Also need some stripe things

    user = db[UserRegistration].query(email=email)[0]
    user.unconfirmed_db = (username, password_hash)

    return {'ok': 1}


@view_config(route_name='confirm_subdb', renderer='json',
             effective_principals=['group:customers'])
def confirm_subdb(request):
    db = request.dbsession
    admin_db = request.admin_db

    email = request.authenticated_userid
    user = db[UserRegistration].query(email=email)[0]
    # XXX call stripe and if it is all good...
    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here https://dashboard.stripe.com/account/apikeys
    stripe.api_key = "sk_test_qiEtoPFg1UktBLSSBNHxCc38"

    # Get the credit card details submitted by the form
    token = request.POST['stripeToken']

    # Create a Customer
    customer = stripe.Customer.create(
      source=token,
      plan="large",
      email=email
    )

    username, password_hash = user.unconfirmed_db

    with admin_db.transaction() as conn:
        admin = zerodb.permissions.base.get_admin(conn)
        admin.add_user(username, password=password_hash, security=nohashing)

    user.unconfirmed_db = None

    return {'ok': 1}


@view_config(route_name='remove_subdb', renderer='json')
def remove_subdb(request):
    admin_db = request.admin_db
    username = request.matchdict['name']

    with admin_db.transaction() as conn:
        admin = zerodb.permissions.base.get_admin(conn)
        admin.del_user(username)

    return {'ok': 1}
