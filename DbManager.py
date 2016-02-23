import sqlite3
import logging
import os
from configparser import SafeConfigParser

log = logging.getLogger('root')

# Config
parser = SafeConfigParser()
parser.read('config.ini')

db_name = parser.get('Main', 'DbName')

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

    def createDb(self, schema_filename_1, schema_filename_2, schema_filename_3, schema_filename_4):
        with sqlite3.connect(self.db) as conn:
            with open(schema_filename_1, 'rt') as f:
                schema = f.read()
            conn.executescript(schema)
            log.debug('Table Qvalue_lower created')
            
            with open(schema_filename_2, 'rt') as f:
                schema = f.read()
            conn.executescript(schema)
            log.debug('Table Qvalue_upper created')

            for i in range(-7,8):
                if i != 0:
                    for j in range(-3,4):
                        if j != 0: 
                            s = i + 0.01 * j
                            conn.execute("""
                            insert into Qvalue_lower (State, Action1, Action2, Action3, Action4, Action5)
                            values ({0}, 0, 0, 0, 0, 0)
                            """.format(s))

            for i in range(-4,5):
                if i != 0:
                    for j in range(-3,4):
                        if j != 0:
                            s = i + 0.01 * j 
                            conn.execute("""
                            insert into Qvalue_upper (State, Action1, Action2, Action3, Action4, Action5)
                            values ({0}, 0, 0, 0, 0, 0)
                            """.format(s))

            log.debug('Initial data inserted')

    def __del__(self):
        try:
            self.conn.close()
            log.debug('Sql connection auto closed')
        except:
            log.error("Cant close db")
    
    def release(self):
        self.conn.close()
        log.debug('Sql connection closed')