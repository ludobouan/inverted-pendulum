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

# ******************
# *** Global Var ***
# ******************
log = logging.getLogger('root')
log.setLevel(logging.DEBUG)

stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] %(levelname)8s %(module)15s: %(message)s')
stream.setFormatter(formatter)

log.addHandler(stream)

dbmgr = DbManager.DbManager("testdb.db")
agent = QAgent.QAgent([-2, -1, 0, 1, 2])

ALPHA = 0.5 #learning rate
GAMMA = 0.5 #discount factor

# *******************
# ***** CLasses *****
# *******************

# *******************
# **** Functions ****
# *******************
def main():
    S = env.state
    while True:
        a = agent.policy(S)
        Q = getQ(S,a) #store Q(s,a)

        env.TakeAction(a) # move motor, update env.reward, update env.state
        ##TIMESLEEP SHOULD BE HERE, no ?
        S = env.state
        R = env.reward

        target = R + GAMMA*max([getQ(S, a) for a in agent.actions])
        newQ = Q + ALPHA*(target - Q)

        dbmgr.setQ(S, a, newQ)

        time.sleep(0.05)

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__":
    main()