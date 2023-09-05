import pymysql
import schedule
import time

# 데이터베이스 접속 설정
db = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    passwd="1234",
    db="plc",
    charset="utf8",
)


# 데이터베이스 관련 함수 정의
def delete_day_contaminated():
    # 데이터베이스에서 데이터 가져오기
    cursor = db.cursor()
    # 여기에서 day_tuna 테이블을 초기화하는 쿼리를 실행합니다.
    cursor.execute("DELETE FROM day_contaminated")
    db.commit()


def delete_day_amount():
    # 데이터베이스에서 데이터 가져오기
    cursor = db.cursor()
    # 여기에서 day_tuna 테이블을 초기화하는 쿼리를 실행합니다.
    cursor.execute("DELETE FROM day_amount")
    db.commit()


# 스케줄링 작업 정의
def scheduled_job():
    delete_day_amount()
    delete_day_contaminated()
    print("스케줄링 작업 실행")


# 스케줄링 설정: 매일 00:00에 scheduled_job 함수 실행
schedule.every().day.at("00:00").do(scheduled_job)

# 스케줄링 루프 실행
while True:
    schedule.run_pending()
    time.sleep(1)
