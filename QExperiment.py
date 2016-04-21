# *******************
# ***** Imports *****
# *******************

import QEnvironment
import QAgent
import time

# *******************
# *****  Class  *****
# *******************

class QExperiment():
	def __init__(self, a_dbmgr, a_name, a_log, a_pfreezed):
		self.dbmgr = a_dbmgr
		self.name = a_name
		experiment = a_dbmgr.query("SELECT * FROM Experiments WHERE Name = {0}".format("'" + a_name + "'")).fetchone()
		self.simulation = experiment[2]
		self.nbr_episode = experiment[3]
		self.nbr_step = experiment[4]
		self.pause_time = experiment[5]
		self.current_episode = experiment[6]
		self.steprate = experiment[7]
		self.regression = experiment[8]
		self.environment = QEnvironment.QEnvironment(a_log, self.simulation)
		if self.environment.connexion is None:
			self.connected = False
		else:
			self.connected = True
			self.log = a_log
			self.agent = QAgent.QAgent(a_dbmgr, a_log, experiment[1], self.regression, a_pfreezed)
			self.policy_freezed = a_pfreezed

	def start_episode(self, a_clear):
		if self.connected:
			try:			
				self.environment.init_episode()
				time.sleep(3)
				state_action_list = []
				reward = 0
				if self.steprate == 0:
					self.environment.lock_message(True)
				else:
					self.environment.lock_message(False)
				state = self.agent.get_state(self.environment.get_state())
				action, greedy_action = self.agent.get_policy(state)
				total_reward = 0
				step_record = []
				for i in range(self.nbr_step):
					self.environment.take_action(action)
					if self.steprate > 0:
						time.sleep(0.001 * self.steprate)
					reward = self.agent.get_reward(state)
					total_reward += reward
					new_state = self.agent.get_state(self.environment.get_state())
					new_action, greedy_action = self.agent.get_policy(new_state)
					step_record.append((state, action, new_state, new_action, greedy_action, reward))
					state  = new_state
					action = new_action
				average_reward = total_reward / self.nbr_step
			except KeyboardInterrupt:
				print("Episode manually stopped")
				return True
			except AttributeError:
				print("Episode critically stopped")
				return True
			else:
				airtime = self.evaluate_airtime(step_record)
				self.log.info("Episode finished")
				self.log.info("Air time : {0}".format(airtime))
				self.log.info("Average Reward : {0}".format(average_reward))
				if not self.policy_freezed:
					self.agent.learn_policy(step_record)
					self.agent.epsilon_discount()
					self.current_episode += 1
					self.dbmgr.query("UPDATE Experiments SET Current_episode = {0} WHERE Name = {1}".format(self.current_episode, "'" + str(self.name) + "'"))
					self.dbmgr.query("INSERT INTO Results (Agent, Episode, Air_time, Average_reward) VALUES ({0}, {1}, {2}, {3})".format("'" + self.agent.name + "'", self.current_episode, airtime, average_reward))
				return False
		else:
			self.log.error("System not connected")

	def isEnded(self):
		if self.current_episode == self.nbr_episode:
			return True
		else:
			return False

	def take_pause(self):
		time.sleep(self.pause_time)

	def evaluate_airtime(self, a_state_action_list):
		airtime = 0
		max_airtime = 0
		for state_action in a_state_action_list:
			if (abs(float(state_action[0][0].split(":")[0]) + float(state_action[0][0].split(":")[1])) / 2) < 20 :
				airtime += 1
				if airtime > max_airtime:
					max_airtime = airtime
			else:
				airtime = 0
		return max_airtime

