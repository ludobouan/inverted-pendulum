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
import DbManager
import logging
import sys

# ******************
# *** Global Var ***
# ******************

# *******************
# ***** CLasses *****
# *******************

class QAgent:
    """Q-Learning agent"""
    def __init__(self, a_actions):
        # super().__init__()
        self.actions = a_actions
        self.db_filename = 'test.db'
    
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

    def targetPolicy(self):
        """
        
        """
        
    def update(self):
        pass

    def getQ(self, s, a):
        try: dbmg.query("SELECT {0} FROM Qvalue WHERE State = {1}".format(a, s))
        return dbmg.cur.fetchone()

# *******************
# **** Functions ****
# *******************

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__":
    pass