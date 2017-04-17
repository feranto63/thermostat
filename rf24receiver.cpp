#include <RF24/RF24.h>
#include <RF24Network/RF24Network.h>
#include <iostream>
#include <ctime>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

// gestione DHT xx Adafruit
#include <stdbool.h>

#include "pi_2_dht_read.h"
#include "pi_2_mmio.h"




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
	printf("a\n");
   	rc = sqlite3_exec(db, sql, callback, 0, &zErrMsg);
	printf("b\n");
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
const int NUM_SENSORI = 100; // definisce il numero massimo di sensori gestiti dal modulo


int main(int argc, char** argv)
{
	sqlite3 *db;
   	int rc;

	char t_stamp[80];
	
	time_t rawtime;
   	struct tm *info;
	
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
	const char *filename7 = "sensor7.log";
	const char *filename8 = "sensor8.log";
	const char *filename9 = "sensor2.log"; // solo per piero per gestire il figloio child come primario
	const char *filename10 = "sensor10.log";
	const char *filename11 = "sensor11.log";
	const char *filename12 = "sensor12.log";
	const char *filename13 = "sensor13.log";
	const char *filename14 = "sensor14.log";
	const char *filename15 = "sensor15.log";
	const char *filename16 = "sensor16.log";
	const char *filename17 = "sensor17.log";
	const char *filename18 = "sensor18.log";
	const char *filename19 = "sensor19.log";
	const char *filename20 = "sensor20.log";
	const char *filename21 = "sensor21.log";
	const char *filename22 = "sensor22.log";
	const char *filename23 = "sensor23.log";
	const char *filename24 = "sensor24.log";
	const char *filename25 = "sensor25.log";
	const char *filename26 = "sensor26.log";
	const char *filename27 = "sensor27.log";
	const char *filename28 = "sensor28.log";
	char filename[20];

	
	// Initialize all radio related modules
	radio.begin();
	delay(5);
	network.begin(90, pi_node);
	
	// Print some radio details (for debug purposes)
	radio.printDetails();
	printf("Ready to receive...\n");
	
	// Now do this forever (until cancelled by user)
	// int i=0;
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

				strcpy(filename, "sensor_strange.log");
				
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
					case 7:
						strcpy(filename, filename7);
						break;
					case 8:
						strcpy(filename, filename8);
						break;
					case 9:
						strcpy(filename, filename9);
						break;
					case 10:
						strcpy(filename, filename10);
						break;
					case 11:
						strcpy(filename, filename11);
						break;
					case 12:
						strcpy(filename, filename12);
						break;
					case 13:
						strcpy(filename, filename13);
						break;
					case 14:
						strcpy(filename, filename14);
						break;
					case 15:
						strcpy(filename, filename15);
						break;
					case 16:
						strcpy(filename, filename16);
						break;
					case 17:
						strcpy(filename, filename17);
						break;
					case 18:
						strcpy(filename, filename18);
						break;
					case 19:
						strcpy(filename, filename19);
						break;
					case 20:
						strcpy(filename, filename20);
						break;
					case 21:
						strcpy(filename, filename21);
						break;
					case 22:
						strcpy(filename, filename22);
						break;
					case 23:
						strcpy(filename, filename23);
						break;
					case 24:
						strcpy(filename, filename24);
						break;
					case 25:
						strcpy(filename, filename25);
						break;
					case 26:
						strcpy(filename, filename26);
						break;
					case 27:
						strcpy(filename, filename27);
						break;
					case 28:
						strcpy(filename, filename28);
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
		// i=i+1;
	}

	sqlite3_close(db);

	// last thing we do before we end things
	return 0;
}
