#include <eHealth.h> 

// the setup routine runs once when you press reset:
void setup() {
  Serial.begin(115200);  
}

// the loop routine runs over and over again forever:
void loop() {

  float conductance = eHealth.getSkinConductance();
  float resistance = eHealth.getSkinResistance();
  float conductanceVol = eHealth.getSkinConductanceVoltage();

  Serial.print("Conductance : ");       
  Serial.print(conductance, 2);  
  Serial.println("");         

  Serial.print("Resistance : ");       
  Serial.print(resistance, 2);  
  Serial.println("");    

  Serial.print("Conductance Voltage : ");       
  Serial.print(conductanceVol, 4);  
  Serial.println("");

  Serial.print("\n");

  // wait for a second  
  delay(1000);            
}
