import sqlite3
from datetime import date

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# 모든 테이블을 확실하게 삭제하여 초기화
cursor.execute("DROP TABLE IF EXISTS logs")
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS teams")
cursor.execute("DROP TABLE IF EXISTS schedules")
cursor.execute("DROP TABLE IF EXISTS notices")
cursor.execute("DROP TABLE IF EXISTS admins")

# --- 테이블 생성 ---
# users 테이블 (employeeId는 사원의 고유 식별자 역할을 합니다)
cursor.execute('''
    CREATE TABLE users ( id INTEGER PRIMARY KEY AUTOINCREMENT, employeeId TEXT NOT NULL UNIQUE, 
        employeeName TEXT NOT NULL, birthDate TEXT NOT NULL )
''')
# (다른 테이블 생성 코드는 이전과 동일)
cursor.execute('''
    CREATE TABLE logs ( id INTEGER PRIMARY KEY AUTOINCREMENT, employeeName TEXT NOT NULL, date TEXT NOT NULL,
        workHours INTEGER NOT NULL, safetyCheck TEXT NOT NULL, source TEXT NOT NULL )
''')
cursor.execute('''
    CREATE TABLE teams ( id INTEGER PRIMARY KEY AUTOINCREMENT, teamName TEXT NOT NULL UNIQUE )
''')
cursor.execute('''
    CREATE TABLE schedules ( id INTEGER PRIMARY KEY AUTOINCREMENT, scheduleDate TEXT NOT NULL,
        employeeId TEXT NOT NULL, teamName TEXT NOT NULL )
''')
cursor.execute('''
    CREATE TABLE notices ( id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
        content TEXT NOT NULL, createdAt TEXT NOT NULL )
''')
cursor.execute('''
    CREATE TABLE admins ( id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE, password TEXT NOT NULL )
''')


# --- 테스트 데이터 삽입 (총 6명으로 확장) ---
today_str = date.today().strftime('%Y-%m-%d')

# ▼▼▼ 사원 데이터를 총 6명으로 늘렸습니다 ▼▼▼
# RFID 사용자 2명
cursor.execute("INSERT INTO users (employeeId, employeeName, birthDate) VALUES (?, ?, ?)", ('427226311070', '김민효', '041208')) # 흰색 고리x
cursor.execute("INSERT INTO users (employeeId, employeeName, birthDate) VALUES (?, ?, ?)", ('566518748246', '박관령', '020811')) # 파란색 고리 O
# QR 코드 사용자 6명
cursor.execute("INSERT INTO users (employeeId, employeeName, birthDate) VALUES (?, ?, ?)", ('user003', '김태현', '990409'))
cursor.execute("INSERT INTO users (employeeId, employeeName, birthDate) VALUES (?, ?, ?)", ('user004', '이상윤', '980121'))
cursor.execute("INSERT INTO users (employeeId, employeeName, birthDate) VALUES (?, ?, ?)", ('user005', '신대혁', '971115'))
cursor.execute("INSERT INTO users (employeeId, employeeName, birthDate) VALUES (?, ?, ?)", ('user006', '홍인혁', '011201'))
cursor.execute("INSERT INTO users (employeeId, employeeName, birthDate) VALUES (?, ?, ?)", ('user007', '이규빈', '000718'))
cursor.execute("INSERT INTO users (employeeId, employeeName, birthDate) VALUES (?, ?, ?)", ('user008', '이다빈', '980806'))

# ▲▲▲

# 관리자 데이터
cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ('admin', 'qwer1234'))

# 팀 데이터
cursor.execute("INSERT INTO teams (teamName) VALUES (?)", ('A팀',))
cursor.execute("INSERT INTO teams (teamName) VALUES (?)", ('B팀',))
cursor.execute("INSERT INTO teams (teamName) VALUES (?)", ('C팀',))

# ▼▼▼ 스케줄 데이터도 늘어난 사원에 맞게 보강했습니다 ▼▼▼
cursor.execute("INSERT INTO schedules (scheduleDate, employeeId, teamName) VALUES (?, ?, ?)", (today_str, '427226311070', '설비1팀'))
cursor.execute("INSERT INTO schedules (scheduleDate, employeeId, teamName) VALUES (?, ?, ?)", (today_str, 'user003', '설비1팀'))
cursor.execute("INSERT INTO schedules (scheduleDate, employeeId, teamName) VALUES (?, ?, ?)", (today_str, 'user004', '설비1팀'))

cursor.execute("INSERT INTO schedules (scheduleDate, employeeId, teamName) VALUES (?, ?, ?)", (today_str, '566518748246', '품질1팀'))
cursor.execute("INSERT INTO schedules (scheduleDate, employeeId, teamName) VALUES (?, ?, ?)", (today_str, 'user005', '품질1팀'))
cursor.execute("INSERT INTO schedules (scheduleDate, employeeId, teamName) VALUES (?, ?, ?)", (today_str, 'user008', '품질1팀'))

cursor.execute("INSERT INTO schedules (scheduleDate, employeeId, teamName) VALUES (?, ?, ?)", (today_str, 'user006', '안전2팀'))
cursor.execute("INSERT INTO schedules (scheduleDate, employeeId, teamName) VALUES (?, ?, ?)", (today_str, 'user007', '안전2팀'))

# ▲▲▲

# ▼▼▼ 근무 기록 데이터도 보강했습니다 ▼▼▼
cursor.execute("INSERT INTO logs (employeeName, date, workHours, safetyCheck, source) VALUES (?, ?, ?, ?, ?)",
               ('김민효', today_str, 8, '양호', 'system'))
cursor.execute("INSERT INTO logs (employeeName, date, workHours, safetyCheck, source) VALUES (?, ?, ?, ?, ?)",
               ('이다빈', today_str, 8, '불량', 'system'))
# ▲▲▲
               
# 공지사항 데이터
cursor.execute("INSERT INTO notices (title, content, createdAt) VALUES (?, ?, ?)",
               ('전체 공지: 안전 장비 착용 필수 안내', '모든 현장 인원은 안전모 및 안전화를 반드시 착용해 주시기 바랍니다.', today_str))

connection.commit()
connection.close()

print("데이터베이스가 성공적으로 초기화되었습니다. 총 8명의 사원 데이터가 적용되었습니다.")

