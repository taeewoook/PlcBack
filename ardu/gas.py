import serial
import paho.mqtt.client as mqtt
import json

print("serial " + serial.__version__)

PORT = "COM8"
BaudRate = 9600

ARD = serial.Serial(PORT, BaudRate)


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


def Decode(A):
    return int(A[0:3])


def Ardread():
    if ARD.readable():
        code = Decode(ARD.readline())
        print(code)
        return code
    else:
        print("읽기 실패")


# 새로운 클라이언트 생성
client = mqtt.Client()
# 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_message(발행된 메세지가 들어왔을 때)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
# address : localhost, port: 1883 에 연결
client.connect("localhost", 1883)

while True:
    Ardread()
    if Ardread() > 50:
        # 메시지를 JSON 형식으로 만듭니다.
        message = {"tagId": "11", "value": "0"}
        # JSON 메시지를 문자열로 변환하여 발행합니다.
        client.publish("edukit/control", json.dumps(message), qos=1)
    else:
        # 메시지를 JSON 형식으로 만듭니다.
        message = {"tagId": "11", "value": "1"}
        # JSON 메시지를 문자열로 변환하여 발행합니다.
        client.publish("edukit/control", json.dumps(message), qos=1)
