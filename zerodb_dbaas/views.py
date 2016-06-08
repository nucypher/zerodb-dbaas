from ZODB.POSException import ConflictError

from pyramid.view import view_config
from .models import Counter

class ValidationError(Exception):
    pass


@view_config(route_name='home', renderer='templates/index.pt')
@view_config(route_name='count_json', renderer='json')
def my_view(request):
    db = request.dbsession
    count = 0

    counters = db[Counter].query(name='root')
    for counter in counters:
        counter.inc()
        count = counter.count
        break

    return {'project': 'zerodb-dbaas', 'count': count}


@view_config(route_name='_add_user', renderer='json')
def add_user(request):
    db = request.dbsession

    if request.content_type == 'application/json':
        form = request.json_body
    else:
        form = request.params

    username = form.get('username')
    passphrase = form.get('passphrase')

    try:
        if not (username and passphrase):
            raise ValidationError('Username and passphrase are required')

        db._storage.add_user(username, passphrase)

    except ConflictError:
        raise
    except Exception as e:
        return {'ok': 0, 'error': str(e), 'error_type': e.__class__.__name__}

    return {'ok': 1}


@view_config(route_name='_del_user', renderer='json')
def del_user(request):
    db = request.dbsession

    if request.content_type == 'application/json':
        form = request.json_body
    else:
        form = request.params

    username = form.get('username')

    try:
        if not username:
            raise ValidationError('Username is required')

        db._storage.del_user(username)

    except ConflictError:
        raise
    except Exception as e:
        return {'ok': 0, 'error': str(e), 'error_type': e.__class__.__name__}

    return {'ok': 1}


@view_config(route_name='_edit_user', renderer='json')
def edit_user(request):
    db = request.dbsession

    if request.content_type == 'application/json':
        form = request.json_body
    else:
        form = request.params

    username = form.get('username')
    passphrase = form.get('passphrase')

    try:
        if not (username and passphrase):
            raise ValidationError('Username and passphrase are required')

        db._storage.change_key(username, passphrase)

    except ConflictError:
        raise
    except Exception as e:
        return {'ok': 0, 'error': str(e), 'error_type': e.__class__.__name__}

    return {'ok': 1}
