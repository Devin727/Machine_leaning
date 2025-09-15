import sqlite3
from datetime import date

# 데이터베이스 연결
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

# logs 테이블: 근무 기록 저장
cursor.execute('''
    CREATE TABLE logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employeeName TEXT NOT NULL,
        date TEXT NOT NULL,
        workHours INTEGER NOT NULL,
        safetyCheck TEXT NOT NULL,
        source TEXT NOT NULL
    )
''')

# users 테이블: 사원 정보 저장 (고유 ID 포함)
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employeeId TEXT NOT NULL UNIQUE,
        employeeName TEXT NOT NULL,
        birthDate TEXT NOT NULL
    )
''')

# teams 테이블: 팀 정보 저장
cursor.execute('''
    CREATE TABLE teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teamName TEXT NOT NULL UNIQUE
    )
''')

# schedules 테이블: 날짜별 근무 조 편성 저장
cursor.execute('''
    CREATE TABLE schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheduleDate TEXT NOT NULL,
        employeeId TEXT NOT NULL,
        teamName TEXT NOT NULL
    )
''')

# notices 테이블: 공지사항 저장
cursor.execute('''
    CREATE TABLE notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        createdAt TEXT NOT NULL
    )
''')

# admins 테이블: 관리자 계정 저장
cursor.execute('''
    CREATE TABLE admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

# --- 테스트 데이터 삽입 ---

today_str = date.today().strftime('%Y-%m-%d')

# 사원 데이터
cursor.execute("INSERT INTO users (employeeId, employeeName, birthDate) VALUES (?, ?, ?)", ('user001', '김민준', '900101'))
cursor.execute("INSERT INTO users (employeeId, employeeName, birthDate) VALUES (?, ?, ?)", ('user002', '이서아', '951225'))
cursor.execute("INSERT INTO users (employeeId, employeeName, birthDate) VALUES (?, ?, ?)", ('user003', '박도윤', '920315'))

# 관리자 데이터
cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ('admin', '1234'))

# 팀 데이터
cursor.execute("INSERT INTO teams (teamName) VALUES (?)", ('A팀',))
cursor.execute("INSERT INTO teams (teamName) VALUES (?)", ('B팀',))

# 스케줄 데이터 (오늘 날짜 기준)
cursor.execute("INSERT INTO schedules (scheduleDate, employeeId, teamName) VALUES (?, ?, ?)", (today_str, 'user001', 'A팀'))
cursor.execute("INSERT INTO schedules (scheduleDate, employeeId, teamName) VALUES (?, ?, ?)", (today_str, 'user002', 'A팀'))
cursor.execute("INSERT INTO schedules (scheduleDate, employeeId, teamName) VALUES (?, ?, ?)", (today_str, 'user003', 'B팀'))

# 근무 기록 데이터 (오늘 날짜 기준)
cursor.execute("INSERT INTO logs (employeeName, date, workHours, safetyCheck, source) VALUES (?, ?, ?, ?, ?)",
               ('김민준', today_str, 8, '양호', 'system'))
cursor.execute("INSERT INTO logs (employeeName, date, workHours, safetyCheck, source) VALUES (?, ?, ?, ?, ?)",
               ('박도윤', today_str, 9, '양호', 'system'))
               
# 공지사항 데이터
cursor.execute("INSERT INTO notices (title, content, createdAt) VALUES (?, ?, ?)",
               ('전체 공지: 안전 장비 착용 필수 안내', '모든 현장 인원은 안전모 및 안전화를 반드시 착용해 주시기 바랍니다.', today_str))

# 변경사항 저장 및 연결 종료
connection.commit()
connection.close()

print("데이터베이스가 성공적으로 초기화되었습니다. 모든 테이블과 최신 테스트 데이터가 생성되었습니다.")

