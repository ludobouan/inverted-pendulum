import matplotlib.pyplot as plt
import DbManager
import QAgent

acts = [-20, -10, 0, 10, 20]

dbmgr = DbManager.dbManager("testdb.db")
agent = QAgent.QAgent(acts)

dic = {0:"Action1", 1:"Action2", 2:"Action3", 3:"Action4", 4:"Action5"}

L={'Action1':[[],[]], 'Action2': [[],[]], 'Action3': [[],[]], 'Action4': [[],[]], 'Action5': [[],[]]}
for i in range(-10,10):
    for j in range(-20,20):
        s = i + (j+20)*0.01
        P = [agent.getQ(s, a) for a in agent.actions]
        mx=0
        for k in range(4):
            if P[k] > P[mx]:
                mx = k 
        L[dic[mx]][0].append(i)
        L[dic[mx]][1].append(j)

plt.plot(L['Action1'][0], L['Action1'][1], 'ro')
plt.plot(L['Action2'][0], L['Action2'][1], 'ro')
plt.plot(L['Action3'][0], L['Action3'][1], 'go')
plt.plot(L['Action4'][0], L['Action4'][1], 'bo')
plt.plot(L['Action5'][0], L['Action5'][1], 'bo')
plt.show()