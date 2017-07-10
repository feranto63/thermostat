dbname='/var/www/templog.db'


import sqlite3

# store the temperature in the database
def log_w_sensor (t_stamp, node_id, temp, humid)   #orario,temp, tempDHT, humidity, ExtTemp, HeatOn, TargetTemp):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    dati_da_inserire = [t_stamp, node_id, temp, humid]  #orario,temp,tempDHT,humidity, ExtTemp, HeatOn, TargetTemp]
    curs.execute("INSERT INTO w_temps values (?,?,?,?)", dati_da_inserire)
    # commit the changes
    conn.commit()
    conn.close()
    return()



	
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

				
def save_sensorlog(filename, t_stamp, temp, humidity):
    filesensor = open(filename,"w")  #apre il file di log del sensore in write mode, se il file non esiste lo crea
    #####   print (( 'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)))
    filesensor.write(t_stamp +" "+str(temp)+" "+str(humidity))
    filesensor.close()  #chiude il file dei dati e lo salva

			
##############################################

import sys
import time
import telepot
import string
import random
import os
import sys
import subprocess

import urllib3

# posto retry = 3 per evitare exception sul send.message casuale
telepot.api._pools = {
    'default': urllib3.PoolManager(num_pools=3, maxsize=10, retries=3, timeout=30),
}

#imports for thermometer reading
import os
import glob
#imports for gmail reading
import imaplib
import email

#import library for logging
import logging
logging.basicConfig(
        filename='/home/pi/BotMysController.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARN)




############ legge da file il token del Telegram Bot e della chat id

tokenpath = os.path.dirname(os.path.realpath(__file__)) + "/BotAssistant.token"
IDpath= os.path.dirname(os.path.realpath(__file__)) + "/Maggiordomo.ID"
chatidpath = os.path.dirname(os.path.realpath(__file__)) + "/BotAssistant.chatid"
#chatidgatepath = os.path.dirname(os.path.realpath(__file__)) + "/chatid_cancello"


try:
    tokenFile = open(tokenpath,'r')
    TOKEN = tokenFile.read().strip()
    tokenFile.close()
except IOError: 
    logging.error("Non ho trovato il file di token. E' necessario creare un file 'BotAssistant.token' con la token telegram per il bot. In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")
    exit()

logging.info("caricata token.")

try:
    chatidFile = open(chatidpath,'r')
    CHATID = chatidFile.read().strip()
    chatidFile.close()
except IOError: 
    logging.error("Non ho trovato il file di chatid. E' necessario creare un file 'BotAssistant.chatid' con la chatidi telegram per il bot. In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")
    exit()

logging.info("caricata chatid.")

# CHATID = 26228522

#def handle(msg):
#    flavor = telepot.flavor(msg)
#
#    summary = telepot.glance(msg, flavor=flavor)
#    print (flavor, summary)


bot = telepot.Bot(TOKEN)
# bot.message_loop(handle)
print ('running Sensor Controller ...')

myIPaddress = str(subprocess.check_output(['dig','+short','myip.opendns.com','@resolver1.opendns.com']))

import mysensors.mysensors as mysensors

ALARM_STATUS = 1

def event(message):
    global ALARM_STATUS
    """Callback for mysensors updates."""

    orario = time.localtime(time.time())
    localtime = time.asctime( orario )
    ora_minuti = time.strftime("%H:%M", orario)
	
    print("sensor_update " + str(message.node_id))
    print("message.sub_type: "+str(message.sub_type))
    print("message.payload: "+message.payload)
	
    if message.node_id == 3:
       print("message.node_id == 3")
       if message.sub_type == 16:
           print("message.sub_type == 16")
           PAYLOAD = int(message.payload)
           print("PAYLOAD = "+str(PAYLOAD))
           if PAYLOAD == ALARM_STATUS:
               print("message.payload == "+str(ALARM_STATUS))
               return()
           else:
               ALARM_STATUS = PAYLOAD
               if PAYLOAD == 0:
                   print("PAYLOAD == 0")
                   bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". E' scattato l'antifurto")
               else:
                   print("PAYLOAD == 1")
                   bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". L'antifurto si e' spento")
    else:
		if message.sub_type == 0: #it is a temperature
			sensor[message.node_id].temp = float(PAYLOAD)
			sensor[message.node_id].time = localtime
		elif message.sub_type == 1: # it is a humidity
			sensor[message.node_id].humidity = float(PAYLOAD)
			sensor[message.node_id].time = localtime

		sensorfilename = "sensor"+int(message.node_id)+".log"
		save_sensorlog(sensorfilename, sensor[message.node_id].temp, sensor[message.node_id].humidity)
	return()

		############### WORKING HERE ##################

GATEWAY = mysensors.SerialGateway('/dev/ttyMySensorsGateway', event, True)
GATEWAY.start()


# generate a name for this maggiordomo if does not exist
try:
    MaggiordomoIDFile = open(IDpath,'r')
    MaggiordomoID = MaggiordomoIDFile.read().strip()
    MaggiordomoIDFile.close()
#    bot.sendMessage(CHATID, "sono "+MaggiordomoID+". Mi sono appena svegliato")

except IOError: 
    logging.error("Non ho trovato il file con ID del maggiordomo. Genero ID e lo salvo")
    MaggiordomoID = "Maggiordomo-"+''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10)) #da generare in modo random
    MaggiordomoIDFile = open(IDpath,'w')
    MaggiordomoIDFile.write(MaggiordomoID)
    MaggiordomoIDFile.close()

#    bot.sendMessage(CHATID,"sono "+MaggiordomoID+". Sono stato appena generato")

bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". Inizio il monitoraggio dell'antifurto")

# Keep the program running.
while 1:
    time.sleep(1)
