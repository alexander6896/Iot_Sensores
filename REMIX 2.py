#Libraries
import RPi.GPIO as GPIO
import os
import glob
import time
import paho.mqtt.publish as publish


#TEMPERATURA 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
_direccion = '/sys/bus/w1/devices/'
dispositivo_folder = glob.glob(_direccion + '28*')[0]
dispositivo_pad = dispositivo_folder + '/w1_slave'

#ULTRA
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18 #ETIQUETA (FISICO 12)
GPIO_ECHO = 24    #ETIQUETA (FISICO 18)
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)



#FUNCIONES TEMPERATURA
def leer_temperatura():
    f = open(dispositivo_pad, 'r')
    lineas = f.readlines()
    f.close()
    return lineas
 
def determinar_valores():
    lineas = leer_temperatura()
    while lineas[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lineas = leer_temperatura()
    igual_pos = lineas[1].find('t=')
    if igual_pos != -1:
        temp_string = lineas[1][igual_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        #return temp_c, temp_f
        return temp_c


#FUNCIONES DISTANCIA
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
    
if __name__ == '__main__':
    try:
        while True:
            #DISTANCIA
            dist = distance()
            print ("Measured Distance = %.1f cm" % dist)
            #TEMPERATURA
            print("Centigrados,Farenheith")
            temperatura = determinar_valores()
            print(temperatura)
            #Parseamos a String
            distStr = str(dist)
            tempStr = str(temperatura)
            #Concatenamos cadena de String
            datos = (distStr+" "+tempStr)
            print("Los datos conca son: "+datos)
            publish.single("CoreE/test", datos, hostname="192.168.1.68")
            
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

	
