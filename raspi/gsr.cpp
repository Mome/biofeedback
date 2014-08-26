//Include eHealth library
#include "eHealth.h"

void loop() { 
	
  float conductance = eHealth.getSkinConductance();
  float resistance = eHealth.getSkinResistance();
  float conductanceVol = eHealth.getSkinConductanceVoltage();

  printf("Conductance : %f \n", conductance);    
  printf("Resistance : %f \n", resistance);  
  printf("Conductance Voltage : %f \n", conductanceVol);       

  printf("\n");

  // wait for a second  
  delay(1000);   
}

int main (){
	//setup();
	while(1){
		loop();
	}
	return (0);
}
