/*
***************************************
@author :    Thomas Lefort;
@contact :   thomas.lefort@ecam.fr
created on : 06/01/2016
title :      Code Arduino TIPE
***************************************
*/

/* ******************
   ***   Imports  ***
   ****************** */

#include "Timer.h"
#include <Encoder.h>
#include <AccelStepper.h>

/* ******************
   ***   Variables  ***
   ****************** */

// Bibliotèques
Encoder encodeur(2, 3);
Timer t;

// Variables générales
String sBuffer = "";
bool blocked = false;
int state = 0;
int count_motor = 0;
int angle = 0;
int angle_speed = 0;

// Pin Arduino
int pinA_power = 5;
int pinA_dir = 4;
int pinB_power = 9;
int pinB_dir = 8;

/* ******************
   ***  Functions ***
   ****************** */

void forwardstep() 
{
    motor_step(1); // Right
}

void backwardstep() 
{  
    motor_step(-1); // Left
}

AccelStepper stepper(forwardstep, backwardstep);

void read_serial()
{
    if(Serial.available() > 0) 
    {
        sBuffer = sBuffer + char(Serial.read());
    }
    else
    {
        if (sBuffer != "")
        {
            if(sBuffer == "S:gs\n"){
                send_state();
            }
            else if(sBuffer == "E:R\n"){
                reinit_encodeur();
            }
            else if (sBuffer == "L:T\n"){
                blocked = true;
            }
            else if (sBuffer == "L:F\n"){
                blocked = false;
            }
            else if (sBuffer.toInt() == 0){
                Serial.println("A:f");
            }
            else
            {
                stepper.move(sBuffer.toInt());
            }
            sBuffer = "";  
        }
    }
}

void motor_step(int sens)
{
    state = positive_modulo(state + sens, 8);
    count_motor = 0;
    switch(state)
    {
        case 0: 
            digitalWrite(pinA_power,HIGH);
            digitalWrite(pinB_power,HIGH);
            digitalWrite(pinA_dir,HIGH);
            digitalWrite(pinB_dir,HIGH);
            break;
 
        case 1:
            digitalWrite(pinA_power,HIGH);
            digitalWrite(pinB_power,LOW);
            digitalWrite(pinA_dir,HIGH);
            digitalWrite(pinB_dir,LOW);
            break;
 
        case 2:
            digitalWrite(pinA_power,HIGH);
            digitalWrite(pinB_power,HIGH);
            digitalWrite(pinA_dir,HIGH);
            digitalWrite(pinB_dir,LOW);
            break;
 
        case 3:
            digitalWrite(pinA_power,LOW);
            digitalWrite(pinB_power,HIGH);
            digitalWrite(pinA_dir,LOW);
            digitalWrite(pinB_dir,LOW);
            break;

        case 4:
            digitalWrite(pinA_power,HIGH);
            digitalWrite(pinB_power,HIGH);
            digitalWrite(pinA_dir,LOW);
            digitalWrite(pinB_dir,LOW);
            break;
 
        case 5:
            digitalWrite(pinA_power,HIGH);
            digitalWrite(pinB_power,LOW);
            digitalWrite(pinA_dir,LOW);
            digitalWrite(pinB_dir,LOW);
            break;
 
        case 6:
            digitalWrite(pinA_power,HIGH);
            digitalWrite(pinB_power,HIGH);
            digitalWrite(pinA_dir,LOW);
            digitalWrite(pinB_dir,HIGH);
            break;
 
        case 7:
            digitalWrite(pinA_power,LOW);
            digitalWrite(pinB_power,HIGH);
            digitalWrite(pinA_dir,LOW);
            digitalWrite(pinB_dir,HIGH);
            break;
    }
    if(stepper.distanceToGo() == 3 || stepper.distanceToGo() == -3){
        Serial.println("A:f");
    }
    if (blocked == false && (stepper.distanceToGo() == 1 || stepper.distanceToGo() == -1)){
        digitalWrite(pinA_power,LOW);
        digitalWrite(pinB_power,LOW);
        digitalWrite(pinA_dir,LOW);
        digitalWrite(pinB_dir,LOW);
    }
}

inline int positive_modulo(int i, int n)
{
    return (i % n + n) % n;
}

void need_to_stop()
{  
    count_motor++;
    if(count_motor == 10)
    {
        digitalWrite(pinA_power,LOW);
        digitalWrite(pinB_power,LOW);
        digitalWrite(pinA_dir,LOW);
        digitalWrite(pinB_dir,LOW);
    }
}

void reinit_encodeur()
{  
    encodeur.write(0);
    angle_speed = 0;
    angle = -300;
    Serial.println("D:Encoder reset");
}

void update_state()
{  
    if (angle != positive_modulo(encodeur.read(), 2400)/4 - 300)
    {
        int lastpos = angle;
        angle = positive_modulo(encodeur.read(), 2400)/4 - 300;
        angle_speed = angle - lastpos;
        if(angle_speed > 400){(angle_speed -= 600) * -1;}
        if(angle_speed < -400){(angle_speed += 600) * -1;}
    }
}

void send_state()
{
    if(angle_speed > 99){angle_speed = 99;}
    if(angle_speed < -100){angle_speed = -100;}
    if(angle > 299){angle = 299;}
    if(angle < -300){angle = -300;}
    Serial.println("S:" + String(angle) + ":" + String(angle_speed));
}

/* ******************
   ***    Setup   ***
   ****************** */

void setup()
{
    Serial.begin(115200);
  
    pinMode(pinA_power, OUTPUT);
    pinMode(pinA_dir, OUTPUT);
    pinMode(pinB_power, OUTPUT);
    pinMode(pinB_dir, OUTPUT);
  
    stepper.setMaxSpeed(1200.0);
    stepper.setAcceleration(1000.0);
    stepper.setSpeed(900.0);
  
    t.every(5, read_serial);
    t.every(10, need_to_stop);
    t.every(50, update_state);
  
    Serial.println("I:Arduino Launched");
}

/* ******************
   ***    Loop    ***
   ****************** */
   
void loop()
{
    stepper.run();
    t.update();
}

