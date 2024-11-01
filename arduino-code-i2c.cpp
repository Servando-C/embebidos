#include <Wire.h>

#define I2C_SLAVE_ADDR 0x0A
#define BOARD_LED 13

void i2c_received_handler(int count);
void i2c_request_handler(int count);
float read_temp(void);
float read_avg_temp(int count);

int ThermistorPin = A0;
int Vo;
float R1 = 10000; // value of R1 on board
float logR2, R2, T;
float c1 = 0.001129148, c2 = 0.000234125, c3 = 0.0000000876741; //steinhart-hart coeficients for thermistor

void setup() {
  // Configure I2C to run in slave mode with the defined address
	Wire.begin(I2C_SLAVE_ADDR);
	// Configure the handler for received I2C data
	Wire.onReceive(i2c_received_handler);
	// Configure the handler for request of data via I2C
	Wire.onRequest(i2c_request_handler);

  Serial.begin(9600);

}

void loop() {
  Vo = analogRead(ThermistorPin);
  R2 = R1*Vo/(1023-Vo); //calculate resistance on thermistor
  logR2 = log(R2);
  T = (1.0 / (c1 + c2*logR2 + c3*logR2*logR2*logR2)); // temperature in Kelvin
  T = T - 273.15; //convert Kelvin to Celcius
  Serial.print("Temperature: "); 
  Serial.print(T);
  Serial.println(" C"); 

  delay(100);
}

void i2c_request_handler(){
	Wire.write((byte*) &T, sizeof(float));
}

void i2c_received_handler(int count){
	char received = 0;
	while (Wire.available()){
		received = (char)Wire.read();
		digitalWrite(BOARD_LED, received ? HIGH : LOW);
		Serial.println(received);
	}

}
