import os

import rocksdb

conn = None
def get_conn():
    global conn
    if conn:
        return conn

    if not os.path.exists('states'):
        os.makedirs('states')
    conn = rocksdb.DB('states/inspace.db', rocksdb.Options(create_if_missing=True))
    return conn


# os.removedirs('/dev/shm/tempspace.db')
temp_conn = None
def get_temp_conn():
    global temp_conn

    temp_conn = rocksdb.DB('/dev/shm/tempspace.db', rocksdb.Options(create_if_missing=True))
    return temp_conn
