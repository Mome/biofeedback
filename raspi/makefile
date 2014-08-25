#EHEALTH_PATH=eHealth2-raspberry
EHEALTH_PATH=eHealth2-raspberry-V2.3

all: GSR

arduPi.o: 
	g++ -c arduPi/arduPi.cpp -o arduPi.o

eHealth.o: 
	g++ -c -I arduPi $(EHEALTH_PATH)/eHealth.cpp -o eHealth.o

GSR: arduPi.o eHealth.o gsr.cpp
	g++ -I arduPi -I $(EHEALTH_PATH) -lpthread -lrt gsr.cpp arduPi.o eHealth.o -o GSR

clean:
	rm -rf *o GSR 
