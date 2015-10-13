#include "eHealth.h"
#include <iostream>
#include <fstream>
#include <chrono>
#include <stdlib.h>
using namespace std;
using namespace chrono;

int main (int argc, char *argv[]){
	
	bool ecg = false;
	bool gsr = false;
	bool file = false;
	bool term = false;
	bool socket = false;
	
	int delay_msec = 50;
	bool measure_loop = true;
	float ecg_value, gsr_value;
	ofstream out_file;
	
	for (int nArg=1; nArg < argc; nArg++) {
		if      ( strcmp("ecg",    argv[nArg])==0) ecg = true;
		else if ( strcmp("gsr",    argv[nArg])==0) gsr = true;
		else if ( strcmp("file",   argv[nArg])==0) file = true;
		else if ( strcmp("term",   argv[nArg])==0) term = true;
		else if ( strcmp("socket", argv[nArg])==0) socket = true;
		else {
			delay_msec = atoi(argv[nArg]);
			cout << "delay set to " << delay_msec << "milliseconds." << endl;
		}
	}
	if ( ecg==false and gsr==false ) {
		ecg = true;
		gsr = true;
	}
	if ( term==false and file==false and socket==false  ) {
		term=true;
	}
		
	if (file) out_file.open("data_record_" + to_string(time(0)));
	
	auto tic = high_resolution_clock::now();

	while(measure_loop){
		
		auto toc = high_resolution_clock::now();
		milliseconds dur = duration_cast<milliseconds>(toc-tic);
		
		if (ecg) ecg_value = eHealth.getECG();
		if (gsr) gsr_value = eHealth.getSkinConductance();
		
		if (term) {
			cout << dur.count()  << " " ; 
			if (ecg) cout << ecg_value;
			if (ecg and gsr) cout << " " ;
			if (gsr) cout << gsr_value; 
			cout << endl;
		}
		if (file) {
			out_file << dur.count() << " " ;
			if (ecg) out_file << ecg_value ;
			if (ecg and gsr) out_file << " " ;
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
