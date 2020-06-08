// This #include statement was automatically added by the Particle IDE.
#include <LiquidCrystal.h>

#include "MQTT.h"

Servo myservo;  // create servo object to control a servo
                // a maximum of eight servo objects can be created

int redLed = D1;
int greenLed = D0;

int pos = 0; 
int prev = 0;
int flag = 0;
// Create an MQTT client
// MQTT client("localhosttest.mosquitto.org", 1883, callback);
MQTT client("test.mosquitto.org", 1883, callback);


// This is called when a message is received. However, we do not use this feature in
// this project so it will be left empty
void callback(char* topic, byte* payload, unsigned int length) 
{
    String messageTemp;
  
    for (int i = 0; i < length; i++) {
        Serial.print((char)payload[i]);
        messageTemp += (char)payload[i];
    }

    int msg = atoi(messageTemp);
    Serial.println();
    
    if(msg == 1 || msg == 0 ){
        // To check whether the park is full or not
        Serial.println("Checkin Park Status");
        if(prev != msg){
            if(msg == 1){
                closeGate();
                Serial.println("Car Park Full");
                
                client.publish("carPark/lcd", "1");
                
                flag = 1;
            }else{
                Serial.println("Car Park Not Full");
                
                 client.publish("carPark/lcd", "0");
                flag = 0;
             }
             
        prev = msg;
    }
    
    if(msg == 3){
        Serial.println("AT THE GATE");
        if(flag != 1){
            Serial.println("Opening Gate");
            openGate();
            delay(1000*5);
            Serial.println("Closing Gate");
            closeGate();
            delay(1000);
        }
        // Nothing can be done if the flag is 1 which means the car park is full
    }
    
}

void closeGate(){
    
            myservo.write(90);
            delay(1000);
}

void openGate(){
    
            myservo.write(0);           // tell servo to go to position in variable 'pos'            
            delay(1000); 
}


void setup() 
{

    pinMode(redLed, OUTPUT);
    pinMode(greenLed, OUTPUT);
    
    myservo.attach(D4); 
    // Connect to the server and call ourselves "photonDev"
    client.connect("pd");
    
    client.subscribe("carPark/status");
    client.subscribe("carPark/gate");
    // Configure GPIO 0 to be an input
    pinMode(0, INPUT);
}


// Main loop
void loop() 
{
            
        client.loop();

}


