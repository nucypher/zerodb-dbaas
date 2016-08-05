from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound


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

    return {'db_users': db_users}


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

    return {'username': username}
