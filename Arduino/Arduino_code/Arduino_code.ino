/*
***************************************
@author :    Thomas Lefo);
@contact :   thomas.lefort@ecam.fr
created on : 06/01/2016
title :      Code Arduino TIPE
***************************************
*/

/* ******************
   ***   Imports  ***
   ****************** */

#include "Timer.h"
#include <AccelStepper.h>

/* ******************
   ***   Variables  ***
   ****************** */

int pinA_power = 3;
int pinA_dir = 2;
int pinB_power = 9;
int pinB_dir = 8;
int angle = 0;
int encoder0PinA = 5;
int encoder0PinB = 6;
int encoder0PinALast = LOW;
Timer t;
int lastPos = 0;
int step_to_go = 0;
int state = 0;
int n = LOW;
String sBuffer = "";

void forwardstep() {
   motor_step(1);
}
void backwardstep() {  
   motor_step(2);
}

AccelStepper stepper(forwardstep, backwardstep);

/* ******************
   ***    Setup   ***
   ****************** */
   
void setup(){
  Serial.begin(115200);
  pinMode(pinA_power, OUTPUT);
  pinMode(pinA_dir, OUTPUT);
  pinMode(pinB_power, OUTPUT);
  pinMode(pinB_dir, OUTPUT);
  pinMode (encoder0PinA,INPUT);
  pinMode (encoder0PinB,INPUT);
  digitalWrite (encoder0PinA, HIGH); // Pullup
  digitalWrite (encoder0PinB, HIGH); 
  t.every(100, send_values);
  t.every(10, readserial);
  delay(1000);
}

/* ******************
   ***    Loop    ***
   ****************** */

void loop(){
  stepper.run();
  t.update();
  read_encoder();
}

/* ******************
   ***  Functions ***
   ****************** */

void send_values(){
  if (angle != lastPos){
  aspeed = angle - lastPos;
  if(aspeed > 400){(aspeed = aspeed - 600) * -1;}
  if(aspeed < -400){(aspeed = aspeed + 600) * -1;}
  long value = long(angle - 300)*10000 + long(aspeed);
  Serial.println(value);
  lastPos = angle;
  }
}

void readserial(){
  if(Serial.available() > 0) 
  {
    // read the incoming byte:
    sBuffer = sBuffer + char(Serial.read());
  }
  else{
     if (sBuffer != ""){
       step_to_go += sBuffer.toInt();
       stepper.moveTo(step_to_go);
       sBuffer = "";  
     }
  }
}

void read_encoder(){
  n = digitalRead(encoder0PinA);
  if ((encoder0PinALast == LOW) && (n == HIGH)) {
    if (digitalRead(encoder0PinB) == LOW) {
      angle--;
    } else {
      angle++;
    }
  }
  if(angle == -1){angle = 600;}
  if(angle == 601){angle = 0;}
  encoder0PinALast = n;
}

void motor_step(){
  int k = 3;
  while(k > 0)
    {
      switch(state)
      {
       case 0: 
         // Starting position (if repeated, full step (4))
          // in this case, both our power are high.
           // Therefore both coils are activated, with their standard polarities for their magnetic fields.
           digitalWrite(pinA_power,HIGH);
           digitalWrite(pinB_power,HIGH);
           digitalWrite(pinA_dir,HIGH);
           digitalWrite(pinB_dir,HIGH);
           break;
 
         case 1:
           //Half step (½)
           //In this case, only out b-coil is active, still with it's stand polarity.
           digitalWrite(pinA_power,HIGH);
           digitalWrite(pinB_power,LOW);
           digitalWrite(pinA_dir,HIGH);
           digitalWrite(pinB_dir,LOW);
           break;
 
         case 2:
           //Full step (1)
           // In this case, the b-coil is activated as in previous cases.
           // But the a-coil now has it's direction turned on. So now it's active, but with the reversered polarity.
           // By continuing this pattern (for reference: http://www.8051projects.net/stepper-motor-interfacing/full-step.gif) , you'll get the axis to turn.
           digitalWrite(pinA_power,HIGH);
           digitalWrite(pinB_power,HIGH);
           digitalWrite(pinA_dir,HIGH);
           digitalWrite(pinB_dir,LOW);
           break;
 
         case 3:
          // Half step (1½)
           digitalWrite(pinA_power,LOW);
           digitalWrite(pinB_power,HIGH);
           digitalWrite(pinA_dir,LOW);
           digitalWrite(pinB_dir,LOW);
           break;
 
         case 4:
           // Full step (2)
           digitalWrite(pinA_power,HIGH);
           digitalWrite(pinB_power,HIGH);
           digitalWrite(pinA_dir,LOW);
           digitalWrite(pinB_dir,LOW);
           break;
 
         case 5:
           // Half step (2½)
           digitalWrite(pinA_power,HIGH);
           digitalWrite(pinB_power,LOW);
           digitalWrite(pinA_dir,LOW);
           digitalWrite(pinB_dir,LOW);
          break;
 
         case 6:
           // Full step (3)
           digitalWrite(pinA_power,HIGH);
           digitalWrite(pinB_power,HIGH);
           digitalWrite(pinA_dir,LOW);
           digitalWrite(pinB_dir,HIGH);
           break;
 
         case 7:
           // Half step (3½)
           digitalWrite(pinA_power,LOW);
           digitalWrite(pinB_power,HIGH);
           digitalWrite(pinA_dir,LOW);
           digitalWrite(pinB_dir,HIGH);
           break;
   }
   if(sens == 1){state--;}      //decrement of remaining halfsteps of forward rotation
   if(sens == 2){state++;}
   state = state % 8;
  }
}