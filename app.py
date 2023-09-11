# import sys
# sys.path.append('/opt/homebrew/lib/python3.9/site-packages')
import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

# 데이터베이스 접속 설정
db = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    passwd="1234",
    db="PLC",
    charset="utf8",
)


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


if __name__ == "__main__":
    app.run(debug=True)
