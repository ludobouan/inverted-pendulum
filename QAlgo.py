# ********************************
# @author     : Ludovic Bouan
# @contact    : ludo.bouan@gmail.com
# title       : Inverted Pendulum / Q-Learning
# ********************************

# *******************
# ***** Imports *****
# *******************

import os
import sys
import time
import numpy

import QAgent
import enviroment
import DbManager

import logging
from configparser import SafeConfigParser
from logging.handlers import RotatingFileHandler
import matplotlib.pyplot as plt

# *******************
# **** Functions ****
# *******************
def getLogLevel():
    loglevel = parser.get('Main', 'LogLevel')
    if loglevel == "DEBUG":
        return logging.DEBUG
    if loglevel == "INFO":
        return logging.INFO
    if loglevel == "ERROR":
        return logging.ERROR
        
def general_debug(type, value, traceback):
    log.error("Error : " + str(type) + " - " + str(value))

def main():
    log.debug(os.path.isfile(db_name))
    if not os.path.isfile(db_name):
        dbmgr = DbManager.DbManager(db_name)
        dbmgr.createDb('schema.sql')
        log.info("Database created")
    else:
        dbmgr = DbManager.DbManager(db_name)

    env = enviroment.env()
    k = 0
    figure, axe = plt.subplots()
    line1, = axe.plot([],[])
    line2, = axe.plot([],[])
    axe.set_autoscaley_on(True)
    axe.grid()
    f = open('recompense_moyenne.data', 'r')
    lines = f.read().split()
    f.close()
    for line in lines:
        k += 1
        line = line.split(":")
        line1.set_xdata(numpy.append(line1.get_xdata(), k))
        line1.set_ydata(numpy.append(line1.get_ydata(), line[0]))
        line2.set_xdata(numpy.append(line2.get_xdata(), k))
        line2.set_ydata(numpy.append(line2.get_ydata(), line[1]))
    axe.relim()
    axe.autoscale_view()
    figure.canvas.draw()
    figure.canvas.flush_events()
    log.debug("Env set")
    UpperQagent = QAgent.QAgentUpper(dbmgr)
    LowerQagent = QAgent.QAgentLower(dbmgr)
    agent = LowerQagent
    log.debug("Agent set")
    state = env.state
    action, greedy_action = agent.policy(state)
    log.info("Starting")
    i=0
    airtime = 0; max_airtime=0
    follow_reward = 0
    j = 0
    try:
        while True:
            while i < 150: 
                log.debug("State: {0}".format(state))
                log.debug("Action: {0}".format(action))
                Q = agent.getQ(state,action) #store Q(s,a)
                log.debug("Stored Q: {0}".format(Q))
                env.take_action(action) # move motor, update env.reward, update env.state
                log.debug("Action taken")
                while env.read_serial():
                    pass
                new_state, isUpper = env.get_state()
                log.debug("New State: {0}".format(state))
                if new_state < 9 and new_state >= 8:
                    airtime += 1
                    if airtime > max_airtime:
                        max_airtime = airtime
                else : airtime = 0

                if isUpper:
                    new_agent = UpperQagent
                else: 
                    new_agent = LowerQagent

                R = env.get_reward()
                follow_reward += R
                new_action, greedy_action = new_agent.policy(new_state)
                log.debug("Reward: {0}".format(R))
                i += 1
                target = R + GAMMA*new_agent.getQ(new_state, greedy_action)
                newQ = Q + ALPHA*(target-Q)
                log.debug("New Q: {0}".format(newQ))
                agent.setQ(state, action, newQ)
                log.debug("New Q set")
                log.debug("-----------------")
                state = new_state
                agent = new_agent
                action = new_action
            log.info("Pause Started")
            log.info("AIRTIME : {0}".format(max_airtime))
            follow_reward = follow_reward / 100
            f = open('recompense_moyenne.data', 'a')
            f.write(str(follow_reward) + ":" + str(max_airtime) + "\n")
            f.close()
            line1.set_xdata(numpy.append(line1.get_xdata(), k))
            line1.set_ydata(numpy.append(line1.get_ydata(), follow_reward))
            line2.set_xdata(numpy.append(line2.get_xdata(), k))
            line2.set_ydata(numpy.append(line2.get_ydata(), max_airtime))
            axe.relim()
            axe.autoscale_view()
            figure.canvas.draw()
            figure.canvas.flush_events()
            k += 1
            j += 1
            log.info("Follow reward : {0}".format(follow_reward))
            follow_reward = 0
            max_airtime = 0
            agent = LowerQagent
            action, greedy_action = agent.policy(state)
            new_state, isUpper = env.get_state()
            time.sleep(float(parser.get('Main', 'PauseDuration')))
            epsilon = (float(parser.get('Coeffs', 'epsilon'))* 0.998) // 0.0001 * 0.0001
            LowerQagent.epsilon = epsilon
            UpperQagent.epsilon = epsilon * 1.5
            parser.set('Coeffs', 'epsilon', str(agent.epsilon))
            parser.write(open('config.ini','w'))
            i = 0
            log.info("Pause Ended")
    except KeyboardInterrupt:
        log.info("All ended")
        dbmgr.release()
        exit()
        
# ******************
# *** Global Var ***
# ******************

# Config
parser = SafeConfigParser()
parser.read('config.ini')

#Log
log = logging.getLogger('root')
log.setLevel(getLogLevel())
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(getLogLevel())
formatter = logging.Formatter('[%(asctime)s] %(levelname)8s %(module)15s: %(message)s')
stream.setFormatter(formatter)
log.addHandler(stream)
file_handler = RotatingFileHandler('debug.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
log.addHandler(file_handler)

#DbManager
db_name = parser.get('Main', 'DbName')

#Coeffs
GAMMA = float(parser.get('Coeffs', 'GAMMA'))
ALPHA = float(parser.get('Coeffs', 'ALPHA'))

#sys.excepthook = general_debug

plt.ion()

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__":
    main()