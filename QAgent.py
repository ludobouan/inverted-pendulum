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
import os
import sys
from DbManager import dbManager
import logging
import random
dbmg = dbManager('Qtable')
# ******************
# *** Global Var ***
# ******************

# *******************
# ***** CLasses *****
# *******************

log = logging.getLogger('root')
dic = {-20:"Action1", -10:"Action2", 0:"Action3", 10:"Action4", 20:"Action5"}

class QAgent:
    """Q-Learning agent"""
    def __init__(self, a_actions):
        # super().__init__()
        self.actions = a_actions
        self.db_filename = 'testdb.db'
        self.epsilon = 0.15
    
    def policy(self, state):
        """
        Chooses action 
        Input: state (float)
        Output: action (int)
        """
        if random.random() < self.epsilon: # exploration
            action = random.choice(self.actions)
        else:
            q = [self.getQ(state, a) for a in self.actions]
            maxQ = max(q)
            count = q.count(maxQ)
            if count > 1:
                best = [i for i in range(len(self.actions)) if q[i] == maxQ]
                i = random.choice(best)
            else:
                i = q.index(maxQ)
     
            action = self.actions[i]
        return action

    def targetPolicy(self, state):
        pass
        
    def update(self):
        pass

    def getQ(self, s, a):
        dbmg.query("SELECT {0} FROM Qvalue WHERE State = {1}".format(dic[a], s))
        rep = dbmg.cur.fetchone()
        if rep is None:
            repo = 0
        else:
            repo = rep[0]
        return repo

    def setQ(self, s, a, v):
        dbmg.query("UPDATE Qvalue SET {0} = {1} WHERE State = {2}".format(dic[a], v, s))

# *******************
# **** Functions ****
# *******************

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__" and __package__ is None:
    q = QAgent([-20,-10,0,10,20])
    print(q.getQ(1.01, 'Action1'))