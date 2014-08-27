#include "eHealth.h"

int main (int argc, char *argv[]){
	
	bool ecg = false;
	bool gsr = false;
	int delay_msec = 500;

	for (int nArg=1; nArg < argc; nArg++) {
		if ( strcmp('ecg', argv[nArg])==0) ecg = true;
		if ( strcmp('gsr', argv[nArg])==0) gsr = true;
	}

	if (ecg == true and gsr == false) {
		while(1){
			float conductance = eHealth.getSkinConductance(); 
			printf("%f\n",conductance);
			delay(delay_msec);
		}
	}
	else if (ecg == false and gsr == true) {
		while(1){
			float ECG = eHealth.getECG();
			printf("%f\n",ECG);
			delay(delay_msec);
		}
	}
	else {
		while(1){
			float ECG = eHealth.getECG();
			float conductance = eHealth.getSkinConductance(); 
			printf("%f %f\n",ECG,conductance);
			delay(delay_msec);
		}
	}


	return (0);
}