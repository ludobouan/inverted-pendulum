# ********************************
# @author     : Ludovic Bouan
# @contact    : ludo.bouan@gmail.com
# created on  :
# last mod    :
# title       :
# to do       :
# ********************************

# *******************
# ***** Imports *****
# *******************

import os
import sys
import time

import QAgent
import enviroment
import dbmanager

import pdb
import logging
from ConfigParser import SafeConfigParser
# ******************
# *** Global Var ***
# ******************

from logging.handlers import RotatingFileHandler

log = logging.getLogger('root')
log.setLevel(logging.DEBUG)

stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] %(levelname)8s %(module)15s: %(message)s')
stream.setFormatter(formatter)

log.addHandler(stream)

file_handler = RotatingFileHandler('debug.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

log.addHandler(file_handler)
log.debug("Initialisation de la connexion Serial")


dbmgr = dbmanager.DbManager('Qdatabase.db')


parser = SafeConfigParser()
parser.read('config.ini')

GAMMA = float(parser.get('Coeffs', 'GAMMA'))
ALPHA = float(parser.get('Coeffs', 'ALPHA'))
# *******************
# ***** CLasses *****
# *******************

# *******************
# **** Functions ****
# *******************
def main():
    env = enviroment.env()
    log.debug("env set")
    agent = QAgent.QAgent()
    log.debug("agent set")
    S = env.state
    log.debug("Lancement")
    i=0
    airtime = 0; max_airtime=0
    try:
        while True:
             while i < 500:
                 a = agent.policy(S) #choose action (nombre)
                 #log.debug("State: {0}".format(S))
                 #log.debug("Action: {0}".format(a))
                 Q = agent.getQ(S,a) #store Q(s,a)
                 #log.debug("Stored Q: {0}".format(Q))
                 env.take_action(a) # move motor, update env.reward, update env.state
                 #log.debug("Action taken")
                 while env.read_serial():
                    pass
                 S2 = env.get_state()
                 #log.debug("New State: {0}".format(S))

                 if S2 < 1 and S2 > -1:
                    airtime += 1
                    if airtime > max_airtime:
                        max_airtime = airtime
                 else : airtime = 0

                 R = env.get_reward()
                 #log.debug("Reward: {0}".format(R))
                 i += 1
                 target = R + GAMMA*max([agent.getQ(S2, i_act) for i_act in agent.action_list])
                 newQ = Q + ALPHA*(target - Q)
                 #log.debug("New Q: {0}".format(newQ))
                 agent.setQ(S, a, newQ)
                 #log.debug("new Q set")
                 #log.debug("-----------------")
                 S=S2
             log.debug("Debut de la pause")
             log.info("AIRTIME : {0}".format(max_airtime))
             max_airtime = 0
             parser.set('Progress', 'max_airtime', str(max_airtime))
             time.sleep(45)
             agent.epsilon = float(parser.get('Coeffs', 'EPSILON'))*0.95
             parser.set('Coeffs', 'EPSILON', str(agent.epsilon))
             i = 0
             log.debug("Fin de la pause")
    except KeyboardInterrupt:
        dbmgr.release()
        exit()

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__":
    main()