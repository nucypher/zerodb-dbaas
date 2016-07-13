import six

from ZODB.POSException import ConflictError

from pyramid.view import view_config

from zerodb.crypto import ecc
from zerodb.permissions import elliptic

kdf = elliptic.Client.kdf


class ValidationError(Exception):
    pass


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

        if isinstance(passphrase, six.binary_type) and passphrase[0] == b'\x04'[0]:
            pubkey = passphrase
        else:
            pubkey = ecc.private(str(passphrase), (str(username), "ZERO"), kdf=kdf).get_pubkey()

        db._storage.add_user(username, pubkey)

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

        if isinstance(passphrase, six.binary_type) and passphrase[0] == b'\x04'[0]:
            pubkey = passphrase
        else:
            pubkey = ecc.private(
                    str(passphrase), (str(username), "ZERO"),
                    kdf=kdf).get_pubkey()

        db._storage.change_key(username, pubkey)

    except ConflictError:
        raise
    except Exception as e:
        return {'ok': 0, 'error': str(e), 'error_type': e.__class__.__name__}

    return {'ok': 1}
