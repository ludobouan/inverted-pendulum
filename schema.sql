-- Schema for Q-learning

create table Qvalues (
    Agent       	string,
    State     		float,
    Action     		float,
    Value     		float,
    Visited         boolean
);

create table Agents (
    Name     		string,
    Creation_date   timestamp,
    Note     		string,
    Epsilon     	float,
    Gamma     		float,
    Alpha     		float,
    Beta            float,
    Epsilon_d       float,
    TwoAgent     	boolean,
    Eligibility     boolean
);

create table States (
    Agent       	string,
    Value           string,
    isUpper     	boolean,
    Reward      	float
);

create table Actions (
    Agent       	string,
    Value     		float,
    isUpper     	boolean
);

create table Results (
	Agent 			string,
	Episode			int,
	Air_time		int,
	Average_reward	float
);

create table Experiments (
    Name            string,
    Agent           string,
    Simulation      boolean,
    Nbr_episode     int,
    Nbr_step        int,
    Pause_time      int,
    Current_episode int,
    StepRate        int,
    Regression      boolean

);
