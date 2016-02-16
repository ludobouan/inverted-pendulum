import sqlite3
#import logging
import os

#log = logging.getLogger('root')

class DbManager():
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.conn.execute('pragma foreign_keys = on')
        self.conn.commit()
        self.cur = self.conn.cursor()
        self.db = db

    def query(self, arg):
        self.cur.execute(arg)
        self.conn.commit()
        return self.cur

    def createDb(self, schema_filename):
        with sqlite3.connect(self.db) as conn:
            with open(schema_filename, 'rt') as f:
                schema = f.read()
            conn.executescript(schema)
            #log.debug('table created')

            for i in range(21):
                for j in range(41):
                    s = i - 10 + j*0.01   
                    conn.execute("""
                    insert into Qvalue (State, Action1, Action2, Action3, Action4, Action5)
                    values ({0}, 0, 0, 0, 0, 0)
                    """.format(s))
            #log.info('initial data inserted')

    def __del__(self):
        self.conn.close()
        #log.info('sql connection closed')
    
    def release(self):
        self.conn.close()
        #log.info('sql connection closed')


if __name__ == "__main__" and __package__ is None:
    #import logSetup
    db = DbManager('Qdatabase.db')
    db.createDb('schema.sql')