import paho.mqtt.client as mqtt
import json
import serial
import pymysql

# 데이터베이스 접속 설정
db = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    passwd="1234",
    db="plc",
    charset="utf8",
)


PORT = "COM8"
BaudRate = 9600
ARD = serial.Serial(PORT, BaudRate)


def Decode(A):
    return int(A[0:3])


def Ardread():
    if ARD.readable():
        code = Decode(ARD.readline())
        print(code)
        return code
    else:
        print("읽기 실패")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))


dice = 0


def on_message1(client, userdata, msg):
    global message
    global dice
    data = msg.payload.decode("utf-8")
    Ardread()
    if Ardread() > 50:
        message = {"tagId": "10", "value": "0"}
    else:
        message = {"tagId": "10", "value": "1"}
    data_dict = json.loads(msg.payload)
    predice = dice
    dice = data_dict["Wrapper"][38]["value"]
    # 메시지를 JSON 형식으로 만듭니다.
    dice = int(dice)
    # POST 요청에서 데이터 받아오기
    if dice > 0 and dice < 7 and dice != predice:
        print(dice)
        # 데이터베이스에 데이터 삽입
        cursor = db.cursor()
        sql = """INSERT INTO dice (num) VALUES (%s)"""
        cursor.execute(sql, dice)
        db.commit()  # 데이터베이스에 변경 사항을 반영합니다.
    if dice >= 2 and dice <= 5:
        message = {"tagId": "11", "value": "1"}
    elif dice == 1 or dice == 6:
        message = {"tagId": "11", "value": "0"}
    # JSON 메시지를 문자열로 변환하여 발행합니다.
    client.publish("edukit/control", json.dumps(message), qos=1)


def on_message2(client, userdata, msg):
    data = msg.payload.decode("utf-8")
    print(str(msg.payload.decode("utf-8")))


# 새로운 클라이언트 생성
client = mqtt.Client()
# 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_subscribe(topic 구독),
# on_message(발행된 메세지가 들어왔을 때)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.on_message = on_message1
# client.on_message = on_message2
# address : localhost, port: 1883 에 연결
client.connect("localhost", 1883)
# common topic 으로 메세지 발행
client.subscribe("edukit/robotarm", 1)

client.loop_forever()
