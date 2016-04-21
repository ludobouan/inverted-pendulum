# ********************************
# @author     : Ludovic Bouan & Thomas Lefort 
# @contact    : ludo.bouan@gmail.com / thomas.lefort@ecam.fr
# title       : Inverted Pendulum / Q-Learning
# ********************************

# *******************
# ***** Imports *****
# *******************

import QAgent
import QEnvironment
import QExperiment
import DbManager

import os
import platform
import logging
import sys
import time
import datetime

from logging.handlers import RotatingFileHandler
import matplotlib.pyplot as plt

# *******************
# **** Functions ****
# *******************

def general_debug(type, value, traceback):
	print("Error : " + str(type) + " - " + str(value))

def main():
	#Initialize functions
	#sys.excepthook = general_debug
	debug = False
	close = False
	if platform.system() == "Linux" or platform.system() == "Darwin":
		clear = lambda: os.system('clear')
	elif platform.system() == "Windows":
		clear = lambda: os.system('cls')
	else:
		clear = lambda: True
	clear()
	log, logstream = init_log()
	datamanager = init_db(log)
	while not close:
		print("---------- Rotary Inverted Pendulum - Reinforced Learning ----------")
		print("1. Create Agent ")
		print("2. Show Agent ")
		print("3. Create Experiment ")
		print("4. Start Learning ")
		print("5. Evaluate Policy ")
		print("6. Evaluate Physical System ")
		print("7. Show and Save Results ")
		if debug:
			print("8. Disable Debug ")
		else:
			print("8. Enable Debug ")
		print("0. Close ")
		choice = input("Choice : ")
		clear()
		try:
			choice = int(choice)
		except ValueError:
			print("Invalid Selection")
		else:
			if choice == 1:
				create_agent(clear, datamanager)
			elif choice == 2:
				show_agent(clear, datamanager)
			elif choice == 3:
				create_experiment(clear, datamanager)
			elif choice == 4:
				start_learning(log, clear, datamanager)
			elif choice == 5:
				evaluate_policy(log, clear, datamanager)
			elif choice == 6:
				evaluate_system(log, clear, datamanager)
			elif choice == 7:
				show_results(log, clear, datamanager)
			elif choice == 8:
				if debug == True:
					debug = False
					log.setLevel(logging.DEBUG)
				else:
					debug = True
					log.setLevel(logging.INFO)
			elif choice == 0:
				close = True
				print("Program ended correctly")
			else:
				print("Invalid Selection")
	exit()
	datamanager.release()

def create_agent(a_clear, a_dbmgr):
	print("---------- Create Agent ----------")
	a_name = get_value("Name : ", "String")
	rep = a_dbmgr.query("SELECT * FROM Agents WHERE Name = {0}".format("'" + a_name + "'")).fetchall()
	if len(rep) > 0:
		a_clear()
		print("Agent name already exist !")
	else:
		note = get_value("Description : ", "String")
		epsilon = get_value("Epsilon (Learning Rate) : ", "Float")
		gamma = get_value("Gamma (Discount Factor) : ", "Float")
		alpha = get_value("Alpha : ", "Float")
		beta = get_value("Beta (Eligibility Trace) : ", "Float")
		epsilon_discount = get_value("Epsilon Discount : ", "Float")
		two_agent = get_value("Two Agent (Y or N) : ", "Bool")
		eligibility = get_value("Eligibility Trace (Y or N) : ", "Bool")
		nbr_angle = get_value("Number of Angle : ", "Int")
		nbr_speed = get_value("Number of Speed : ", "Int")
		nbr_action = get_value("Number of Action : ", "Int")

		list_speed = []
		print("Enter speed interval in this form min_value:max_value")
		for i in range(nbr_speed):
			speed = get_value("Speed Interval : ", "Speed")
			list_speed.append(speed)


		print("Enter angle interval in this form min_value:max_value:isUpper(Y or N):Reward")
		list_states = []
		i = 0
		for i in range(nbr_angle):
			angle = get_value("Angle Interval : ", "Angle")
			if two_agent == False:
				angle[2] = False
			for speed in list_speed:
				list_states.append((str(angle[0]) + ":" + str(angle[1]) + ":" + str(speed[0]) + ":" + str(speed[1]), angle[2], angle[3]))
			

		print("Enter action in this form Value:isUpper(Y or N)")
		i = 0
		list_actions = []
		while i < nbr_action:
			action = get_value("Action : ", "Action")
			list_actions.append(action)
			i += 1

		a_dbmgr.query("INSERT INTO Agents (Name, Note, Epsilon, Gamma, Alpha, TwoAgent, Creation_date, Eligibility, Beta, Epsilon_d) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9})".format("'" + a_name + "'", "'" + note +"'" , epsilon, gamma, alpha, "'" + str(two_agent) + "'" , time.time(), "'" + str(eligibility) + "'", beta, epsilon_discount))
		for state in list_states:
			a_dbmgr.query("INSERT INTO States (Agent, Value, isUpper, Reward) VALUES ({0}, {1}, {2}, {3})".format("'" + a_name + "'", "'" + str(state[0]) + "'", "'" + str(state[1]) + "'", state[2]))
			for action in list_actions:
				a_dbmgr.query("INSERT INTO QValues (Agent, State, Action, Value) VALUES ({1}, {2}, {3}, {0})".format(0, "'" + a_name + "'", "'" + str(state[0]) + "'", "'" + action[0] + "'"))
		for action in list_actions:
			a_dbmgr.query("INSERT INTO Actions (Agent, Value, isUpper) VALUES ({0}, {1}, {2})".format("'" + a_name + "'", action[0], "'" + action[1] + "'"))
		a_clear()
		print("Agent created !")

def show_agent(a_clear, a_dbmgr):
	print("---------- Show Agent ----------")
	list_agent = a_dbmgr.query("SELECT * FROM Agents").fetchall()
	if len(list_agent) > 0:
		i = 0
		for agent in list_agent:
			date = datetime.datetime.fromtimestamp(int(agent[1])).strftime('%d-%m-%Y %H:%M:%S')
			print("{0}. {1} : {2} - {3}".format(i, agent[0], date, agent[2]))
			i += 1
		choice = input("Choice : ")
		try:
			choice = list_agent[int(choice)]
			a_clear()
		except ValueError:
			print("Error in selection")
		except IndexError:
			print("Error in selection")
		else:
			print("Name : {0}".format(choice[0]))
			date = datetime.datetime.fromtimestamp(int(choice[1])).strftime('%d-%m-%Y %H:%M:%S')
			print("Creation Date : {0}".format(date))
			print("Note : {0}".format(choice[2]))
			print("Epsilon : {0}".format(choice[3]))
			print("Gamma : {0}".format(choice[4]))
			print("Alpha : {0}".format(choice[5]))
			print("Beta : {0}".format(choice[6]))
			print("Epsilon Discount : {0}".format(choice[7]))
			print("TwoAgent : {0}".format(choice[8]))
			print("Eligibility : {0}".format(choice[9]))
	else:
		print("No Agent created")

def start_learning(a_log, a_clear, a_dbmgr):
	print("---------- Start Learning ----------")
	list_experiment = a_dbmgr.query("SELECT * FROM Experiments").fetchall()
	i = 0
	for experiment in list_experiment:
		print("{0}. {1} : {2} - {3} - {4} - {5} - {6}".format(i, experiment[0], experiment[2], experiment[3], experiment[4], experiment[5], experiment[6]))
		i += 1
	choice = input("Choice : ")
	try:
		choice = list_experiment[int(choice)]
		a_clear()
	except ValueError:
		print("Error in selection")
	except IndexError:
		print("Error in selection")
	else:
		experiment = QExperiment.QExperiment(a_dbmgr, choice[0], a_log, False)
		a_log.debug("Experiment loaded")
		if experiment.connected == True:
			a_log.info("Starting learning phase")
			stop = False
			while not stop:
				stop = experiment.start_episode(a_clear)
				if experiment.isEnded() or stop:
					stop = True
				else:
					try:
						a_log.info("Episode ended. Pause Begin")
						experiment.take_pause()
					except KeyboardInterrupt:
						print("Learning stop Manually")

def evaluate_policy(a_log, a_clear, a_dbmgr):
	print("---------- Evaluate Policy ----------")
	nbr_episode = get_value("Number of episode : ", "Int")
	pause = get_value("Pause Time : ", "Int")
	list_experiment = a_dbmgr.query("SELECT * FROM Experiments").fetchall()
	i = 0
	for experiment in list_experiment:
		print("{0}. {1} : {2} - {3} - {4} - {5}".format(i, experiment[0], experiment[3], experiment[4], experiment[5], experiment[6]))
		i += 1
	choice = input("Choice : ")
	try:
		choice = int(choice)
	except ValueError:
		print("Error in selection")
	else:
		experiment = QExperiment.QExperiment(a_dbmgr, list_experiment[choice][0], a_log, True)
		if experiment.connected == True:
			a_log.info("Starting policy evaluation")
			for i in range(nbr_episode):
				experiment.start_episode(a_clear)
				time.sleep(pause)

def evaluate_system(a_log, a_clear, a_dbmgr):
	print("---------- Evaluate Physical System ----------")
	environment = QEnvironment.QEnvironment(a_log, "False")
	if environment.connexion is None:
		a_clear()
		print("Can't evaluate system if not connected")
	else:
		repetition = get_value("Number of episode : ", "Int")
		actions = get_value("Actions : ", "ListFloat")
		blocked = get_value("Blocked (Y or N) : ", "Bool")
		pause = get_value("Pause Time : ", "Int")
		environment.lock_message(blocked)
		try:
			for i in range(repetition):
				x = []
				states = []
				j = 0
				environment.init_episode()
				for action in actions:
					environment.take_action(action)
					states.append(abs(float(environment.get_state().split(":")[0])))
					x.append(j)
					j += 1
				plt.plot(x, states)
				time.sleep(pause)
			plt.show()
			a_clear() 
		except KeyboardInterrupt:
			print("System stopped Manually")

def show_results(a_log, a_clear, a_dbmgr):
	print("---------- Show Results ----------")
	list_agent = a_dbmgr.query("SELECT * FROM Agents").fetchall()
	if len(list_agent) > 0:
		i = 0
		for agent in list_agent:
			date = datetime.datetime.fromtimestamp(int(agent[1])).strftime('%d-%m-%Y %H:%M:%S')
			print("{0}. {1} : {2} - {3}".format(i, agent[0], date, agent[2]))
			i += 1
		choice = get_value("Choice : ", "Int")
		try:
			agent_name = list_agent[choice][0]
		except IndexError:
			print("Error in selection")
		else:
			data = a_dbmgr.query("SELECT * FROM Results WHERE Agent = {0}".format("'" + agent_name + "'")).fetchall()
			if len(data) > 0:
				step = []
				airtime = []
				reward = []
				for element in data:
					step.append(element[1])
					airtime.append(element[2])
					reward.append(element[3])
				plt.plot(step, reward)
				plt.plot(step, airtime)
				plt.show()
				a_clear()
			else:
				a_clear()
				print("No data available")
	else:
		print("Create an agent first")


def create_experiment(a_clear, a_dbmgr):
	print("---------- Create Experiment ----------")	
	list_agent = a_dbmgr.query("SELECT * FROM Agents").fetchall()
	if len(list_agent) > 0:
		name = get_value("Name : ", "String")
		list_experiment = a_dbmgr.query("SELECT * FROM Experiments WHERE Name = {0}".format("'" + name + "'")).fetchall()
		if len(list_experiment) > 0:
			print("Experiment name already exist")
		else:
			i = 0
			for agent in list_agent:
				date = datetime.datetime.fromtimestamp(int(agent[1])).strftime('%d-%m-%Y %H:%M:%S')
				print("{0}. {1} : {2} - {3}".format(i, agent[0], date, agent[2]))
				i += 1
			choice = get_value("Choice : ", "Int")
			try:
				agent_name = list_agent[choice][0]
			except IndexError:
				print("Error in selection")
			else:
				simulation = get_value("Y:Simulation   N:Physical System : ", "Bool")
				episode = get_value("Number of episodes : ", "Int")
				step_by_episode = get_value("Number of step by episode : ", "Int")
				steprate = get_value("Time between steps (ms) (0 : waiting end of move) : ", "Int")
				pause_time = get_value("Pause Time : ", "Int")
				a_clear()
				a_dbmgr.query("INSERT INTO Experiments (Name, Agent, Simulation, Nbr_episode, Nbr_step, Pause_time, Current_episode, StepRate) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, 0, {6})".format("'" + name + "'","'" + agent_name + "'", "'" + str(simulation) + "'", episode, step_by_episode, pause_time, steprate))
				print("Experiment created !")
	else:
		print("Create an agent first")

def init_log():
	log = logging.getLogger('root')
	log.setLevel(logging.INFO)
	stream = logging.StreamHandler(sys.stdout)
	stream.setLevel(logging.INFO)
	formatter = logging.Formatter('[%(asctime)s] %(levelname)8s %(module)15s: %(message)s')
	stream.setFormatter(formatter)
	log.addHandler(stream)
	file_handler = RotatingFileHandler('debug.log', 'a', 1000000, 1)
	file_handler.setLevel(logging.INFO)
	file_handler.setFormatter(formatter)
	log.addHandler(file_handler)
	return log, stream

def init_db(a_log):
	if not os.path.isfile("Database.db"):
		dbmgr = DbManager.DbManager("Database.db", a_log)
		dbmgr.create_database('schema.sql')
		a_log.info("Database created")
	else:
		dbmgr = DbManager.DbManager("Database.db", a_log)
	return dbmgr

def get_value(a_text, a_type):
	done = False
	while not done:
		value = input(a_text)
		if a_type == "Float":
			try:
				value = float(value)
			except ValueError:
				print("You need to type a float.")
			else:
				done = True
		elif a_type == "String":
			done = True
		elif a_type == "Bool":
			if value == "Y":
				done = True
				value = True
			elif value == "N":
				done = True
				value = False
			else:
				print("You need to type Y or N")
		elif a_type == "Action":
			list_value = value.split(":")
			try:
				value = []
				value.append(float(list_value[0]))
				if list_value[1] == "Y":
					value.append(True)
				elif list_value[1] == "N":
					value.append(False)
				else:
					raise ValueError()
			except ValueError:
				print("Input doesn't match with an action")
			else:
				done = True
				value = list_value
		elif a_type == "Int":
			try:
				value = int(value)
			except ValueError:
				print("You need to type an integer.")
			else:
				done = True
		elif a_type == "Angle":
			list_value = value.split(":")
			try:
				value = []
				value.append(float(list_value[0]))
				value.append(float(list_value[1]))
				if list_value[2] == "Y":
					value.append(True)
				elif list_value[2] == "N":
					value.append(False)
				else:
					raise ValueError()
				value.append(float(list_value[3]))
			except ValueError:
				print("Input doesn't match with an angle")
			except IndexError:
				print("Input doesn't match with an angle")
			else:
				done = True
		elif a_type == "Speed":
			list_value = value.split(":")
			try:
				value = []
				value.append(float(list_value[0]))
				value.append(float(list_value[1]))
			except ValueError:
				print("Input doesn't match with a speed")
			except IndexError:
				print("Input doesn't match with a speed")
			else:
				done = True
		elif a_type == "ListFloat":
			list_value = value.split(":")
			try:
				value = []
				for action in list_value:
					value.append(float(action))
			except ValueError:
				print("Item has to be float")
			else:
				done = True
	return value

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__":
    main()