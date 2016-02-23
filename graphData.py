import matplotlib.pyplot as plt

f = open('recompense_moyene.data', 'r')
lines = f.read().split()
f.close()
reward = []
x = []
airtime = []
i = 0
for line in lines:
    i += 1
    line = line.split(":")
    x.append(i)
    reward.append(line[0])
    airtime.append(line[1])
plt.plot(x, airtime)
plt.plot(x, reward)
plt.show()