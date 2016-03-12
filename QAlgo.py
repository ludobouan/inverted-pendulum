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
def update_values(episode_record, agent, a_StateActionPairs):
    E_dict = {}
    Q_dict = agent.getAllQ()
    for s,a in a_StateActionPairs:
        E_dict[str(s) + str(a)] = 0
    for i_r in episode_record:
        state, action, new_state, new_action, greedy_action, R = i_r

        Q = Q_dict[str(state) + ":" + str(action)]
        target = R + GAMMA*Q_dict[str(new_state) + ":" + str(greedy_action)]
        E_dict[str(state) + str(action)] += 1
        for s,a in a_StateActionPairs:
            updatedQ = Q_dict[str(s) + ":" + str(a)]+ALPHA*E_dict[str(s) + str(a)]*(target-Q)
            Q_dict[str(s) + ":" + str(a)] = updatedQ
            if greedy_action == new_action:
                E_dict[str(s) + str(a)] *= GAMMA*LAMBDA
            else: 
                E_dict[str(s) + str(a)] = 0
    agent.setAllQ(Q_dict)
    log.info('Qvalues updated')


def getLogLevel():
    loglevel = parser.get('Main', 'LogLevel')
    if loglevel == "DEBUG": return logging.DEBUG
    if loglevel == "INFO": return logging.INFO
    if loglevel == "ERROR": return logging.ERROR
        
def general_debug(type, value, traceback):
    log.error("Error : " + str(type) + " - " + str(value))

def main():
    #Connect to (or create) database
    log.debug(os.path.isfile(db_name))
    if not os.path.isfile(db_name):
        dbmgr = DbManager.DbManager(db_name)
        dbmgr.createDb('schema.sql')
        log.info("Database created")
    else:
        dbmgr = DbManager.DbManager(db_name)

    # Setup enviroment and agents
    env         = enviroment.env()
    UpperQagent = QAgent.QAgentUpper(dbmgr)
    LowerQagent = QAgent.QAgentLower(dbmgr)
    log.debug("Env set")
    log.debug("Agent set")

    # Initial conditions
    agent          = LowerQagent
    state          = env.state
    airtime        = 0
    max_airtime    = 0
    follow_reward  = 0
    step           = 0
    episode_record = []
    LowerQagent.get_policy()
    UpperQagent.get_policy()
    StateActionPairs = agent.getStateActionPairs()
    action, greedy_action = agent.policy(state)
    pause_time = float(parser.get('Main', 'PauseDuration'))
    max_steps  = float(parser.get('Main', 'max_steps'))
    log.info("Starting")
    try:
        while True:
            while step < max_steps: 
                log.debug("State: {0}".format(state))
                log.debug("Action: {0}".format(action))

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
                if new_state < 10 and new_state >= 7:
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
                # Record
                episode_record.append((state, action, new_state, new_action, greedy_action, R))

                # Update variables
                state  = new_state
                agent  = new_agent
                action = new_action
                step   += 1

            ### ENTER PAUSE (every `max_steps` steps) ###
            log.info("Pause Started")
            log.info("AIRTIME : {0}".format(max_airtime))

            # Averge reward: calculate, save
            follow_reward = follow_reward / max_steps
            f = open('recompense_moyenne.data', 'a')
            f.write(str(follow_reward) + ":" + str(max_airtime) + "\n")
            f.close()

            log.info("Follow reward : {0}".format(follow_reward))
            follow_reward = 0
            max_airtime   = 0

            # Reset and prepare next episode
            agent = LowerQagent
            state = 0.0
            action, greedy_action = agent.policy(state)

            epsilon = (float(parser.get('Coeffs', 'epsilon'))* 0.998) // 0.0001 * 0.0001
            LowerQagent.epsilon = epsilon
            UpperQagent.epsilon = epsilon * 1.5
            parser.set('Coeffs', 'epsilon', str(agent.epsilon))
            parser.write(open('config.ini','w'))

            # Update Q and policies
            update_values(episode_record, agent, StateActionPairs)
            LowerQagent.get_policy()
            UpperQagent.get_policy()
            
            # Delay 
            time.sleep(pause_time)

            step = 0
            record = []
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
LAMBDA = 0.4

#sys.excepthook = general_debug

#plt.ion()

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__":
    main()