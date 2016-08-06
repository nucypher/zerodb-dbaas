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


suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


def humansize(nbytes):
    if nbytes == 0:
        return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])
