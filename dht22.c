#include <wiringPi.h>

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#define MAXTIMINGS 85
#define DHTPIN 7
int dht11_dat[5] = {0,0,0,0,0};
float retValues[2] = {-1,-1};

void read_dht11_dat()
{
  uint8_t laststate = HIGH;
  uint8_t counter = 0;
  uint8_t j = 0, i;
  float ff; // fahrenheit
  float f,h;

  retValues[0] = -1;
  retValues[1] = -1;

  dht11_dat[0] = dht11_dat[1] = dht11_dat[2] = dht11_dat[3] = dht11_dat[4] = 0;

  // pull pin down for 18 milliseconds
  pinMode(DHTPIN, OUTPUT);
  digitalWrite(DHTPIN, LOW);
  delay(18);
///  digitalWrite(DHTPIN, HIGH);
///  delay(500);
  
  // then pull it up for 40 microseconds
  digitalWrite(DHTPIN, HIGH);
  delayMicroseconds(40); 
///  digitalWrite(DHTPIN, LOW);
///  delay(20);

  // prepare to read the pin
  pinMode(DHTPIN, INPUT);

  // detect change and read data
  for ( i=0; i< MAXTIMINGS; i++) {
    counter = 0;
    while (digitalRead(DHTPIN) == laststate) {
      counter++;
      delayMicroseconds(1);
      if (counter == 255) {
        break;
      }
    }
    laststate = digitalRead(DHTPIN);

    if (counter == 255) break;

    // ignore first 3 transitions
    if ((i >= 4) && (i%2 == 0)) {
      // shove each bit into the storage bytes
      dht11_dat[j/8] <<= 1;
      if (counter > 16)
        dht11_dat[j/8] |= 1;
      j++;
    }
  }

  // check we read 40 bits (8bit x 5 ) + verify checksum in the last byte
  // print it out if data is good
  if ((j >= 40) && 
      (dht11_dat[4] == ((dht11_dat[0] + dht11_dat[1] + dht11_dat[2] + dht11_dat[3]) & 0xFF)) ) {

    h = dht11_dat[0] * 256 + dht11_dat[1];
    h /= 10;
    f = (dht11_dat[2] & 0x7F)* 256 + dht11_dat[3];
        f /= 10.0;
        if (dht11_dat[2] & 0x80) f *= -1;
    ff = f * 9. / 5. + 32;
    retValues[0] = f;
    retValues[1] = h;
//1
//    printf("Temp = %.1f *C / %.lf *F , Hum = %.1f \%\n", f, ff, h);
//    f = dht11_dat[2] * 9. / 5. + 32;
//    printf("Humidity = %d.%d %% Temperature = %d.%d *C (%.1f *F)\n", 
//            dht11_dat[0], dht11_dat[1], dht11_dat[2], dht11_dat[3], f);
  }
  else
  {
//2
//    printf("Data not good, skip\n");
  }
}

int main (void)
{

  if (wiringPiSetup () == -1) {
     printf("100,100\n");
     exit (1) ;
  }
  float tmp;
  float hum;
  int i;
  int wrongCounter;
  float rightCounter;
  rightCounter = 0.0;

  for (i=0;i<5;i++) {
     wrongCounter = 0;
     do {
        wrongCounter++;
         read_dht11_dat();
    delay(4000);
     } while (retValues[0] == -1 && wrongCounter < 10);
     if (retValues[0] != -1) {
        rightCounter += 1.0;;
        tmp += retValues[0];
        hum += retValues[1];
     }
     delay(60000); //delay 1 minute
  }

if (rightCounter > 0) {
  printf("%.1f,%.1f\n", tmp / rightCounter , hum / rightCounter);
} else {
  printf("100,100\n");
}
  return 0 ;
}
