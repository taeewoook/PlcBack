import sys

sys.path.append("/opt/homebrew/lib/python3.9/site-packages")
import logging
import pymysql
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

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
    data = [{"id": row[0], "num": row[1], "created_at": row[2]} for row in result]
    return jsonify(data)


@app.route("/track")
def track():
    id = request.args.get("id")
    cursor = db.cursor()
    sql = """SELECT * FROM track where id = (%s)"""
    cursor.execute(sql, id)
    result = cursor.fetchone()
    data = [{"id": result[0], "start": result[1], "end": result[2]}]
    return jsonify(data)


@app.route("/track/all")
def track_all():
    cursor = db.cursor()
    sql = """SELECT * FROM track"""
    cursor.execute(sql)
    row = cursor.fetchall()

    data = [{"id": result[0], "start": result[1], "end": result[2]} for result in row]
    return jsonify(data)


@app.route("/log")
def log():
    start = request.args.get("start")
    end = request.args.get("end")
    cursor = db.cursor()
    sql = """SELECT * FROM record where Datetime between (%s) and (%s)"""
    cursor.execute(sql, (start, end))
    row = cursor.fetchall()
    data = [
        {
            "id": result[0],
            "Datetime": result[1],
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
    data = [{"id": row[0], "figure": row[1], "created_at": row[2]} for row in result]
    return jsonify(data)


@app.route("/tracklog")
def tracklog():
    track_id = request.args.get("track_id", type=int)  # 클라이언트에서 트랙 ID를 받아옵니다.

    # 트랙의 시작 및 종료 시간을 가져옵니다.
    cursor = db.cursor()
    cursor.execute("SELECT start, end FROM track WHERE id = %s", (track_id,))
    track_info = cursor.fetchone()

    if track_info is None:
        return jsonify({"error": "Track not found"})

    start_time, end_time = track_info

    # 트랙의 시작 및 종료 시간을 기반으로 레코드를 가져옵니다.
    cursor.execute(
        "SELECT * FROM record WHERE Datetime BETWEEN %s AND %s", (start_time, end_time)
    )
    records = cursor.fetchall()

    data = [
        {
            "id": result[0],
            "Datetime": result[1],
            "Start": result[2],
            "No1Action": result[3],
            "No2InPoint": result[4],
            "No3Motor1": result[5],
            "No3Motor2": result[6],
            "Dicevalue": result[7],
        }
        for result in records
    ]

    return jsonify(data)


@app.route("/page")
def page():
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
                "Datetime": row[i][1],
                "Start": row[i][2],
                "No1Action": row[i][3],
                "No2InPoint": row[i][4],
                "No3Motor1": row[i][5],
                "No3Motor2": row[i][6],
                "Dicevalue": row[i][7],
            }
        )
    if (int(num) + 1) * 50 < count:
        data["next"] = f"http://192.168.0.38:5001/page?num={int(num) + 1}"
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
