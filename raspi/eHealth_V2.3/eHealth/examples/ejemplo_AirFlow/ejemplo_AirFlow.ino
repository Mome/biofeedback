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
 

// the setup routine runs once when you press reset:
void setup() {                
  Serial.begin(115200);  
}

// the loop routine runs over and over again forever:
void loop() {
  
  
  int airFlow = eHealth.getAirFlow(); 
  //Serial.println(airFlow);
  
  if (airFlow >10)
  
  for (int i=0; i < (airFlow / 3) ;i ++) {  
        Serial.print("..");  
  }
  
  Serial.print("..");
  Serial.print("\n");
  delay(40);
  
}
       
  
