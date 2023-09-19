import speech_recognition as sr
import sys
import io
import paho.mqtt.client as mqtt
import json


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))


def on_message(client, userdata, msg):
    data = msg.payload.decode("utf-8")
    print(str(msg.payload.decode("utf-8")))


# -*- coding: euc-kr -*-
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding="utf-8")

r = sr.Recognizer()

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect("localhost", 1883)
while True:
    text = ""
    with sr.Microphone() as source:
        print("말해보셈", flush=True)
        audio = r.listen(source)
        print("확인", flush=True)

    try:
        text = r.recognize_google(audio, language="ko-KR")
        print("You Said: {}".format(text), flush=True)
    except:
        print("인식못함", flush=True)

    a = 0
    b = 0
    print(text)
    if "켜" in text or "꺼" in text:
        if "켜" in text:
            if "1" in text or "일" in text:
                a = 9
            elif "2" in text or "이" in text:
                a = 10
            elif "3" in text or "삼" in text:
                a = 11
            else:
                a = 1
            b = 1
        elif "꺼" in text:
            if "1" in text or "일" in text:
                a = 9
            elif "2" in text or "이" in text:
                a = 10
            elif "3" in text or "삼" in text:
                a = 11
            else:
                a = 1
            b = 0
        message = {"tagId": "%d" % a, "value": "%d" % b}
        client.publish("edukit/control", json.dumps(message), qos=1)
