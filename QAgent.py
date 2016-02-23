# ********************************
# @author     : Ludovic Bouan
# @contact    : ludo.bouan@gmail.com
# created on  : 26.09.1015
# title       : Q-Learning Agent
# to do       :
# ********************************

# *******************
# ***** Imports *****
# *******************
import logging
import random
import sqlite3
from configparser import SafeConfigParser

from DbManager import DbManager

# ******************
# *** Global Var ***
# ******************
parser = SafeConfigParser()
parser.read('config.ini')

log = logging.getLogger('root')

# *******************
# ***** CLasses *****
# *******************

class QAgent():
    """Q-Learning agent"""
    def __init__(self, a_dbmg, a_type):
        self.action_names = ("Action1", 
                             "Action2", 
                             "Action3", 
                             "Action4", 
                             "Action5")

        self.Qvalue_table = "Qvalue_" + a_type
        self.Evalue_table = "Evalue_" + a_type
        
        self.epsilon = float(parser.get('Coeffs','EPSILON'))
        
        self.dbmg = a_dbmg
    
    def policy(self, state):
        """
        Chooses action 
        Input: state (float)
        Output: action (int)
        """
    
        q_list = [self.getQ(state, i_action) for i_action in self.action_list]
        maxQ = max(q_list)
        count = q_list.count(maxQ)
        if count > 1:
            best = [i for i in range(5) if q_list[i] == maxQ]
            i = random.choice(best)
        else:
            i = q_list.index(maxQ)
 
        greedy_action = self.action_list[i]

        if random.random() < self.epsilon: # exploration
            action = random.choice(self.action_list)
        else:
            action = greedy_action
        
        return action, greedy_action

    def getQ(self, s, a):
        i = self.action_list.index(a)
        try:
            self.dbmg.query("SELECT {0} FROM {2} WHERE State = {1}".format(self.action_names[i], s, self.Qvalue_table))
        except sqlite3.OperationalError:
            log.debug("Database Error")
        rep = self.dbmg.cur.fetchone()
        if rep is None:
            repo = 0
            log.error("State not found !")
        else:
            repo = rep[0]
        return repo
        
    def getAllQ(self):
        try:
            self.dbmg.query("SELECT Action1, Action2, Action3, Action4, Action5 FROM {0}".format(self.Qvalue_table))
        except sqlite3.OperationalError:
            log.debug("Database Error")
        rep = self.dbmg.cur.fetchall()
        if rep is None:
            repo = 0
            log.error("Db error")
        else:
            return rep

    def getE(self, s, a):
        i = self.action_list.index(a)
        try:
            self.dbmg.query("SELECT E FROM {1} WHERE State = {0}".format(s, self.Evalue_table))
        except sqlite3.OperationalError:
            log.debug("Database Error")
        rep = self.dbmg.cur.fetchone()
        if rep is None:
            repo = 0
            log.error("State not found !")
        else:
            repo = rep[0]
        return repo

    def setQ(self, s, a, v):
        i = self.action_list.index(a)
        try:
            self.dbmg.query("UPDATE {3} SET {0} = {1} WHERE State = {2}".format(self.action_names[i], v, s, self.Qvalue_table))
        except sqlite3.OperationalError:
            log.debug("Database Error")

    def setEi(self,a_str):
        try:
            self.dbmg.query("UPDATE {0} SET E = {1}".format(self.Evalue_table, a_str))
        except sqlite3.OperationalError:
            log.debug("Database Error")
            
    def setE(self, s, a, v):
        i = self.action_list.index(a)
        try:
            self.dbmg.query("UPDATE {2} SET E = {0} WHERE State = {1}".format(v, s, self.Evalue_table))
        except sqlite3.OperationalError:
            log.debug("Database Error")
            
    def getAllE(self):
        try:
            self.dbmg.query("SELECT E FROM {0}".format(self.Evalue_table))
        except sqlite3.OperationalError:
            log.debug("Database Error")
        rep = self.dbmg.cur.fetchall()
        if rep is None:
            repo = 0
            log.error("Db error")
        else:
            E_list = []
            for row in rep:
                E_list.append(row[0])
        return E_list


class UpperQAgent(QAgent):
    """docstring for UpperQAgent"""
    def __init__(self, a_dbmg):
        self.action_list = (int(parser.get('Upper','Action1')), 
                    int(parser.get('Upper','Action2')), 
                    int(parser.get('Upper','Action3')), 
                    int(parser.get('Upper','Action4')), 
                    int(parser.get('Upper','Action5')))


        super(UpperQAgent, self).__init__(a_dbmg, 'upper')
        
        self.State = self.getStates()

    def getStates(self):
        states = []
        for i in range(-4,5):
            if i != 0:
                for j in range(-3,4):
                    if j != 0:
                        states.append(i + 0.01 * j)

        return states


class LowerQAgent(QAgent):
    """docstring for LowerQAgent"""
    def __init__(self, a_dbmg):
        self.action_list = (int(parser.get('Lower','Action1')), 
                    int(parser.get('Lower','Action2')), 
                    int(parser.get('Lower','Action3')), 
                    int(parser.get('Lower','Action4')), 
                    int(parser.get('Lower','Action5')))

        super(LowerQAgent, self).__init__(a_dbmg, 'lower')
        
        self.State = self.getStates()


    def getStates(self):
        states = []
        for i in range(-7,8):
            if i != 0:
                for j in range(-3,4):
                    if j != 0:
                        states.append(i + 0.01 * j)

        return states