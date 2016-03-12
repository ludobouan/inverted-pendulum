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
        self.global_action_names = ['Action1', 'Action2', 'Action3', 'Action4','Action5']
        self.global_action_list = (int(parser.get('Actions','Action1')), 
                            int(parser.get('Actions','Action2')), 
                            int(parser.get('Actions','Action3')),
                            int(parser.get('Actions','Action4')),                         
                            int(parser.get('Actions','Action5')))
    
    def policy(self, state):
        """
        Returns action and greedy action 
        """
        # exploration
        if random.random() < self.epsilon:
            action = random.choice(self.action_list)
        else:
            try:
                action = self.state_action_dict[state]
            except:
                action = 0
                log.error("State not found in dict : " + str(state) + "n" + str(self.state_action_dict))
                log.error(self.name)
        try:
            greedy_action = self.state_action_dict[state]
        except:
            greedy_action = 0
            log.error("State not found in dict : " + str(state) + "n" + str(self.state_action_dict))
            log.error(self.name)
        
        return action, greedy_action

    def getAllQ(self):
        Q_dict = {}
        
        try:
            self.dbmg.query("SELECT * FROM Qvalue")
        except sqlite3.OperationalError:
            log.debug("Database Error")
        
        rep = self.dbmg.cur.fetchall()
        if rep is None:
            log.error("Bd empty !")
        for ligne in  rep:
            Q_dict[str(ligne[0]) + ":" + str(self.global_action_list[0])] = ligne[1]
            Q_dict[str(ligne[0]) + ":" + str(self.global_action_list[1])] = ligne[2]
            Q_dict[str(ligne[0]) + ":" + str(self.global_action_list[2])] = ligne[3]
            Q_dict[str(ligne[0]) + ":" + str(self.global_action_list[3])] = ligne[4]
            Q_dict[str(ligne[0]) + ":" + str(self.global_action_list[4])] = ligne[5]
        return Q_dict

    def setAllQ(self, Q_dict):
        for element in Q_dict:
            name = element.split(":")
            try:
                self.dbmg.query("UPDATE Qvalue SET {0} = {1} WHERE State = {2}".format(self.global_action_names[self.global_action_list.index(int(name[1]))], Q_dict[element], name[0]))
            except sqlite3.OperationalError:
                log.debug("Database Error")

    def getStateActionPairs(self):
        states_actions = []
        for i in range(17):
            for j in range(6):
                state = i + j*0.01
                for action in self.global_action_list:
                    states_actions.append((state, action))

        return [(sa[0], sa[1]) for sa in states_actions]

class QAgentLower(QAgent):
    """docstring for QAgentLower"""
    def __init__(self, a_dbmg):
        self.action_names = ['Action1', 'Action3','Action5']
        self.action_list = (int(parser.get('Actions','Action1')), 
                            int(parser.get('Actions','Action3')),                          
                            int(parser.get('Actions','Action5')))
        self.name = "Lower"

        super(QAgentLower, self).__init__(a_dbmg)

    def get_policy(self):
        try:
            Qtable = self.dbmg.query("SELECT State, {0}, {1}, {2} FROM Qvalue".format(self.action_names[0],self.action_names[1],self.action_names[2])).fetchall()
        except sqlite3.OperationalError:
            log.debug("Database Error")

        self.state_action_dict = {}

        for state in Qtable:
            if float(state[0]) < 5 or float(state[0]) >= 12:
                q_list = [float(q) for q in state[1:]]
                maxQ = max(q_list) # Q value of best action
                count = q_list.count(maxQ) # number of best actions

                if count > 1: # if more than one best action
                    best = [i_n for i_n in range(len(q_list)) if q_list[i_n] == maxQ]
                    best_action_index = random.choice(best)
                else:
                    best_action_index = q_list.index(maxQ) # index of best action

                self.state_action_dict[state[0]] = self.action_list[best_action_index]


class QAgentUpper(QAgent):
    """docstring for QAgentUpper"""
    def __init__(self, a_dbmg):
        self.action_names = ['Action2', 'Action3','Action4']
        self.action_list = (int(parser.get('Actions','Action2')), 
                            int(parser.get('Actions','Action3')),                          
                            int(parser.get('Actions','Action4')))
        self.name = "Upper"

        super(QAgentUpper, self).__init__(a_dbmg)

    def get_policy(self):
        try:
            Qtable = self.dbmg.query("SELECT State, {0}, {1}, {2} FROM Qvalue".format(self.action_names[0],self.action_names[1],self.action_names[2])).fetchall()
        except sqlite3.OperationalError:
            log.debug("Database Error")

        self.state_action_dict = {}

        for state in Qtable:
            if float(state[0]) >= 5 and float(state[0]) < 12:
                q_list = [float(q) for q in state[1:]]
                maxQ = max(q_list) # Q value of best action
                count = q_list.count(maxQ) # number of best actions

                if count > 1: # if more than one best action
                    best = [i_n for i_n in range(len(q_list)) if q_list[i_n] == maxQ]
                    best_action_index = random.choice(best)
                else:
                    best_action_index = q_list.index(maxQ) # index of best action

                self.state_action_dict[state[0]] = self.action_list[best_action_index]
        
        
        