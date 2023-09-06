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

# 새로운 클라이언트 생성
client = mqtt.Client()
# 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_message(발행된 메세지가 들어왔을 때)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
# address : localhost, port: 1883 에 연결
client.connect("localhost", 1883)
while True:
    text = ""
    # 마이크
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
            if "1" in text or "일" in text:  # 1호기 ON
                a = 9
            elif "2" in text or "이" in text:  # 2호기 ON
                a = 10
            elif "3" in text or "삼" in text:  # 3호기 ON
                a = 11
            else:  # 전체 ON
                a = 1
            b = 1
        elif "꺼" in text:
            if "1" in text or "일" in text:  # 1호기 OFF
                a = 9
            elif "2" in text or "이" in text:  # 2호기 OFF
                a = 10
            elif "3" in text or "삼" in text:  # 3호기 OFF
                a = 11
            else:
                a = 1  # 전체 OFF
            b = 0
            # 메시지를 JSON 형식으로 만듭니다.
        message = {"tagId": "%d" % a, "value": "%d" % b}
        # JSON 메시지를 문자열로 변환하여 발행합니다.
        client.publish("edukit/control", json.dumps(message), qos=1)
