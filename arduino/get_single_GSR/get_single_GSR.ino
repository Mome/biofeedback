#include <eHealth.h> 

void setup() {
  Serial.begin(115200);  
}

void loop() {

  float conductance = eHealth.getSkinConductance();
  //float resistance = eHealth.getSkinResistance();
  //float conductanceVol = eHealth.getSkinConductanceVoltage();

  Serial.println(conductance, 2);  
  //Serial.println(resistance, 2);  
  //Serial.println(conductanceVol, 4);  

  delay(100);            
}
