#include <RF24/RF24.h>
#include <RF24Network/RF24Network.h>
#include <iostream>
#include <ctime>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>


#include <sqlite3.h> 



static int callback(void *NotUsed, int argc, char **argv, char **azColName){
   int i;
   for(i=0; i<argc; i++){
      printf("%s = %s\n", azColName[i], argv[i] ? argv[i] : "NULL");
   }
   printf("\n");
   return 0;
}


/**
 * g++ -L/usr/lib main.cc -I/usr/include -o main -lrrd
 **/

// CE Pin, CSN Pin, SPI Speed
RF24 radio(RPI_BPLUS_GPIO_J8_15,RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ);

RF24Network network(radio);

// Constants that identifies this node
const uint16_t pi_node = 0;

// Time between checking for packets (in ms)
const unsigned long interval = 2000;

// Structure of our message
struct message_t {
  float temperature;
  float humidity;
};

int main(int argc, char** argv)
{

	char sql[200];
	sqlite3 *db;
   	char *zErrMsg = 0;
   	int rc;

	struct tm t; /* variable for timestamp */
	char t_stamp[80];
	
	time_t rawtime;
	time_t curtime;
   	struct tm *info;
   	char buffer[80];

   	/* open database */
	rc = sqlite3_open("/var/www/templog.db", &db);

   	if( rc ){
      		fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
      		return(0);
   	}else{
      		fprintf(stderr, "Opened database successfully\n");
   	}

// shared memory section
	int shmid;
	// give your shared memory an id, anything will do
	key_t key = 123456;
	char *shared_memory;

	// Setup shared memory, 11 is the size
	if ((shmid = shmget(key, 11, IPC_CREAT | 0666)) < 0)
	{
		printf("Error getting shared memory id");
		exit(1);
	}
	// Attached shared memory
	if ((shared_memory = shmat(shmid, NULL, 0)) == (char *) -1)
	{
		printf("Error attaching shared memory id");
   		exit(1);
   	}
	// copy "hello world" to shared memory
	memcpy(shared_memory, "Hello World", sizeof("Hello World"));
	// sleep so there is enough time to run the reader!
	//sleep(10);
	// Detach and remove shared memory
	//shmdt(shmid);
	//shmctl(shmid, IPC_RMID, NULL);
	
	// Initialize all radio related modules
	radio.begin();
	delay(5);
	network.begin(90, pi_node);
	
	// Print some radio details (for debug purposes)
	radio.printDetails();
	printf("Ready to receive...\n");
	
	// Now do this forever (until cancelled by user)
	int i=0;
	while(1)
	{
		// Get the latest network info
		network.update();
		printf(".");
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

				printf("Current time = %s", t_stamp);

				sprintf(sql,"INSERT INTO 'w_temps' VALUES ('%s', %i, %f, %f);", t_stamp, header.from_node, message.temperature,message.humidity);
				printf(sql);
   				/* Execute SQL statement */
   				rc = sqlite3_exec(db, sql, callback, 0, &zErrMsg);
   				if( rc != SQLITE_OK ){
      					fprintf(stderr, "SQL error: %s\n", zErrMsg);
      					sqlite3_free(zErrMsg);
   				}else{
      					fprintf(stdout, "Records created successfully\n");
   				}
				
				// write temperature in shared memory
				memcpy(shared_memory, str(message.temperature), sizeof(str(message.temperature)));

				
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
