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

class QAgent(object):
    """Q-Learning agent"""
    def __init__(self, a_dbmg):
        self.epsilon = float(parser.get('Coeffs','epsilon'))
        self.dbmg = a_dbmg
    
    def policy(self, state):
        """
        Returns action and greedy action 
        """
        q_list = [self.getQ(state, i_action) for i_action in self.action_list]
        maxQ = max(q_list) # Q value of best action
        count = q_list.count(maxQ) # number of best actions

        if count > 1: # if more than one best action
            best = [i_n for i_n in range(len(q_list)) if q_list[i_n] == maxQ]
            best_action_index = random.choice(best)
        else:
            best_action_index = q_list.index(maxQ) # index of best action
 
        # greedy action is best action
        greedy_action = self.action_list[best_action_index]

        # exploration
        if random.random() < self.epsilon:
            action = random.choice(self.action_list)
        else:
            action = greedy_action
        
        return action, greedy_action

    def getQ(self, s, a):
        try:
            i = self.action_list.index(a)
        except ValueError:
            log.error("Action not in the list : " + str(a) + " - " + str(self.action_list) + " - " + str(s))
        
        try:
            self.dbmg.query("SELECT {0} FROM Qvalue WHERE State = {1}".format(self.action_names[i], s))
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
            self.dbmg.query("UPDATE Qvalue SET {0} = {1} WHERE State = {2}".format(self.action_names[i], v, s))
        except sqlite3.OperationalError:
            log.debug("Database Error")

class QAgentLower(QAgent):
    """docstring for QAgentLower"""
    def __init__(self, a_dbmg):
        self.action_names = ['Action1', 'Action3','Action5']
        self.action_list = (int(parser.get('Actions','Action1')), 
                            int(parser.get('Actions','Action3')),                          
                            int(parser.get('Actions','Action5')))

        super(QAgentLower, self).__init__(a_dbmg)

class QAgentUpper(QAgent):
    """docstring for QAgentUpper"""
    def __init__(self, a_dbmg):
        self.action_names = ['Action2', 'Action3','Action4']
        self.action_list = (int(parser.get('Actions','Action2')), 
                            int(parser.get('Actions','Action3')),                          
                            int(parser.get('Actions','Action4')))

        super(QAgentUpper, self).__init__(a_dbmg)

        
        
        