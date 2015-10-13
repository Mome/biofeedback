#include <eHealth.h> 

void setup() {
  Serial.begin(115200);  
}

void loop() {

  float conductance = eHealth.getSkinConductance();
  //float resistance = eHealth.getSkinResistance();
  //float conductanceVol = eHealth.getSkinConductanceVoltage();

  Serial.print(conductance, 2);  
  //Serial.print(resistance, 2);  
  //Serial.print(conductanceVol, 4);  
  Serial.print('\n');
  
  delay(500);   
}
