/*
 *  eHealth sensor platform for Arduino and Raspberry from Cooking-hacks.
 *
 *  Description: "The e-Health Sensor Shield allows Arduino and Raspberry Pi 
 *  users to perform biometric and medical applications by using 9 different 
 *  sensors: Pulse and Oxygen in Blood Sensor (SPO2), Airflow Sensor (Breathing),
 *  Body Temperature, Electrocardiogram Sensor (ECG), Glucometer, Galvanic Skin
 *  Response Sensor (GSR - Sweating), Blood Pressure (Sphygmomanometer) and 
 *  Patient Position (Accelerometer)."
 *
 *  In this example we read the values in volts of EMG sensor and show
 *  these values in the serial monitor. 
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
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 *  Version 2.0
 *  Author: Luis Martin & Ahmad Saad & Anartz Nuin
 */

//Include eHealth library
#include "eHealth.h"

void setup() { 

  eHealth.readGlucometer();
  delay(100);    
}

void loop() { 

  uint8_t numberOfData = eHealth.getGlucometerLength();   
  printf("Number of measures : %d",numberOfData);       
  delay(100);


  for (int i = 0; i< numberOfData; i++) { 
    // The protocol sends data in this order 
    printf("\n==========================================\n");

    printf("Measure number %d\n",i+1);

    printf("Date -> %d",eHealth.glucoseDataVector[i].day); 
    printf(" of "); 
    printf("%s",eHealth.numberToMonth(eHealth.glucoseDataVector[i].month));
    printf(" of ");
    printf("%d",2000 + eHealth.glucoseDataVector[i].year);    
    printf(" at ");

    if (eHealth.glucoseDataVector[i].hour < 10) {
      printf("0"); // Only for best representation.
    }

    printf("%d",eHealth.glucoseDataVector[i].hour);
    printf(":");

    if (eHealth.glucoseDataVector[i].minutes < 10) {
      printf("0");// Only for best representation.
    }
    printf("%d",eHealth.glucoseDataVector[i].minutes);

    if (eHealth.glucoseDataVector[i].meridian == 0xBB)
      printf(" pm");
    else if (eHealth.glucoseDataVector[i].meridian == 0xAA)
      printf(" am"); 

    printf("\nGlucose value : %d mg/dL",eHealth.glucoseDataVector[i].glucose); 
  }
  delay(20000);
}

int main (){
	setup();
	while(1){
		loop();
	}
	return (0);
}
