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
#include <Encoder.h>

/* ******************
   ***   Variables  ***
   ****************** */

int mspeed = 2;
int aspeed = 0;
int pinA_power = 5;
int pinA_dir = 4;
int pinB_power = 9;
int pinB_dir = 8;
int angle = 0;
//int encoder0PinA = 2;
//int encoder0PinB = 3;
Encoder encodeur(2, 3);
Timer t;
int lastPos = 0;
int step_to_go = 0;
int state = 5;
int needstop = 0;
int n = LOW;
String sBuffer = "";

/* ******************
   ***    Setup   ***
   ****************** */
   
void setup(){
  Serial.begin(115200);
  pinMode(pinA_power, OUTPUT);
  pinMode(pinA_dir, OUTPUT);
  pinMode(pinB_power, OUTPUT);
  pinMode(pinB_dir, OUTPUT);
//  pinMode (encoder0PinA,INPUT);
//  pinMode (encoder0PinB,INPUT);
//  digitalWrite (encoder0PinA, HIGH); // Pullup
//  digitalWrite (encoder0PinB, HIGH); 
  t.every(100, send_values);
  t.every(400, need_stop);
  t.every(15, readserial);
//  attachInterrupt(digitalPinToInterrupt(encoder0PinA), doEncoder, CHANGE); 
  t.every(3, moteur_move);
  delay(1000);
}

/* ******************
   ***    Loop    ***
   ****************** */

void readserial(){
  if(Serial.available() > 0) 
  {
    // read the incoming byte:
    sBuffer = sBuffer + char(Serial.read());
    state += 1;
  }
  else{
    if (sBuffer != ""){
      step_to_go += sBuffer.toInt()*2;
      sBuffer = "";  
    }
  }
}

/* ******************
   ***  Functions ***
   ****************** */
inline int positive_modulo(int i, int n) {
   return (i % n + n) % n;
}

void send_values(){
  angle = positive_modulo(encodeur.read(), 2400)/4 - 300;
  if (state > 1){
    needstop = 0;
    aspeed = angle - lastPos;
    if(aspeed > 400){(aspeed = aspeed - 600) * -1;}
    if(aspeed < -400){(aspeed = aspeed + 600) * -1;}
    long value = long(angle)*10000 + long(aspeed);
    Serial.println(value);
    state -= 1;
    lastPos = angle;
  }
  else
  {
    needstop++;
  }
}

void need_stop(){
  if(needstop > 50){
    encodeur.write(0);
  }
}

//void doEncoder() {
//  if (digitalRead(encoder0PinA) == digitalRead(encoder0PinB)) {
//    angle++;
//  } else {
//    angle--;
//  }
//  if(angle == -1){angle = 1200;}
//  if(angle == 1201){angle = 0;}
//}

void moteur_move(){
  if(step_to_go != 0)
    {
      int _sub = step_to_go % 8;
      if(_sub < 0){_sub += 8;}
      switch(_sub)
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
   if(step_to_go>0){step_to_go--;}      //decrement of remaining halfsteps of forward rotation
   if(step_to_go<0){step_to_go++;}
  }
  else{
    digitalWrite(pinA_power,LOW);
    digitalWrite(pinB_power,LOW);
    digitalWrite(pinA_dir,LOW);
    digitalWrite(pinB_dir,LOW);
  }
}

void loop(){
  t.update();
}


