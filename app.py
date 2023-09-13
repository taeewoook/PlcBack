import logging
import pymysql
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from datetime import datetime
import threading

lock = threading.Lock()

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
logging.getLogger("flask_cors").level = logging.DEBUG

# 데이터베이스 접속 설정
db = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    passwd="1234",
    db="PLC",
    charset="utf8",
)


@app.route("/")
def home():
    return "Hello World"


@app.route("/dice")
def index():
    # 데이터베이스에서 데이터 가져오기
    start = request.args.get("start")
    end = request.args.get("end")
    cursor = db.cursor()
    sql = """SELECT * FROM dice where created_at between (%s) and (%s)"""
    cursor.execute(sql, (start, end))
    result = cursor.fetchall()
    # 데이터를 JSON 형식으로 변환하여 반환
    data = [
        {
            "id": row[0],
            "num": row[1],
            "created_at": datetime.strftime(row[2], "%Y/%m/%d %H:%M:%S"),
        }
        for row in result
    ]
    data = [
        {
            "id": row[0],
            "num": row[1],
            "created_at": datetime.strftime(row[2], "%Y/%m/%d %H:%M:%S"),
        }
        for row in result
    ]
    return jsonify(data)


@app.route("/track")
def track():
    id = request.args.get("id")
    cursor = db.cursor()
    sql = """SELECT * FROM track where id = (%s)"""
    cursor.execute(sql, id)
    result = cursor.fetchone()
    data = [
        {
            "id": result[0],
            "start": datetime.strftime(result[1], "%Y/%m/%d %H:%M:%S"),
            "end": datetime.strftime(result[1], "%Y/%m/%d %H:%M:%S"),
        }
    ]

    return jsonify(data)


@app.route("/track/all")
def track_all():
    cursor = db.cursor()
    sql = """SELECT * FROM track"""
    cursor.execute(sql)
    row = cursor.fetchall()

    data = [
        {
            "id": result[0],
            "start": datetime.strftime(result[1], "%Y/%m/%d %H:%M:%S"),
            "end": datetime.strftime(result[2], "%Y/%m/%d %H:%M:%S"),
        }
        for result in row
    ]

    return jsonify(data)


@app.route("/log")
def log():
    trackid = request.args.get("track")
    cursor = db.cursor()
    sql = """SELECT * FROM record where TrackId = (%s)"""
    cursor.execute(sql, (trackid))
    row = cursor.fetchall()
    data = [
        {
            "id": result[0],
            "Datetime": datetime.strftime(result[1], "%Y/%m/%d %H:%M:%S"),
            "Start": result[2],
            "No1Action": result[3],
            "No2InPoint": result[4],
            "No3Motor1": result[5],
            "No3Motor2": result[6],
            "Dicevalue": result[7],
        }
        for result in row
    ]

    return jsonify(data)


@app.route("/radiation")
def radiation():
    cursor = db.cursor()
    sql = """SELECT * from radiation"""
    cursor.execute(sql)
    result = cursor.fetchall()
    data = [
        {
            "id": row[0],
            "figure": row[1],
            "created_at": datetime.strftime(row[2], "%Y/%m/%d %H:%M:%S"),
        }
        for row in result
    ]

    return jsonify(data)


@app.route("/page")
def page():
    with lock:
        cursor = db.cursor()
        sql = """select count(*) from record"""
        cursor.execute(sql)
        count = cursor.fetchone()[0]
        data = {"count": f"{count}", "results": [], "next": None}
        num = request.args.get("num")
        sql = """select * from record where id <= (select count(*) from record) - (50 * (%s)) order by id desc limit 50"""
        cursor.execute(sql, num)
        row = cursor.fetchall()
        for i in range(len(row)):
            data["results"].append(
                {
                    "id": row[i][0],
                    "Datetime": datetime.strftime(row[i][1], "%Y/%m/%d %H:%M:%S"),
                    "TrackId": row[i][8],
                    "Start": row[i][2],
                    "No1Action": row[i][3],
                    "No2InPoint": row[i][4],
                    "No3Motor1": row[i][5],
                    "No3Motor2": row[i][6],
                    "Dicevalue": row[i][7],
                }
            )
        if (int(num) + 1) * 50 < count:
            data["next"] = f"http://192.168.0.128:5001/page?num={int(num) + 1}"
        return jsonify(data)


@app.route("/tracklog")
def tracklog():
    with lock:
        track_id = request.args.get("track_id", type=int)  # 클라이언트에서 트랙 ID를 받아옵니다.
        # 트랙의 시작 및 종료 시간을 가져옵니다.
        # 트랙의 시작 및 종료 시간을 기반으로 레코드를 가져옵니다.
        data = {"results": [], "dice": None, "radiation": None}
        if not track_id:
            return jsonify(data)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM record WHERE TrackId = %s", (track_id))
        row = cursor.fetchall()
        for i in range(len(row)):
            data["results"].append(
                {
                    "id": row[i][0],
                    "Datetime": datetime.strftime(row[i][1], "%Y/%m/%d %H:%M:%S"),
                    "TrackId": row[i][8],
                    "Start": row[i][2],
                    "No1Action": row[i][3],
                    "No2InPoint": row[i][4],
                    "No3Motor1": row[i][5],
                    "No3Motor2": row[i][6],
                    "Dicevalue": row[i][7],
                }
            )
        sql = "SELECT * FROM dice WHERE TrackId = %s"
        cursor.execute(sql, track_id)
        row = cursor.fetchone()
        if row:
            if row[1] == 1:
                data["dice"] = "규격미달"
            elif row[1] == 6:
                data["dice"] = "규격초과"
            else:
                data["dice"] = "정상"
        sql = "SELECT * FROM radiation WHERE TrackId = %s"
        cursor.execute(sql, track_id)
        row = cursor.fetchone()
        if row:
            data["radiation"] = row[1]
        return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
