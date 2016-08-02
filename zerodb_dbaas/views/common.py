class ValidationError(Exception):
    pass


def nohashing(uname, password, key_file, cert_file, appname, key):
    return password, key


def decode_password_hex(password):
    if password.startswith("hash::"):
        return bytes.fromhex(password[6:])
    else:
        raise ValidationError(
                'You need to turn javascript on to ' +
                'generate public key from the passphrase client-side')
