import sqlite3
import logging
import os
from configparser import SafeConfigParser

log = logging.getLogger('root')

# Config
parser = SafeConfigParser()
parser.read('config.ini')

db_name = parser.get('Main', 'dbname')

class DbManager():
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.conn.execute('pragma foreign_keys = on')
        self.conn.commit()
        self.cur = self.conn.cursor()
        self.db = db
        log.debug("DbManager init")

    def query(self, arg):
        self.cur.execute(arg)
        self.conn.commit()
        return self.cur

    def createDb(self, schema_filename):
        with sqlite3.connect(self.db) as conn:
            with open(schema_filename, 'rt') as f:
                schema = f.read()
            conn.executescript(schema)
            log.debug('Table created')

            for i in range(17):
                for j in range(6):
                    state = i + j*0.01   
                    conn.execute("""
                    insert into Qvalue (State, Action1, Action2, Action3, Action4, Action5)
                    values ({0}, 0, 0, 0, 0, 0)
                    """.format(state))
            log.debug('Initial data inserted')

    def release(self):
        self.conn.close()
        log.debug('Sql connection closed')

    def __del__(self):
        try:
            self.conn.close()
            log.debug('Sql connection auto closed')
        except:
            log.error("Cant close db")