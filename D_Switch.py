import subprocess
import time

import RPi.GPIO as GPIO
from Data import Details

from Mqtt_Module.mqtt import mqtt_mod

username_mqtt=Details["username_mqtt"]
password_mqtt=Details["password_mqtt"]
mqtt_broker=Details["mqtt_broker"]
mqtt_port=Details["mqtt_port"]
Publish_Topic=Details["Publish_Topic"]
HeartBeat_Topic_Suffix=Details["HeartBeat_Topic_Suffix"]
Data_Topic_Suffix=Details["Data_Topic_Suffix"]
Main_Location=Details["Main_Location"]
HB_time=Details["HB_time"]
Main_Loop_Interval=Details["Main_Loop_Interval"]
MqTT=mqtt_mod(username_mqtt,password_mqtt,mqtt_broker,mqtt_port,Publish_Topic,HeartBeat_Topic_Suffix,Data_Topic_Suffix)
Program_Version=0.1
# Main_Loop_Interval=.2
# HB_time=60
HB_Mul=HB_time/Main_Loop_Interval
HB_Time_Interval=Main_Loop_Interval*HB_Mul





Er=0
C1=0
NO_button = 16
NC_button = 18

def Get_IP_Address():
    c=0
    with open("/etc/dhcpcd.conf", 'r') as outfile:
        f=outfile.read()
        fdata=f.split()
        for i in fdata:
            if i =="eth0":
                c=1
            if i == "static" and c==1:
                c=2
            if "ip_address" in i and c==2 :
                ip_line=i[:-3]
                c=0
        IP_Address=ip_line.split('.')[-1]
        if len(IP_Address) <3:
            IP_Address='0{}'.format(IP_Address)
            return IP_Address

Device_ID=Get_IP_Address()



def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(NO_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(NC_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def MQtt_Publisher(Msg_To_Publish,EdgeID):
    MqTT_State,client=MqTT.MQTT_Connect()
    time.sleep(0.01)
    if MqTT_State:
        print("Mqtt is {}_{}".format(str(MqTT_State),str(client)))
        pub_state,pub_error=MqTT.Publish_Data(client,EdgeID,Message=Msg_To_Publish)
        print("Publish is {}_{}".format(str(pub_state),str(pub_error)))
        MqTT.MQTT_Disconnect(client)
        MqTT_State=False
    else:
        print(str(client))
        # MqTT_State,client=MqTT.MQTT_Connect()


def loop():
    while True:
        time.sleep(0.05)
        try:
            NO_button_state = GPIO.input(NO_button)
            NC_button_state = GPIO.input(NC_button)
            if  NC_button_state == True:
                print('NC_button(RED)    Pressed...')
                jsondata='{{"Device_ID":{},"button":1,"Time":"{}"}}'.format(Device_ID,time.strftime("%Y-%m-%dT%X"))
                jsondata=jsondata.replace("'",'"')
                MQtt_Publisher(Msg_To_Publish=jsondata,EdgeID=Device_ID)
                time.sleep(1)
            if  NO_button_state == False:
                print('NO_button(GREEN)  Pressed...')
                jsondata='{{"Device_ID":{},"button":2,"Time":"{}"}}'.format(Device_ID,time.strftime("%Y-%m-%dT%X"))
                jsondata=jsondata.replace("'",'"')
                MQtt_Publisher(Msg_To_Publish=jsondata,EdgeID=Device_ID)
                time.sleep(1)
                # while GPIO.input(NO_button) == False:
                    # time.sleep(0.2)
        except Exception as df:
            print(df)

def endprogram():
    GPIO.cleanup()


if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        print ('keyboard interrupt detected' )
        endprogram()
