#include <eHealth.h>

void setup() {
  Serial.begin(115200);
  //Serial.begin(9600); 
}

void loop() {

  float ECG = eHealth.getECG();
  float conductance = eHealth.getSkinConductance();

  Serial.print(ECG, 2);
  Serial.print(" ");
  Serial.print(conductance, 2); 
  Serial.print("\n");

  delay(50);
}

