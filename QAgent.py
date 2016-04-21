# *******************
# ***** Imports *****
# *******************

import random
from scipy import interpolate
import numpy as np

# *******************
# *****  Class  *****
# *******************

class QAgent(object):
    """Q-Learning agent"""
    def __init__(self, a_dbmgr, a_log, a_name, a_regression, a_epsilon_disabled):
        self.name = a_name
        self.dbmgr = a_dbmgr
        self.log = a_log
        agent = a_dbmgr.query("SELECT * FROM Agents WHERE Name = {0}".format("'" + a_name + "'")).fetchone()
        self.epsilon = agent[3]
        self.gamma = agent[4]
        self.alpha = agent[5]
        self.beta = agent[6]
        self.epsilon_d = agent[7]
        self.two_agent = bool(agent[8])
        self.eligibility = bool(agent[9])
        self.list_state = self.get_states()
        self.list_action = self.get_actions()
        self.policy = self.update_policy()
        self.regression = a_regression
        self.state_action_list_visited = []
        self.log.debug("Agent loaded")
        if a_epsilon_disabled:
            self.epsilon = 0.0

    def get_policy(self, a_state):
        if random.random() < self.epsilon:
            done = False
            while not done:
                m_action = random.choice(self.list_action)
                if self.isUpper(a_state) == m_action[1]:
                    done = True
                    action = m_action[0]
            greedy_action = self.policy[a_state[0]][0]
        else:
            action = self.policy[a_state[0]][0]
            greedy_action = action
        return action, greedy_action

    def learn_policy(self, a_state_action_list):
        if self.eligibility:
            Q_dict = self.getAllQ()
            E_dict = {}
            for state in self.list_state:
                for action in self.list_action:
                    try:
                        if action[0] == 0:
                            action = (0.0, action[1])
                        E_dict[str(state[0]) + ":" + str(action[0])] = 0
                    except KeyError:
                        print("KeyError1")
                        print(action)
            for step in a_state_action_list:
                state, action, new_state, new_action, greedy_action, reward = step
                if Q_dict[str(state[0]) + ":" + str(float(action))][1] == "False":
                    Q_dict[str(state[0]) + ":" + str(float(action))] = (Q_dict[str(state[0]) + ":" + str(float(action))][0], "True")
                try:
                    if action == 0:
                        action = 0.0
                    if greedy_action == 0:
                        greedy_action = 0.0
                    Q = Q_dict[str(state[0]) + ":" + str(float(action))][0]
                    target = reward + self.gamma * Q_dict[str(new_state[0]) + ":" + str(float(greedy_action))][0]
                    E_dict[str(state[0]) + ":" + str(action)] += 1
                except KeyError:
                    print("KeyError2")
                    print(action)
                for s in self.list_state:
                    for a in self.list_action:
                        try:
                            if a[0] == 0:
                                a = (0.0, a[1])
                            updatedQ = Q_dict[str(s[0]) + ":" + str(a[0])][0] + self.alpha * E_dict[str(s[0]) + ":" + str(a[0])] * (target - Q)
                            Q_dict[str(s[0]) + ":" + str(a[0])] = (updatedQ, Q_dict[str(s[0]) + ":" + str(a[0])][1])
                        
                            if greedy_action == new_action:
                                E_dict[str(s[0]) + ":" + str(a[0])] *= self.gamma * self.beta
                            else: 
                                E_dict[str(s[0]) + ":" + str(a[0])] = 0
                        except KeyError:
                            print(a)
                            print("KeyError3")
        else:
            Q_dict = self.getAllQ()
            for step in a_state_action_list:
                state, action, new_state, new_action, greedy_action, reward = step
                if Q_dict[str(state[0]) + ":" + str(float(action))][1] == "False":
                    Q_dict[str(state[0]) + ":" + str(float(action))] = (Q_dict[str(state[0]) + ":" + str(float(action))][0], "True")
                Q = Q_dict[str(state[0]) + ":" + str(action)][0]
                target = reward + self.gamma * Q_dict[str(new_state[0]) + ":" + str(greedy_action)][0]
                updatedQ = Q + self.alpha * (target - Q)
                Q_dict[str(state[0]) + ":" + str(action)] = (updatedQ, Q_dict[str(state[0]) + ":" + str(action)][1])
        if self.regression == "True":
            w = []
            x = []
            y = []
            z = []
            for s in self.list_state:
                for a in self.list_action:
                    if Q_dict[str(s[0]) + ":" + str(a[0])][1] == "True":
                        w.append((float(s[0].split(":")[0]) + float(s[0].split(":")[1]))/2)
                        x.append((float(s[0].split(":")[2]) + float(s[0].split(":")[3]))/2)
                        y.append(float(a[0]))
                        z.append(Q_dict[str(s[0]) + ":" + str(a[0])][0])
            self.log.info("Nb state visited : " + str(len(x)))
            W, X, Y = np.meshgrid(w, x ,y)
            approx = interpolate.LinearNDInterpolator((w, x, y), z, fill_value = 0)

            for s in self.list_state:
                for a in self.list_action:
                    Q_dict[str(s[0]) + ":" + str(a[0])] = (approx((float(s[0].split(":")[0]) + float(s[0].split(":")[1]))/2, (float(s[0].split(":")[2]) + float(s[0].split(":")[3]))/2, float(a[0])), Q_dict[str(s[0]) + ":" + str(a[0])][1])
        else:
            i = 0 
            for s in self.list_state:
                for a in self.list_action:
                    if Q_dict[str(s[0]) + ":" + str(a[0])][1] == "True":
                        i += 1
            self.log.info("Nb state visited : " + str(i))
        self.setAllQ(Q_dict)
        self.log.info("Qvalues updated")


    def update_policy(self):
        try:
            Qtable = self.dbmgr.query("SELECT State, Action, Value FROM Qvalues WHERE Agent = {0}".format("'" + self.name + "'")).fetchall()
        except sqlite3.OperationalError:
            self.log.debug("DataBase Error Id 1")
        self.log.info("Start update policy")
        policy = {}
        for state in Qtable:
            policy[state[0]] = (0, 0)

        for state in Qtable:
            if policy[state[0]][1] < state[2]:
                policy[state[0]] = (state[1], state[2])
            elif policy[state[0]][1] == state[2]:
                if random.random() > 0.8:
                    policy[state[0]] = (state[1], state[2])
        return policy


    def get_reward(self, a_state):
        for state in self.list_state:
            if state == a_state:
                return int(state[2])
        self.log.error("state not found for reward")

    def get_states(self):
        return(self.dbmgr.query("SELECT Value, isUpper, Reward FROM States WHERE Agent = {0}".format("'" + self.name + "'")).fetchall())

    def get_actions(self):
        return(self.dbmgr.query("SELECT Value, isUpper FROM Actions WHERE Agent = {0}".format("'" + self.name + "'")).fetchall())

    def get_state(self, a_state):
        a_state = a_state.split(":")
        for state in self.list_state:
            state_spl = state[0].split(":")
            if float(a_state[0]) >= float(state_spl[0]) and float(a_state[0]) < float(state_spl[1]) and float(a_state[1]) >= float(state_spl[2]) and float(a_state[1]) < float(state_spl[3]):
                return state
        self.log.error("State not found")

    def isUpper(self, a_state):
        for state in self.list_state:
            if a_state == state:
                return state[1]

    def epsilon_discount(self):
        self.epsilon *= self.epsilon_d
        self.dbmgr.query("UPDATE Agents SET Epsilon = {0} WHERE Name = {1}".format(self.epsilon, "'" + str(self.name) + "'"))

    def getAllQ(self):
        Q_dict = {}
        try:
            Qtable = self.dbmgr.query("SELECT State, Action, Value, Visited FROM Qvalues WHERE Agent = {0}".format("'" + self.name + "'"))
        except sqlite3.OperationalError:
            self.log.debug("DataBase Error Id 1")

        for item in Qtable:
            Q_dict[str(item[0]) + ":" + str(item[1])] = (float(item[2]), item[3])
        return Q_dict

    def setAllQ(self, a_Q_dict):
        for item in a_Q_dict:
            item_spl = item.split(":")
            self.dbmgr.query("UPDATE QValues SET Value = {0} WHERE Agent = {1} AND State = {2} AND Action = {3}".format(a_Q_dict[item][0], "'" + str(self.name) + "'", "'" + str(item[:len(item)-len(item_spl[4])-1]) + "'"  , "'" + str(item_spl[4]) + "'"))
            self.dbmgr.query("UPDATE QValues SET Visited = {0} WHERE Agent = {1} AND State = {2} AND Action = {3}".format("'" + a_Q_dict[item][1] + "'", "'" + str(self.name) + "'", "'" + str(item[:len(item)-len(item_spl[4])-1]) + "'"  , "'" + str(item_spl[4]) + "'"))