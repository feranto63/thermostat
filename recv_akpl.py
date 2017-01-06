from nrf24 import NRF24
import time

pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio = NRF24(15,24)
radio.begin(0, 0, 17)
#radio.begin(1, 0, "P8_23", "P8_24")

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
    print recv_buffer
    c = c + 1
    if (c&1) == 0:    # queue a return payload every alternate time
        radio.writeAckPayload(1, akpl_buf, len(akpl_buf))
