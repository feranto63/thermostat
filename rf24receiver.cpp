#include <RF24/RF24.h>
#include <RF24Network/RF24Network.h>
#include <iostream>
#include <ctime>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
//#include <wiringPi.h>
//#include <stdio.h>
//#include <stdlib.h>
//#include <stdint.h>
//#include "bcm2835.h"

//char* ntoa(double num)
//{ 
//    /* log10(num) gives the number of digits; + 1 for the null terminator */
//    int size = log10(num) + 1;
//    char *x = malloc(size);
//    snprintf(x, size, "%f", num);
//}

// gestione DHT xx Adafruit
#include <stdbool.h>
//#include <stdlib.h>

#include "pi_2_dht_read.h"
#include "pi_2_mmio.h"

/*
// This is the only processor specific magic value, the maximum amount of time to
// spin in a loop before bailing out and considering the read a timeout.  This should
// be a high value, but if you're running on a much faster platform than a Raspberry
// Pi or Beaglebone Black then it might need to be increased.
#define DHT_MAXCOUNT 32000

// Number of bit pulses to expect from the DHT.  Note that this is 41 because
// the first pulse is a constant 50 microsecond pulse, with 40 pulses to represent
// the data afterwards.
#define DHT_PULSES 41

int pi_2_dht_read(int type, int pin, float* humidity, float* temperature) {
  // Validate humidity and temperature arguments and set them to zero.
  if (humidity == NULL || temperature == NULL) {
    return DHT_ERROR_ARGUMENT;
  }
  *temperature = 0.0f;
  *humidity = 0.0f;

  // Initialize GPIO library.
  if (pi_2_mmio_init() < 0) {
    return DHT_ERROR_GPIO;
  }

  // Store the count that each DHT bit pulse is low and high.
  // Make sure array is initialized to start at zero.
  int pulseCounts[DHT_PULSES*2] = {0};

  // Set pin to output.
  pi_2_mmio_set_output(pin);

  // Bump up process priority and change scheduler to try to try to make process more 'real time'.
  set_max_priority();

  // Set pin high for ~500 milliseconds.
  pi_2_mmio_set_high(pin);
  sleep_milliseconds(500);

  // The next calls are timing critical and care should be taken
  // to ensure no unnecssary work is done below.

  // Set pin low for ~20 milliseconds.
  pi_2_mmio_set_low(pin);
  busy_wait_milliseconds(20);

  // Set pin at input.
  pi_2_mmio_set_input(pin);
  // Need a very short delay before reading pins or else value is sometimes still low.
  for (volatile int i = 0; i < 50; ++i) {
  }

  // Wait for DHT to pull pin low.
  uint32_t count = 0;
  while (pi_2_mmio_input(pin)) {
    if (++count >= DHT_MAXCOUNT) {
      // Timeout waiting for response.
      set_default_priority();
      return DHT_ERROR_TIMEOUT;
    }
  }

  // Record pulse widths for the expected result bits.
  for (int i=0; i < DHT_PULSES*2; i+=2) {
    // Count how long pin is low and store in pulseCounts[i]
    while (!pi_2_mmio_input(pin)) {
      if (++pulseCounts[i] >= DHT_MAXCOUNT) {
        // Timeout waiting for response.
        set_default_priority();
        return DHT_ERROR_TIMEOUT;
      }
    }
    // Count how long pin is high and store in pulseCounts[i+1]
    while (pi_2_mmio_input(pin)) {
      if (++pulseCounts[i+1] >= DHT_MAXCOUNT) {
        // Timeout waiting for response.
        set_default_priority();
        return DHT_ERROR_TIMEOUT;
      }
    }
  }

  // Done with timing critical code, now interpret the results.

  // Drop back to normal priority.
  set_default_priority();

  // Compute the average low pulse width to use as a 50 microsecond reference threshold.
  // Ignore the first two readings because they are a constant 80 microsecond pulse.
  uint32_t threshold = 0;
  for (int i=2; i < DHT_PULSES*2; i+=2) {
    threshold += pulseCounts[i];
  }
  threshold /= DHT_PULSES-1;

  // Interpret each high pulse as a 0 or 1 by comparing it to the 50us reference.
  // If the count is less than 50us it must be a ~28us 0 pulse, and if it's higher
  // then it must be a ~70us 1 pulse.
  uint8_t data[5] = {0};
  for (int i=3; i < DHT_PULSES*2; i+=2) {
    int index = (i-3)/16;
    data[index] <<= 1;
    if (pulseCounts[i] >= threshold) {
      // One bit for long pulse.
      data[index] |= 1;
    }
    // Else zero bit for short pulse.
  }

  // Useful debug info:
  //printf("Data: 0x%x 0x%x 0x%x 0x%x 0x%x\n", data[0], data[1], data[2], data[3], data[4]);

  // Verify checksum of received data.
  if (data[4] == ((data[0] + data[1] + data[2] + data[3]) & 0xFF)) {
    if (type == DHT11) {
      // Get humidity and temp for DHT11 sensor.
      *humidity = (float)data[0];
      *temperature = (float)data[2];
    }
    else if (type == DHT22) {
      // Calculate humidity and temp for DHT22 sensor.
      *humidity = (data[0] * 256 + data[1]) / 10.0f;
      *temperature = ((data[2] & 0x7F) * 256 + data[3]) / 10.0f;
      if (data[2] & 0x80) {
        *temperature *= -1.0f;
      }
    }
    return DHT_SUCCESS;
  }
  else {
    return DHT_ERROR_CHECKSUM;
  }
}

// fine gestione DHT Adafruit
*/



#include <sqlite3.h> 

static int callback(void *NotUsed, int argc, char **argv, char **azColName){
   int i;
   for(i=0; i<argc; i++){
      printf("%s = %s\n", azColName[i], argv[i] ? argv[i] : "NULL");
   }
   printf("\n");
   return 0;
}

void log_w_sensor (sqlite3 *db, char *t_stamp, int node_id, float temp, float humid) {
	char sql[200];
   	char *zErrMsg = 0;
   	int rc;

	sprintf(sql,"INSERT INTO 'w_temps' VALUES ('%s', %i, %f, %f);", t_stamp, node_id, temp, humid);
	printf(sql);
   	/* Execute SQL statement */
   	rc = sqlite3_exec(db, sql, callback, 0, &zErrMsg);
   	if( rc != SQLITE_OK ){
      		fprintf(stderr, "SQL error: %s\n", zErrMsg);
      		sqlite3_free(zErrMsg);
   	}else{
      		fprintf(stdout, "Records created successfully\n");
   	}
}


// Structure of our message
struct message_t {
  float temperature;
  float humidity;
};



// CE Pin, CSN Pin, SPI Speed
RF24 radio(RPI_BPLUS_GPIO_J8_15,RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ);

RF24Network network(radio);

// Constants that identifies this node
const uint16_t pi_node = 0;

// Time between checking for packets (in ms)
const unsigned long interval = 2000;
const int SAMPLE = 600; // intervallo in secondi per la memorizzazione delle temp nel db 10 minuti 10*60
const int NUM_SENSORI = 10; // definisce il numero massimo di sensori gestiti dal modulo


int main(int argc, char** argv)
{
/*	float* humidity;
	float* temperature;
	int esito_dht = pi_2_dht_read(DHT22, 18, humidity, temperature);
	printf("esito: %i; temperatura: %f; umidità: %f\n", esito_dht, temperature, humidity);
*/	
//	char sql[200];
	sqlite3 *db;
//   	char *zErrMsg = 0;
   	int rc;

//	struct tm t; /* variable for timestamp */
	char t_stamp[80];
	
	time_t rawtime;
//	time_t curtime;
   	struct tm *info;
//   	char buffer[80];
	
	int elapsed =0;

   	/* open database */
	rc = sqlite3_open("/var/www/templog.db", &db);

   	if( rc ){
      		fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
      		return(0);
   	}else{
      		fprintf(stderr, "Opened database successfully\n");
   	}


//OPEN CONFIG FILE IN OUR APPLICAITONS DIRECTORY OR CREATE IT IF IT DOESN'T EXIST
	FILE *file1;
	const char *filename1 = "sensor1.log";
	const char *filename2 = "sensor2.log";
	const char *filename3 = "sensor3.log";
	const char *filename4 = "sensor4.log";
	const char *filename5 = "sensor5.log";
	const char *filename6 = "sensor6.log";
	char filename[20];

	
	// Initialize all radio related modules
	radio.begin();
	delay(5);
	network.begin(90, pi_node);
	
	// Print some radio details (for debug purposes)
	radio.printDetails();
	printf("Ready to receive...\n");
	
	// Now do this forever (until cancelled by user)
	int i=0;
	rawtime = time(NULL);
	info = localtime( &rawtime );
	time_t timeout[NUM_SENSORI+1];
	
	for (int i=0; i< NUM_SENSORI+1; i++) {
		timeout[i]=rawtime;
		printf("timeout[%i]=%ld\n", i, timeout[i]);
	}
		
	while(1)
	{
		//clear temporary variable
		char file_data[100] = "";

		// Get the latest network info
		network.update();
		printf(".");
		fflush(stdout);
		// Enter this loop if there is data available to be read,
		// and continue it as long as there is more data to read
		while ( network.available() ) {
			RF24NetworkHeader header;
			message_t message;
			// Have a peek at the data to see the header type
			network.peek(header);
			// We can only handle the Temperature type for now
			if (header.type == 't') {
				// Read the message
				network.read(header, &message, sizeof(message));
				// Print it out
				printf("\nTemperature received from node %i: %f \n", header.from_node, message.temperature);
				printf("Humidity received from node %i: %f \n", header.from_node, message.humidity);
				   /* Create SQL statement */
/*
CREATE TABLE w_temps (timestamp DATETIME, sensor_id NUMERIC, temp NUMERIC, humidity NUMERIC);
*/

				time( &rawtime );
				info = localtime( &rawtime );
				strftime(t_stamp,80,"%Y-%m-%d %H:%M:%S", info);

				printf("Current time = %s \n", t_stamp);
				printf("Sensor ID = %i\n", header.from_node);
				
				elapsed = difftime(rawtime,timeout[header.from_node]);
				printf("elapsed = %i\n", elapsed);
				
				if (elapsed >= 0)
				{
					log_w_sensor (db, t_stamp, header.from_node, message.temperature, message.humidity);
					timeout[header.from_node] = rawtime + SAMPLE;
				}

				
				switch (header.from_node) {
					case 1:
						strcpy(filename, filename1);
						break;
					case 2:
						strcpy(filename, filename2);
						break;
					case 3:
						strcpy(filename, filename3);
						break;
					case 4:
						strcpy(filename, filename4);
						break;
					case 5:
						strcpy(filename, filename5);
						break;
					case 6:
						strcpy(filename, filename6);
						break;
					default:
						printf("identificativo del sensore non riconosciuto %i\n", header.from_node);
				}
				file1 = fopen(filename, "w");
				sprintf(file_data, "%s %f %f\n",t_stamp, message.temperature,message.humidity);
				fwrite(file_data, 1, sizeof(file_data), file1) ;
				fclose(file1);
				file1 = NULL;


//				// write temperature in shared memory
//				memcpy(shared_memory, ntoa(message.temperature), sizeof(ntoa(message.temperature)));

				
			} else {
				// This is not a type we recognize
				network.read(header, &message, sizeof(message));
				printf("Unknown message received from node %i\n", header.from_node);
			}
		}
	
		// Wait a bit before we start over again
		delay(2000);
		i=i+1;
	}

	sqlite3_close(db);

	// last thing we do before we end things
	return 0;
}
