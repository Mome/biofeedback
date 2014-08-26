#include "eHealth.h"

void loop() {

  
  float ECG = eHealth.getECG();
  float conductance = eHealth.getSkinConductance(); 

  printf("%f %f \n",ECG,conductance);
  delay(1000);
}

int main (){
	//setup();
	while(1){
		loop();
	}
	return (0);
}