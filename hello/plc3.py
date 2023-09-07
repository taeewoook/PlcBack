import paho.mqtt.client as mqtt
import json
import serial
import pymysql
import cv2
import numpy as np
from socket import *
from select import *
from time import sleep
from datetime import datetime, timedelta

# 교육키트 IP
HOST = "192.168.0.120"
# 교육키트 Port
PORT = 2004
BUFSIZE = 1024
ADDR = (HOST, PORT)


def dice_recognition():
    cap = cv2.VideoCapture(1)  # 0 or 1
    readings = [-1, -1]
    display = [0, 0]

    Circle_Inertia = 0.6
    Gaussian_ksize = (7, 7)
    canny_threshold_min = 100
    canny_threshold_max = 250

    params = cv2.SimpleBlobDetector_Params()
    params.filterByInertia = True
    params.minInertiaRatio = Circle_Inertia

    detector = cv2.SimpleBlobDetector_create(params)

    while True:
        ret, frame = cap.read()
        # print(cap.read())
        frame_blurred = cv2.GaussianBlur(frame, Gaussian_ksize, 1)
        frame_gray = cv2.cvtColor(frame_blurred, cv2.COLOR_BGR2GRAY)
        frame_canny = cv2.Canny(
            frame_gray,
            canny_threshold_min,
            canny_threshold_max,
            apertureSize=3,
            L2gradient=True,
        )

        keypoints = detector.detect(frame_canny)
        num = len(keypoints)
        readings.append(num)

        # print(readings)
        if (
            readings[-1]
            == readings[-2]
            == readings[-3]
            == readings[-4]
            == readings[-5]
            == readings[-6]
        ):
            im_with_keypoints = cv2.drawKeypoints(
                frame,
                keypoints,
                np.array([]),
                (0, 0, 255),
                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
            )
            cv2.putText(
                im_with_keypoints,
                str(num),
                (500, 250),
                cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                5,
                (0, 255, 0),
            )
            socketTxData = bytes(
                [
                    76,
                    83,
                    73,
                    83,
                    45,
                    88,
                    71,
                    84,
                    0,
                    0,
                    0,
                    0,
                    160,
                    51,
                    0,
                    0,
                    22,
                    0,
                    0,
                    0,
                    88,
                    0,
                    2,
                    0,
                    0,
                    0,
                    1,
                    0,
                    8,
                    0,
                    37,
                    68,
                    87,
                    48,
                    49,
                    49,
                    48,
                    48,
                    2,
                    0,
                ]
            )
            num_little = num.to_bytes(2, "little")

            if num != 0:
                print("num is " + str(num))
                try:
                    clientSocket = socket(AF_INET, SOCK_STREAM)
                    clientSocket.connect(ADDR)
                    print("Connection PLC Success!")
                    clientSocket.send(socketTxData + num_little)
                    clientSocket.close()
                except Exception as e:
                    print("Error" + str(e))
            # cv2.imwrite("After.png", im_with_keypoints)
            return num
            # print("close PLC Success!")
            # sleep(1)


# 데이터베이스 접속 설정
db = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    passwd="1234",
    db="plc",
    charset="utf8",
)


# PORT = "COM8"
# BaudRate = 9600
# ARD = serial.Serial(PORT, BaudRate)


# def Decode(A):
#     return int(A[0:3])


# def Ardread():
#     if ARD.readable():
#         code = Decode(ARD.readline())
#         print(code)
#         return code
#     else:
#         print("읽기 실패")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))


message = {"tagId": "12", "value": "1"}
dice = 0

mflag = True
trackflag = True


def on_message1(client, userdata, msg):
    global mflag
    global message
    global dice
    global trackflag
    data = msg.payload.decode("utf-8")
    # Ardread()
    # if Ardread() > 50:
    #     message = {"tagId": "11", "value": "0"}
    #     client.publish("edukit/control", json.dumps(message), qos=1)
    # else:
    #     message = {"tagId": "11", "value": "1"}
    #     client.publish("edukit/control", json.dumps(message), qos=1)
    data_dict = json.loads(msg.payload)
    if data_dict["Wrapper"][2]["value"] and trackflag:
        print("ok")
        trackflag = False
        dataTime = datetime.strptime(
            data_dict["Wrapper"][40]["value"], "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        cursor = db.cursor()
        start_time = dataTime
        end_time = start_time + timedelta(seconds=25)
        sql = "INSERT INTO track (start, end) VALUES (%s, %s)"
        cursor.execute(sql, (start_time, end_time))
        db.commit()
    if data_dict["Wrapper"][2]["value"] == False:
        trackflag = True
    predice = dice
    dice = dice_recognition()
    # x = data_dict["Wrapper"][34]["value"]
    # y = data_dict["Wrapper"][35]["value"]
    # 메시지를 JSON 형식으로 만듭니다.
    # dice = int(dice)
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
        mflag = False
    elif dice == 1 or dice == 6:
        message = {"tagId": "11", "value": "0"}
        mflag = False
    # JSON 메시지를 문자열로 변환하여 발행합니다.
    if mflag == False:
        client.publish("edukit/control", json.dumps(message), qos=1)
        mflag = True


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
