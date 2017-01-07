# python da convertire

from nrf24 import NRF24
import time

pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio = NRF24()
radio.begin(0, 0, 17)

radio.setRetries(15,15)

radio.setPayloadSize(32)
radio.setChannel(0x60)
radio.setDataRate(NRF24.BR_2MBPS)
radio.setPALevel(NRF24.PA_MIN)

radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

radio.startListening()
radio.stopListening()

radio.printDetails()

radio.startListening()

c=1
while True:
	akpl_buf = [c,1, 2, 3,4,5,6,7,8,9,0,1, 2, 3,4,5,6,7,8]
    	pipe = [0]
    	# wait for incoming packet from transmitter
    	while not radio.available(pipe):
        	time.sleep(10000/1000000.0)

    	recv_buffer = []
    	radio.read(recv_buffer, radio.getDynamicPayloadSize())
    	print (recv_buffer)
    	c = c + 1
    	if (c&1) == 0:    # queue a return payload every alternate time
        	radio.writeAckPayload(1, akpl_buf, len(akpl_buf))

######################################################################## fine 	
	
#include <RF24/RF24.h>
#include <RF24Network/RF24Network.h>
#include <iostream>
#include <ctime>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

##
## g++ -L/usr/lib main.cc -I/usr/include -o main -lrrd
##

##// CE Pin, CSN Pin, SPI Speed
RF24 radio(RPI_BPLUS_GPIO_J8_15,RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ);

RF24Network network(radio);

##// Constants that identifies this node
const uint16_t pi_node = 0;

##// Time between checking for packets (in ms)
const unsigned long interval = 2000;

##// Structure of our message
struct message_t {
  float temperature;
  float humidity;
};

int main(int argc, char** argv)
{
##	// Initialize all radio related modules
	radio.begin();
	delay(5);
	network.begin(90, pi_node);
	
##	// Print some radio details (for debug purposes)
	radio.printDetails();
	printf("Ready to receive...\n");
	
##	// Now do this forever (until cancelled by user)
	while(1)
	{
##		// Get the latest network info
		network.update();
		printf(".\n");
##		// Enter this loop if there is data available to be read,
##		// and continue it as long as there is more data to read
		while ( network.available() ) {
			RF24NetworkHeader header;
			message_t message;
##			// Have a peek at the data to see the header type
			network.peek(header);
##			// We can only handle the Temperature type for now
			if (header.type == 't') {
##				// Read the message
				network.read(header, &message, sizeof(message));
##				// Print it out
				printf("Temperature received from node %i: %f \n", header.from_node, message.temperature);
				printf("Humidity received from node %i: %f \n", header.from_node, message.humidity);
			} else {
##				// This is not a type we recognize
				network.read(header, &message, sizeof(message));
				printf("Unknown message received from node %i\n", header.from_node);
			}
		}
	
##		// Wait a bit before we start over again
		delay(2000);
	}

##	// last thing we do before we end things
	return 0;
}
