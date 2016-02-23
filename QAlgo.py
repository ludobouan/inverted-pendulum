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

import QAgent
import enviroment
import DbManager

import logging
from configparser import SafeConfigParser
from logging.handlers import RotatingFileHandler


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
        dbmgr.createDb('schema_1.sql', 'schema_2.sql')
        log.info("Database created")
    else:
        dbmgr = DbManager.DbManager(db_name)

    env = enviroment.env()
    log.debug("Env set")
    LowerAgent = QAgent.LowerQAgent(dbmgr)
    UpperAgent = QAgent.UpperQAgent(dbmgr)
    log.debug("Agents set")
    S = env.state
    agent = LowerAgent
    a = agent.policy(S)[0] #choose action (nombre)
    log.info("Starting")
    i=0
    follow_reward = 0
    list_reward = []
    airtime = 0; max_airtime=0
    epsilon = float(parser.get('Coeffs', 'epsilon'))
    try:
        while True:
            while i < 100:
                
                Q = agent.getQ(S,a) #store Q(s,a)
                log.debug("State: {0}".format(S))
                log.debug("Action: {0}".format(a))
                log.debug("Stored Q: {0}".format(Q))

                env.take_action(a) # move motor, update env.reward, update env.state
                log.debug("Action taken")

                while env.read_serial():
                    pass
                new_state, isUpper = env.get_state()
                if isUpper == True:
                    new_agent = UpperAgent
                else:
                    new_agent = LowerAgent
                log.debug("New State: {0}".format(S))
                if new_state < 1 and new_state > -1:
                    airtime += 1
                    if airtime > max_airtime:
                        max_airtime = airtime
                else : airtime = 0

                R = env.get_reward()
                follow_reward += R
                new_action, greedy_action = new_agent.policy(new_state)
                log.debug("Reward: {0}".format(R))

                i += 1

                target = R + GAMMA*new_agent.getQ(new_state, greedy_action)
                
                newQ = Q + ALPHA*(target-Q)
                agent.setQ(S, a, newQ)

                log.debug("New Qs set")
                log.debug("-----------------")
                S = new_state
                a = new_action
                agent = new_agent
            log.info("Pause Started")
            log.info("AIRTIME : {0}".format(max_airtime))
            follow_reward = follow_reward / 100
            f = open('recompense_moyene.data', 'a')
            f.write(str(follow_reward) + ":" + str(max_airtime) + "\n")
            f.close()
            log.info("Follow reward : {0}".format(follow_reward))
            follow_reward = 0
            max_airtime = 0
            time.sleep(float(parser.get('Main', 'PauseDuration')))
            epsilon *= 0.99
            LowerAgent.epsilon = epsilon
            UpperAgent.epsilon = epsilon
            parser.set('Coeffs', 'epsilon', str(epsilon))
            i = 0
            log.info("Pause Ended")
    except KeyboardInterrupt:
        dbmgr.release()
        f.close()
        log.info("All ended")
        
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
GAMMA = float(parser.get('Coeffs', 'gamma'))
ALPHA = float(parser.get('Coeffs', 'alpha'))

sys.excepthook = general_debug

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__":
    main()