g++ -c arduPi/arduPi.cpp -o arduPi.o

g++ -c eHealth2-raspberry-V2.3/eHealth.cpp -o eHealth.o

g++ -lpthread -lrt gsr.cpp arduPi.o eHealth.o -o GSR 
