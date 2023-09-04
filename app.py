from flask import Flask, jsonify, request
import pymysql

app = Flask(__name__)

# 데이터베이스 접속 설정
db = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    passwd="1234",
    db="plc",
    charset="utf8",
)


@app.route("/")
def index():
    # 데이터베이스에서 데이터 가져오기
    cursor = db.cursor()
    sql = """SELECT * FROM dice"""
    cursor.execute(sql)
    result = cursor.fetchall()

    # 데이터를 JSON 형식으로 변환하여 반환
    print(result)
    data = [{"id": row[0], "num": row[1], "created_at": row[2]} for row in result]
    return jsonify(data)


@app.route("/dice_insert", methods=["POST"])
def insert():
    # POST 요청에서 데이터 받아오기
    data = request.json  # JSON 형식의 데이터를 받아옵니다.

    # 데이터베이스에 데이터 삽입
    cursor = db.cursor()
    sql = """INSERT INTO dice (num) VALUES (%s)"""
    cursor.execute(sql, (data["num"]))
    db.commit()  # 데이터베이스에 변경 사항을 반영합니다.

    return jsonify({"message": "데이터가 삽입되었습니다."})


if __name__ == "__main__":
    app.run(debug=True)
