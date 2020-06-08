import Adafruit_CharLCD as LCD
from socket import gethostbyname, gaierror
from datetime import datetime
import telepot
from telepot.loop import MessageLoop
import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import Queue

GPIO.setmode(GPIO.BCM) #BCM if not

trig1 =23	
echo1 =24	

trig2 = 20	
echo2 = 21	

trig3 = 19	
echo3 = 26

gateTrig = 17	
gateEcho = 27	

q = Queue.Queue()

GPIO.setup(trig3, GPIO.OUT)
GPIO.setup(echo3, GPIO.IN)
GPIO.setup(trig2 , GPIO.OUT)
GPIO.setup(echo2 , GPIO.IN)
GPIO.setup(trig1, GPIO.OUT)
GPIO.setup(echo1, GPIO.IN)

GPIO.setup(gateTrig , GPIO.OUT)
GPIO.setup(gateEcho , GPIO.IN)

GPIO.output(trig3, False)
GPIO.output(trig2, False)
GPIO.output(trig1, False)
GPIO.output(gateTrig, False)

lcd_rs        = 11 # 16  # Note this might need to be changed to 21 for o$
lcd_en        = 13
lcd_d4        = 6
lcd_d5        = 5
lcd_d6        = 9
lcd_d7        = 10
lcd_backlight = 4


lcd_columns = 16
lcd_rows    = 2

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows)



lcd_flag = 0

# Our "on message" event
def messageFunction (client, userdata, message):
        topic = str(message.topic)
        message = str(message.payload.decode("utf-8"))
        print(topic + message)

        message = int(message)

        if message == 1:
                lcd.clear()
                lcd.message("Car Park Full")
                print"Car Park Full"
        else:
                lcd.clear()
                lcd.message("Car Park Open")
                print "Car Park Open"


ourClient = mqtt.Client("raspClient")           # Create a MQTT client object
ourClient.connect("test.mosquitto.org", 1883)   # Connect to the test MQTT broker
ourClient.subscribe("carPark/lcd")                      # Subscribe to the topic $
ourClient.on_message = messageFunction          # Attach the messageFunction to s$
ourClient.loop_start()                          # Start the MQTT client



class slotClass:
	def __init__(self,trig,echo,slot):
                self.trig = trig
                self.echo = echo
                self.slot = slot

slot1 = slotClass(23,24,1)
slot2 = slotClass(20,21,2)
slot3 = slotClass(19,26,3)

slotList = []

slotList.append(slot1)
slotList.append(slot2)
slotList.append(slot3)

time.sleep(1)

def getAllSlots():
	slotAvList = []
	for obj in slotList:
		tempTrig = obj.trig
		tempEcho = obj.echo

	        GPIO.output(tempTrig,True)
	        time.sleep(0.00001)
	        GPIO.output(tempTrig,False)

	        while GPIO.input(tempEcho)==0:
	                start = time.time()

	        while GPIO.input(tempEcho)==1:
	                stop = time.time()

	        pDuration = stop - start

	        distance = pDuration * 17150

	        distance = round(distance,2)
	        time.sleep(1)
		slotAvList.append(distance)

	return slotAvList


def getDistance():
	GPIO.output(trig2,True)
	time.sleep(0.00001)
	GPIO.output(trig2,False)

	while GPIO.input(echo2)==0:
		start = time.time()

	while GPIO.input(echo2)==1:
		stop = time.time()

	pDuration = stop - start

	distance = pDuration * 17150

	distance = round(distance,2)
	time.sleep(1)

	return distance


def checkForVehicles():

	print "Started Check"
        GPIO.output(gateTrig,True)
        time.sleep(0.00001)
        GPIO.output(gateTrig,False)
	
	print "ECho ...."
        while GPIO.input(gateEcho)==0:
		start = time.time()

        while GPIO.input(gateEcho)==1:
		stop = time.time()

	print "Calc duartion"
        pDuration = stop - start

        distance = pDuration * 17150

        distance = round(distance,2)
        time.sleep(1)

	if distance < 8:
		publish.single("carPark/gate","3",hostname="test.mosquitto.org")


def handle(msg):
	chat_id = msg['chat']['id']
	command = msg['text']

	print "Received :"+command
	command = command.lower()

	if command=='slots':
		print "First Slots"
		slots = getAllSlots()
		print "Inside SLOTS"
		c = 0
		occpSlots = 0
		for x in slots:
			tempStatus = ""
			if x > 10:
				tempStatus = "available"
			else:
				tempStatus = "Occupied"
				occpSlots = occpSlots + 1

			print "Status: "+str(x)
			c = c + 1
			bot.sendMessage(chat_id , str("Slot ")+str(c)+str(": ")+str(tempStatus))

		if c == occSlots:
			bot.sendMessage(chat_id, str("Sorry! All slots are occupied at the moment"))

		now =datetime.now()
		current_time = now.strftime("%H:%M:%S")

		bot.sendMessage(chat_id, str('Slot availability as at ->  ')+str(current_time))

bot = telepot.Bot('1169687100:AAF5FCQMk89g7UPY8NaWMwZhRDtoXf9Pohg') #1287081843:AAGtpx_QGStf-sY9JIDdn_2W2NxraH5GzYY
print (bot.getMe())

MessageLoop(bot, handle).run_as_thread()
print('Listening.....')

def monitorSlots(q):

	my_mutex = threading.Lock()

	occSlots = 0
        slots = 0

	my_mutex.acquire()

        for obj in slotList:
                tempTrig =obj.trig
                tempEcho =obj.echo

                GPIO.setup(tempTrig , GPIO.OUT)
                GPIO.setup(tempEcho , GPIO.IN)

                GPIO.output(tempTrig,True)
                time.sleep(0.00001)
                GPIO.output(tempTrig,False)

                while GPIO.input(tempEcho)==0:
                        start = time.time()

                while GPIO.input(tempEcho)==1:
                        stop = time.time()

                pDuration = stop - start

                distance = pDuration * 17150

                distance = round(distance,2)

                slots = slots + 1

                if distance <= 10:
                        occSlots = occSlots + 1


	if slots == occSlots:
		q.put(1)
	else:
		q.put(0)


	my_mutex.release()


try:
	while(1):

		t1 = threading.Thread(target=checkForVehicles())
		t2 = threading.Thread(target=monitorSlots , args =(q,))

		t1.start()
		t2.start()

		t1.join()
		t2.join()

		result = q.get()

		print "Approaching MQTT publish"
		if(result == 1):
			publish.single("carPark/status","1",hostname="test.mosquitto.org")
		else:
			publish.single("carPark/status","0",hostname="test.mosquitto.org")


		with q.mutex:
			q.queue.clear()



except KeyboardInterrupt:
	GPIO.cleanup()


