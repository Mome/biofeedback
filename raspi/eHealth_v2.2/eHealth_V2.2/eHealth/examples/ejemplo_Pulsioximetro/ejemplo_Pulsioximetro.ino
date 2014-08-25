
/*
  *  eHelath board from Libelium for Arduino.
  *  Explanation : 
  *
  *  Copyright (C) 2012 Libelium Comunicaciones Distribuidas S.L.
  *  http://www.libelium.com
  *
  *  This program is free software: you can redistribute it and/or modify
  *  it under the terms of the GNU General Public License as published by
  *  the Free Software Foundation, either version 3 of the License, or
  *  (at your option) any later version.
  *
  *  This program is distributed in the hope that it will be useful,
  *  but WITHOUT ANY WARRANTY; without even the implied warranty of
  *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  *  GNU General Public License for more details.
  *
  *  You should have received a copy of the GNU General Public License
  *  along with this program.  If not, see .
  *
  *  Version 0.1
  *  Author: Ahmad Saad & Luis Martin
  */


#include <eHealth.h>

void setup() {  
    Serial.begin(115200);  
    eHealth.initPulsioximeter();
}

void loop() {    
  
  //Serial.print("PRbpm : "); 
  //Serial.print(eHealth.getOxygenSaturation());

  //Serial.print(" % SPo2 : ");
  //Serial.print(eHealth.getBPM());
  
  //Serial.print("\n");
  
  eHealth.readPulsioximeter();
    delay(100);               // wait for a second

  float temperature = eHealth.getTemperature();
  
         Serial.print("Temperature (ºC): ");       
         Serial.print(temperature, 2);  
         Serial.println("");
         
    delay(100);               // wait for a second
}
