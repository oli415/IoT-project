//Code from DHT11_Example, Active Buzzer,
//https://www.pjrc.com/teensy/td_libs_AltSoftSerial.html

#include <dht_nonblocking.h>
#include <AltSoftSerial.h>
#define DHT_SENSOR_TYPE DHT_TYPE_11

static const int DHT_SENSOR_PIN = 2;
DHT_nonblocking dht_sensor( DHT_SENSOR_PIN, DHT_SENSOR_TYPE );
int yled = 3;            //the pin of the yellow LED
bool yled_status = HIGH;  //the yellow led status

AltSoftSerial BTserial;  // RX = 8, TX = 9
char inDataBT = ' ';  
char inDataSerial = ' ';
bool NL = true;
int ble_led = 13;

/*
 * Initialize the serial ports.
 * set leds to pinMode OUTPUT
 */
void setup( )
{
  pinMode(yled, OUTPUT); //initialize the led pin as an output
  digitalWrite(yled, LOW); // switch OFF yellow LED
  Serial.begin(9600);
  BTserial.begin(9600);
  pinMode(ble_led, OUTPUT); // onboard LED and blue LED
  digitalWrite(ble_led, LOW); // switch OFF BLE LED
  Serial.print("Arduino node ready!\n");
}

/*
 * Poll for a measurement, keeping the state machine alive.  Returns
 * true if a measurement is available.
 */
static bool measure_environment( float *temperature, float *humidity )
{
  static unsigned long measurement_timestamp = millis( );
  static bool first_call = 1;

  /* Measure once every five seconds. */
  if(first_call || (millis() - measurement_timestamp > 5000ul))
  {
    if( dht_sensor.measure( temperature, humidity ) == true )
    {
      first_call = 0;
      measurement_timestamp = millis();
      return(true);
    }
  }

  return(false);
}

/*
 * Main program loop.
 */
void loop( )
{
  //sensor and LED code
  float temperature;
  float humidity;

  /* Measure temperature and humidity.  If the functions returns
     true, then a measurement is available. */
  if(measure_environment(&temperature, &humidity) == true)
  {
    digitalWrite(yled, yled_status);
    yled_status = (yled_status == LOW) ? HIGH : LOW;
    Serial.print("T = ");
    Serial.print(temperature, 1);
    Serial.print("deg. C, H = ");
    Serial.print(humidity, 1);
    Serial.println("%");
    BTserial.print("T = ");
    BTserial.print(temperature, 1);
    BTserial.print("C, H = ");
    BTserial.print(humidity, 1);
    BTserial.print("%");
  }

  //BLE code
  // Read from the Bluetooth module and send to the Arduino Serial Monitor
  if (BTserial.available()){
      inDataBT = BTserial.read();
      Serial.write(inDataBT);

      /*if (inDataBT == 'F') {
        inDataBT = ' ';
        Serial.println("\nLED OFF");
        digitalWrite(ble_led, LOW); // switch OFF BLE LED
      }
      if (inDataBT == 'N') {
        inDataBT = ' ';
        Serial.println("\nLED ON");
        digitalWrite(ble_led, HIGH); // switch ON BLE LED
      }*/
  }
  
  // Read from the Serial Monitor and send to the Bluetooth module
    if (Serial.available())
    {
        inDataSerial = Serial.read();
 
        // do not send line end characters to the HM-17 (10 = LF, 13 = CR)
        if ((inDataSerial != 10) & (inDataSerial != 13) ) 
        {  
             BTserial.write(inDataSerial);
        }
 
        // Echo the user input to the main window. 
        // If there is a new line print the ">" character.
        if (NL){
          Serial.print("\r\n");
          NL = false;
        }
        Serial.write(inDataSerial);
        if (inDataSerial == 10){
          NL = true;
        }
    }
}
