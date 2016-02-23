-- Schema for Q-learning

create table Qvalue_lower (
    State       float primary key,
    Action1     float,
    Action2     float,
    Action3     float,
    Action4     float,
    Action5     float
);
