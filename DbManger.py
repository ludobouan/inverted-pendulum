import sqlite3
import logging
import os

class DbManager:
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
            #log 'Creating schema'
            with open(schema_filename, 'rt') as f:
                schema = f.read()
            conn.executescript(schema)

            #log 'Inserting initial data'
            for i in range(16):
                for j in range(20):
                    s = i + j*0.01   
                    conn.execute("""
                    insert into Qvalue (State, Action1, Action2, Action3, Action4, Action5)
                    values ({0}, 0, 0, 0, 0, 0)
                    """.format(s))

    def __del__(self):
        self.conn.close()


if __name__ == "__main__":
    db = DbManager('Qtable')
    db.createDb('schema.sql')