# *******************
# ***** Imports *****
# *******************

import sqlite3

# *******************
# *****  Class  *****
# *******************

class DbManager():
    def __init__(self, a_db, a_log):
        self.db_connexion = sqlite3.connect(a_db)
        self.db_connexion.execute('pragma foreign_keys = on')
        self.db_connexion.commit()
        self.cursor = self.db_connexion.cursor()
        self.database = a_db
        self.log = a_log
        self.log.debug("DbManager init")

    def create_database(self, a_states):
    	with sqlite3.connect(self.database) as self.db_connexion:
            with open('schema.sql', 'rt') as f:
                schema = f.read()
            self.db_connexion.executescript(schema)
            self.log.debug('Table created')

    def query(self, a_arg):
        self.cursor.execute(a_arg)
        self.db_connexion.commit()
        return self.cursor

    def release(self):
        self.db_connexion.close()

