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
import time
import DbManager
import logging
import sys
import QAgent
import enviroment
import pdb
from logging.handlers import RotatingFileHandler

# ******************
# *** Global Var ***
# ******************
acts = [-20, -10, 0, 10, 20]
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

dbmgr = DbManager.dbManager("testdb.db")
agent = QAgent.QAgent(acts)
log.debug("Initialisation de la connexion Serial")
env = enviroment.env(acts)
ALPHA = 0.6 #learning rate
GAMMA = 0.9 #discount factor

# *******************
# ***** CLasses *****
# *******************

# *******************
# **** Functions ****
# *******************
def main():
    agent = QAgent.QAgent([-20,-10,0,10,20])
    S = env.state
    log.debug("Lancement")
    i = 0
    try:
        while True:
             while i < 1000:
                 a = agent.policy(S)
                 Q = agent.getQ(S,a) #store Q(s,a)
                 env.take_action(a) # move motor, update env.reward, update env.state
                 time.sleep(0.02)
                 S = env.get_state()
                 R = env.get_reward()
                 i += 1
                 target = R + GAMMA*max([agent.getQ(S, a) for a in agent.actions])
                 newQ = Q + ALPHA*(target - Q)
                 agent.setQ(S, a, newQ)
             log.debug("Debut de la pause")
             time.sleep(60)
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