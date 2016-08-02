import zerodb

from ZODB.POSException import ConflictError

from pyramid.view import view_config


class ValidationError(Exception):
    pass


def nohashing(uname, password, key_file, cert_file, appname, key):
    return password, key


@view_config(route_name='_add_user', renderer='json')
def add_user(request):
    admin_db = request.admin_db

    if request.content_type == 'application/json':
        form = request.json_body
    else:
        form = request.params

    username = form.get('username')
    passphrase = form.get('passphrase')
    # If javascript hashed password, we have "hash::<hex>"
    # Else just password

    try:
        if not (username and passphrase):
            raise ValidationError('Username and passphrase are required')

        with admin_db.transaction() as conn:
            admin = zerodb.permissions.base.get_admin(conn)
            if passphrase.startswith("hash::"):
                passphrase = bytes.fromhex(passphrase[6:])
                admin.add_user(username, password=passphrase, security=nohashing)
            else:
                admin.add_user(username, password=passphrase)

    except ConflictError:
        raise
    except Exception as e:
        return {'ok': 0, 'error': str(e), 'error_type': e.__class__.__name__}

    return {'ok': 1}


@view_config(route_name='_del_user', renderer='json')
def del_user(request):
    admin_db = request.admin_db

    if request.content_type == 'application/json':
        form = request.json_body
    else:
        form = request.params

    username = form.get('username')

    try:
        if not username:
            raise ValidationError('Username is required')

        with admin_db.transaction() as conn:
            admin = zerodb.permissions.base.get_admin(conn)
            admin.del_user(username)

    except ConflictError:
        raise
    except Exception as e:
        return {'ok': 0, 'error': str(e), 'error_type': e.__class__.__name__}

    return {'ok': 1}


@view_config(route_name='_edit_user', renderer='json')
def edit_user(request):
    admin_db = request.admin_db

    if request.content_type == 'application/json':
        form = request.json_body
    else:
        form = request.params

    username = form.get('username')
    passphrase = form.get('passphrase')

    try:
        if not (username and passphrase):
            raise ValidationError('Username and passphrase are required')

        with admin_db.transaction() as conn:
            admin = zerodb.permissions.base.get_admin(conn)
            if passphrase.startswith("hash::"):
                passphrase = bytes.fromhex(passphrase[6:])
                admin.change_cert(username, password=passphrase,
                                  security=nohashing)
            else:
                admin.change_cert(username, password=passphrase)

    except ConflictError:
        raise
    except Exception as e:
        return {'ok': 0, 'error': str(e), 'error_type': e.__class__.__name__}

    return {'ok': 1}
