#EHEALTH_PATH=eHealth2-raspberry
EHEALTH_PATH=eHealth2-raspberry-V2.3

all: GET_SENSOR_DATA 

arduPi.o: 
	g++ -c arduPi/arduPi.cpp -o arduPi.o

eHealth.o: 
	g++ -c -I arduPi $(EHEALTH_PATH)/eHealth.cpp -o eHealth.o

GSR: arduPi.o eHealth.o gsr.cpp
	g++ -I arduPi -I $(EHEALTH_PATH) -lpthread -lrt gsr.cpp arduPi.o eHealth.o -o GSR

ECG: arduPi.o eHealth.o ecg.cpp
	g++ -I arduPi -I $(EHEALTH_PATH) -lpthread -lrt ecg.cpp arduPi.o eHealth.o -o ECG

ECG_GSR: arduPi.o eHealth.o ecg_gsr.cpp
	g++ -I arduPi -I $(EHEALTH_PATH) -lpthread -lrt ecg_gsr.cpp arduPi.o eHealth.o -o ECG_GSR

GET_SENSOR_DATA: arduPi.o eHealth.o get_sensor_data.cpp
	g++ -I arduPi -I $(EHEALTH_PATH) -lpthread -lrt get_sensor_data.cpp arduPi.o eHealth.o -o GET_SENSOR_DATA

sweep:
	rm -rf GET_SENSOR_DATA

clean:
	rm -rf *o GSR ECG ECG_GSR
