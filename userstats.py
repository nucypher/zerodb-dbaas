#!/usr/bin/env python3.5
# Reads stats and saves in admin_db

import os
import ZEO
import ZEO.tests.testssl
import zerodb.db
from BTrees.OIBTree import BTree
from datetime import datetime
from zerodb.crypto import kdf
from zerodb.permissions.userstats import userstats

DB_FILENAME = os.path.join(os.path.dirname(__file__), "_server/db/db.fs")
ZEO_SERVER = ('localhost', 8001)
server_cert = ZEO.tests.testssl.server_cert
USERNAME = 'root'
PASSWORD = '123'

####################
stats = userstats(DB_FILENAME)  # in format (user_id, username, bytes)

h, _ = kdf.hash_password(
        USERNAME, PASSWORD,
        key_file=None, cert_file=None, appname='zerodb.com', key=None)
admin_db = ZEO.DB(
        ZEO_SERVER,
        ssl=zerodb.db.make_ssl(server_cert=server_cert),
        credentials=dict(name=USERNAME, password=h),
        wait_timeout=11)

with admin_db.transaction() as conn:
    admin = conn.root()['admin']
    if not hasattr(admin, 'user_stats'):
        admin.user_stats = BTree()

    for _, username, size in stats:
        admin.user_stats[username] = size

    admin.user_stats_updated = datetime.utcnow()
