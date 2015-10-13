#include "eHealth.h"

void loop() {

  float ECG = eHealth.getECG();

  printf("ECG value :  %f V\n",ECG);
  delay(1000);
}

int main (){
	//setup();
	while(1){
		loop();
	}
	return (0);
}
