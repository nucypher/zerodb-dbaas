import hashlib
import binascii

from datetime import datetime
from datetime import timedelta

from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.interfaces import IBeforeRender
from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPFound

from zerodb.permissions import elliptic

from zerodb_dbaas.models import UserRegistration

kdf = elliptic.Client.kdf


class ValidationError(Exception):
    pass


@subscriber(IBeforeRender)
def globals_factory(event):
    """Provide master template"""
    master = get_renderer('zerodb_dbaas:templates/master.pt').implementation()
    event['master'] = master


@view_config(route_name='home', renderer='zerodb_dbaas:templates/index.pt')
def home(request):
    """Home page"""
    return {}


@view_config(route_name='login', renderer='zerodb_dbaas:templates/login.pt')
def login(request):
    """Login form"""
    # db = request.dbsession
    form = request.params

    if not form:
        return {'ok': 1}

    username = form.get('inputEmail')  # XXX
    password = form.get('inputPassword')

    try:
        if not (username and password):
            raise ValidationError('Account name and password are required')

        # ...

        return HTTPFound(request.route_url('home'))

    except (ValidationError, LookupError) as e:
        return {'ok': 0, 'error': str(e), 'error_type': e.__class__.__name__}

    return {'ok': 0}


@view_config(route_name='register', renderer='zerodb_dbaas:templates/register.pt')
@view_config(route_name='_register', renderer='json')
def register(request):
    """Sign up form"""
    db = request.dbsession

    if request.content_type == 'application/json':
        form = request.json_body
    else:
        form = request.params

    if not form:
        return {'ok': 1}

    email = form.get('inputEmail')
    password = form.get('inputPassword')
    passwordConfirm = form.get('inputPasswordConfirmation')

    try:
        if not (email and password and passwordConfirm):
            raise ValidationError('All fields are required')

        user = db[UserRegistration].query(email=email)
        if user:
            raise ValidationError('Account name is already in use')

        try:
            pubkey = binascii.unhexlify(password)
        except:
            raise ValidationError(
                    'You need to turn javascript on to ' +
                    'generate public key from the passphrase client-side')
        pubkey = b'\x04' + pubkey

        now = datetime.now()
        hashcode = hashlib.sha256((
            email + "$3cr3t" + now.isoformat()).encode()).hexdigest()

        newUser = UserRegistration(
            email=email,
            password=pubkey,
            created=now,
            completed=datetime(1970, 1, 1),
            hashcode=hashcode)

        db.add(newUser)

        if request.content_type == 'application/json':
            return {'ok': 1, 'hashcode': hashcode}
        else:
            return HTTPFound(request.route_url('register-email', _query={'hashcode': hashcode}))

    except ValidationError as e:
        return {'ok': 0, 'error': str(e), 'error_type': e.__class__.__name__}

    return {'ok': 0}


@view_config(route_name='register-email', renderer='zerodb_dbaas:templates/register-email.pt')
def register_email(request):
    """Send confirmation email"""
    # FIXME Just shows page for now
    form = request.params

    hashcode = form.get('hashcode')
    return {'ok': 1, 'url': request.route_url('register-confirm', _query={'hashcode': hashcode})}


@view_config(route_name='register-confirm', renderer='zerodb_dbaas:templates/register-confirm.pt')
@view_config(route_name='_register_confirm', renderer='json')
def register_confirm(request):
    """Finish registration

    Verifies all preconditions and creates the database user.
    """
    db = request.dbsession

    if request.content_type == 'application/json':
        form = request.json_body
    else:
        form = request.params

    hashcode = form.get('hashcode')

    try:
        if not hashcode:
            raise ValidationError('No registration code provided')

        user = db[UserRegistration].query(hashcode=hashcode)

        if not user:
            raise ValidationError('Invalid registration code')

        user = user[0]
        now = datetime.now()

        if user.created + timedelta(days=14) < now:
            raise ValidationError('Registration code has expired')

        if user.completed > datetime(1970, 1, 1):
            raise ValidationError('Registration code has already been used')

        user.completed = now
        db._storage.add_user(user.email, user.password)

        if request.content_type == 'application/json':
            return {'ok': 1}
        else:
            return HTTPFound(request.route_url('register-success'))

    except (ValidationError, LookupError) as e:
        return {'ok': 0, 'error': str(e), 'error_type': e.__class__.__name__}

    return {'ok': 0}


@view_config(route_name='register-success', renderer='zerodb_dbaas:templates/register-success.pt')
def register_success(request):
    """Success landing page"""
    # db = request.dbsession
    form = request.params

    if not form:
        return {'ok': 1}

    username = form.get('inputEmail')  # XXX
    password = form.get('inputPassword')  # XXX

    try:
        if not (username and password):
            raise ValidationError('Account name and password are required')

        # ...

        return HTTPFound(request.route_url('home'))

    except (ValidationError, LookupError) as e:
        return {'ok': 0, 'error': str(e), 'error_type': e.__class__.__name__}

    return {'ok': 0}


@view_config(route_name='_account_available', renderer='json')
def account_available(request):
    """Check availability of email"""
    db = request.dbsession
    form = request.json_body

    #  username = form.get('inputAccount')  # XXX
    email = form.get('inputEmail')

    try:
        if not email:
            raise ValidationError('Account name or email are required')

        user = db[UserRegistration].query(email=email)
        if user:
            raise ValidationError('Account name is already in use')

    except ValidationError as e:
        return {'ok': 0, 'error': str(e), 'error_type': e.__class__.__name__}

    return {'ok': 1}


@view_config(route_name='registrations', renderer='zerodb_dbaas:templates/registrations.pt')
def registrations(request):
    """Show pending registrations"""
    db = request.dbsession

    users = db[UserRegistration].query(
        completed=datetime(1970, 1, 1),
        sort_index='created',
        reverse=True,
        limit=10)

    return {'users': users}
