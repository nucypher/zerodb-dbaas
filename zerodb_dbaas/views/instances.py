from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from zerodb_dbaas.views.common import humansize
from zerodb_dbaas.models import UserRegistration
from BTrees.OOBTree import OOBTree
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

    return {'db_users': db_users,
            'next_db_id': next_db_id,
            'stripe_pk': request.registry.settings['stripe.stripe_pk']}


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
    email = request.authenticated_userid
    db = request.dbsession
    user = db[UserRegistration].query(email=email)[0]

    if (username != email) and (not username.startswith(email + '-')):
        raise HTTPNotFound('No such username: %s' % username)

    with request.admin_db.transaction() as conn:
        admin = conn.root()['admin']
        if username not in admin.users_by_name:
            raise HTTPNotFound('No such username: %s' % username)

        size = 0
        if hasattr(admin, 'user_stats'):
            if username in admin.user_stats:
                size = admin.user_stats[username]


        size_dict = {'small': 2, 'medium': 4, 'large': 8}
        max_size = 2
        bill = 0
        if hasattr(user, "subscriptions") and (username in user.subscriptions):
            subscription_id = user.subscriptions[username]
            stripe.api_key = request.registry.settings['stripe.api_key']
            subscription = stripe.Subscription.retrieve(subscription_id)
            max_size = size_dict[subscription.plan.name]
            bill = subscription.plan.amount / 100


    return {'username': username, 'size': humansize(size), 'bill': bill, 'maxSize': max_size}


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
    stripe.api_key = request.registry.settings['stripe.api_key']

    # Get the credit card details submitted by the form
    token = request.POST['stripeToken']
    plan = request.matchdict['plan']

    # Create a Customer
    customer = stripe.Customer.create(
      source=token,
      plan=plan,
      email=email
    )
    subscription_id = customer.subscriptions.data[0].id
    if hasattr(user, 'subscriptions'):
        subscriptions = user.subscriptions
    else:
        subscriptions = OOBTree()
        user.subscriptions = subscriptions

    username, password_hash = user.unconfirmed_db
    user.subscriptions[username] = subscription_id

    with admin_db.transaction() as conn:
        admin = zerodb.permissions.base.get_admin(conn)
        admin.add_user(username, password=password_hash, security=nohashing)

    user.unconfirmed_db = None

    return HTTPFound(request.route_path('home'))


@view_config(route_name='remove_subdb', renderer='json')
def remove_subdb(request):
    db = request.dbsession
    admin_db = request.admin_db
    username = request.matchdict['name']
    email = request.authenticated_userid
    user = db[UserRegistration].query(email=email)[0]

    if (username != email) and (not username.startswith(email + '-')):
        raise HTTPNotFound('No such username: %s' % username)

    with admin_db.transaction() as conn:
        admin = zerodb.permissions.base.get_admin(conn)
        admin.del_user(username)

    # Do stripe stuff
    if hasattr(user, "subscriptions") and (username in user.subscriptions):
        subscription_id = user.subscriptions[username]
        stripe.api_key = request.registry.settings['stripe.api_key']
        subscription = stripe.Subscription.retrieve(subscription_id)
        subscription.delete()
        del user.subscriptions[username]

    return HTTPFound(request.route_path('home'))
