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
    #Connect to database
    log.debug(os.path.isfile(db_name))
    if not os.path.isfile(db_name):
        dbmgr = DbManager.DbManager(db_name)
        dbmgr.createDb('schema.sql')
        log.info("Database created")
    else:
        dbmgr = DbManager.DbManager(db_name)

    # Setup Graphing
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

    # Setup enviroment and agents
    env = enviroment.env()
    UpperQagent = QAgent.QAgentUpper(dbmgr)
    LowerQagent = QAgent.QAgentLower(dbmgr)

    # Initial conditions
    agent = LowerQagent
    state = env.state
    action, greedy_action = agent.policy(state)
    log.debug("Agent set")
    airtime = 0
    max_airtime=0
    follow_reward = 0
    j = 0
    i=0
    log.info("Starting")
    try:
        while True:
            while i < 150: 
                log.debug("State: {0}".format(state))
                log.debug("Action: {0}".format(action))
                
                # Get Q from state-action pair
                Q = agent.getQ(state,action)
                log.debug("Stored Q: {0}".format(Q))

                # Take Action - move motor
                env.take_action(action) 
                log.debug("Action taken")
                
                # Wait for motor to finish turing (anticipated)
                while env.read_serial():
                    pass

                # Get new state and reward
                new_state, isUpper = env.get_state()
                R = env.get_reward()
                log.debug("New State: {0}".format(state))
                log.debug("Reward: {0}".format(R))

                # Update follow_reward and airtime
                follow_reward += R
                if new_state < 9 and new_state >= 8:
                    airtime += 1
                    if airtime > max_airtime:
                        max_airtime = airtime
                else : airtime = 0

                # Choose upper or lower agent based on state
                if isUpper:
                    new_agent = UpperQagent
                else: 
                    new_agent = LowerQagent

                # Choose new action and theoretical greedy action 
                new_action, greedy_action = new_agent.policy(new_state)
                log.debug("Reward: {0}".format(R))
                
                # Update Q value according to Q value iteration update 
                target = R + GAMMA*new_agent.getQ(new_state, greedy_action)
                newQ = Q + ALPHA*(target-Q)
                
                log.debug("New Q: {0}".format(newQ))
                agent.setQ(state, action, newQ)
                log.debug("New Q set")
                log.debug("-----------------")

                #Update variables
                state = new_state
                agent = new_agent
                action = new_action
                i += 1

            ### ENTER PAUSE (every 150 steps) ###
            log.info("Pause Started")
            log.info("AIRTIME : {0}".format(max_airtime))

            # Averge reward: calculate, save, and graph
            follow_reward = follow_reward / 150
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

            # Reset and prepare next episode
            agent = LowerQagent
            action, greedy_action = agent.policy(state)
            new_state, isUpper = env.get_state()

            epsilon = (float(parser.get('Coeffs', 'epsilon'))* 0.998) // 0.0001 * 0.0001
            LowerQagent.epsilon = epsilon
            UpperQagent.epsilon = epsilon * 1.5
            parser.set('Coeffs', 'epsilon', str(agent.epsilon))
            parser.write(open('config.ini','w'))
            
            # Delay 
            time.sleep(float(parser.get('Main', 'PauseDuration')))

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