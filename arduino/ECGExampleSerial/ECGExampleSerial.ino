#include <eHealth.h>

void setup() {
  Serial.begin(115200);  
}

void loop() {

  float ECG = eHealth.getECG();

  //Serial.print("ECG value :  ");
  Serial.print(ECG, 2); 
  //Serial.print(" V"); 
  Serial.print("\n");

  delay(50);
}

