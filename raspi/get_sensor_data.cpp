#include "eHealth.h"
#include <iostream>
#include <fstream>
using namespace std;

int main (int argc, char *argv[]){
	
	bool ecg = false;
	bool gsr = false;
	bool file = false;
	bool term = false;
	bool socket = false;
	
	int delay_msec = 500;

	bool measure_loop = true;
	
	float ecg_value, gsr_value;
	
	ofstream out_file;
	
	for (int nArg=1; nArg < argc; nArg++) {
		if ( strcmp("ecg",    argv[nArg])==0) ecg = true;
		if ( strcmp("gsr",    argv[nArg])==0) gsr = true;
		if ( strcmp("file",   argv[nArg])==0) file = true;
                if ( strcmp("term",   argv[nArg])==0) term = true;
		if ( strcmp("socket", argv[nArg])==0) socket = true;
	}
	if ( ecg==false and gsr==false ) {
		ecg = true;
		gsr = true;
	}
	if ( term==false and file==false and socket==false  ) {
		term=true;	
	}
	
	if (file) out_file.open("data_record");
	
	while(measure_loop){
		if (ecg) ecg_value = eHealth.getECG();
		if (gsr) gsr_value = eHealth.getSkinConductance();
		
		if (term) {
			if (ecg) cout << ecg_value;
			if (ecg and gsr) cout << " ";
			if (gsr) cout << gsr_value; 
			cout << endl;
		}
		if (file) {
			if (ecg) out_file << ecg_value;
			if (ecg and gsr) out_file << " ";
                        if (gsr) out_file << gsr_value; 
                        out_file << endl;
		}
		if (socket) {
			// not implemented
		}
		
		delay(delay_msec);
	}
	
	out_file.close();	
	return 0;
}
