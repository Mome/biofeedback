/*
 *  eHealth sensor platform fro Arduino and Raspberry from Cooking-hacks.
 *
 *  Explanation : eHealth is a board that integrates diferent sensors
 *  for monitoring vital signs of human body.
 *  
 *  In this example we are going to measure the blood pressure
 *  and show the result in the serial monitor.   
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
 *  along with this program.  If not, see <http://www.gnu.org/licenses/> .
 *
 *  Version 0.1
 *  Author: Ahmad Saad  & Luis Martin
 */


#include <eHealth.h>

float parameter = 0.0;

void setup() {
  Serial.begin(115200);
  Serial.println("Press On/Off button please...");

}

void loop() {

  eHealth.initTensionometer(parameter);

  Serial.println("****************************");
  Serial.print("Systolic blood pressure value : ");
  Serial.println(eHealth.getSystolicPressure());
  delay(10);

  Serial.println("****************************");
  Serial.print("Diastolic blood pressure value : ");
  Serial.println(eHealth.getDiastolicPressure());
  delay(10); 

  delay(3000);   
}

