import sqlite3
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime, date

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_very_secret_key_here'

# --- 데이터베이스 연결 ---
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- API 엔드포인트 ---

# 사원별 로그 필터링 기능이 추가된 로그 조회 API
@app.route('/api/logs', methods=['GET'])
def get_logs():
    employee_name = request.args.get('employeeName')
    conn = get_db_connection()
    if employee_name:
        logs_rows = conn.execute('SELECT * FROM logs WHERE employeeName = ? ORDER BY id DESC', (employee_name,)).fetchall()
    else:
        logs_rows = conn.execute('SELECT * FROM logs ORDER BY id DESC').fetchall()
    conn.close()
    logs = [dict(row) for row in logs_rows]
    return jsonify(logs)

# 수동 로그 추가 API
@app.route('/api/add_log', methods=['POST'])
def add_log():
    new_log = request.json
    date = datetime.now().strftime('%Y-%m-%d')
    source = 'manual'
    conn = get_db_connection()
    conn.execute('INSERT INTO logs (employeeName, workHours, safetyCheck, date, source) VALUES (?, ?, ?, ?, ?)',
                 (new_log['employeeName'], new_log['workHours'], new_log['safetyCheck'], date, source))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Log added successfully'})

# 사원 로그인 API (employeeId 세션 저장)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    name = data.get('employeeName')
    birth_date = data.get('birthDate')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE employeeName = ? AND birthDate = ?', 
                        (name, birth_date)).fetchone()
    conn.close()
    if user:
        session['employeeId'] = user['employeeId']
        session['employeeName'] = user['employeeName']
        return jsonify({'status': 'success', 'message': 'Login successful'})
    else:
        return jsonify({'status': 'error', 'message': '이름 또는 생년월일이 일치하지 않습니다.'})

# 관리자 로그인 API
@app.route('/api/admin_login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM admins WHERE username = ? AND password = ?',
                         (username, password)).fetchone()
    conn.close()
    if admin:
        session['admin_logged_in'] = True
        return jsonify({'status': 'success', 'message': 'Admin login successful'})
    else:
        return jsonify({'status': 'error', 'message': '아이디 또는 비밀번호가 일치하지 않습니다.'})

# 로그인한 사원의 로그 조회 API
@app.route('/api/my_logs')
def get_my_logs():
    if 'employeeName' in session:
        name = session['employeeName']
        conn = get_db_connection()
        my_logs_rows = conn.execute('SELECT * FROM logs WHERE employeeName = ? ORDER BY id DESC', (name,)).fetchall()
        conn.close()
        my_logs = [dict(row) for row in my_logs_rows]
        return jsonify(my_logs)
    else:
        return jsonify({'error': 'Not logged in'}), 401

# 오늘의 팀원 조회 API (employeeId 사용)
@app.route('/api/my_team')
def get_my_team():
    if 'employeeId' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    today_str = date.today().strftime('%Y-%m-%d')
    current_user_id = session['employeeId']
    conn = get_db_connection()
    # ID로 팀 이름 찾기
    my_team_info = conn.execute('SELECT teamName FROM schedules WHERE scheduleDate = ? AND employeeId = ?',
                           (today_str, current_user_id)).fetchone()
    if my_team_info:
        team_name = my_team_info['teamName']
        # 팀 이름으로 팀원들의 '이름'을 조회
        teammates_rows = conn.execute('SELECT u.employeeName FROM schedules s JOIN users u ON s.employeeId = u.employeeId WHERE s.scheduleDate = ? AND s.teamName = ?',
                                      (today_str, team_name)).fetchall()
        teammates = [row['employeeName'] for row in teammates_rows]
        conn.close()
        return jsonify({'teamName': team_name, 'teammates': teammates})
    else:
        conn.close()
        return jsonify({'teamName': '배정된 팀 없음', 'teammates': []})

# 나의 전체 스케줄 조회 API (employeeId 사용)
@app.route('/api/my_schedule')
def get_my_schedule():
    if 'employeeId' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    current_user_id = session['employeeId']
    conn = get_db_connection()
    schedule_rows = conn.execute('SELECT scheduleDate, teamName FROM schedules WHERE employeeId = ?',
                                 (current_user_id,)).fetchall()
    conn.close()
    schedules = {row['scheduleDate']: row['teamName'] for row in schedule_rows}
    return jsonify(schedules)

# 공지사항 조회 API
@app.route('/api/notices', methods=['GET'])
def get_notices():
    conn = get_db_connection()
    notices_rows = conn.execute('SELECT * FROM notices ORDER BY id DESC').fetchall()
    conn.close()
    notices = [dict(row) for row in notices_rows]
    return jsonify(notices)

# 공지사항 추가 API
@app.route('/api/add_notice', methods=['POST'])
def add_notice():
    new_notice = request.json
    title = new_notice.get('title')
    content = new_notice.get('content')
    today_str = date.today().strftime('%Y-%m-%d')
    conn = get_db_connection()
    conn.execute('INSERT INTO notices (title, content, createdAt) VALUES (?, ?, ?)',
                 (title, content, today_str))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Notice added successfully'})
    
# QR 스캔 출근 기록 API (employeeId 사용)
@app.route('/api/check_in', methods=['POST'])
def check_in():
    data = request.json
    employee_id = data.get('employeeId')
    safety_check = data.get('safetyCheck')
    
    if not employee_id:
        return jsonify({'status': 'error', 'message': 'Employee ID is missing'}), 400

    conn = get_db_connection()
    # ID로 이름을 찾음
    user = conn.execute('SELECT employeeName FROM users WHERE employeeId = ?', (employee_id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Unknown employee ID'}), 404
        
    employee_name = user['employeeName']
    date = datetime.now().strftime('%Y-%m-%d')
    source = 'system'
    work_hours = 8
    
    conn.execute('INSERT INTO logs (employeeName, workHours, safetyCheck, date, source) VALUES (?, ?, ?, ?, ?)',
                 (employee_name, work_hours, safety_check, date, source))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': f'{employee_name}님의 출근이 기록되었습니다.'})

# 모든 사원 목록 조회 API
@app.route('/api/employees', methods=['GET'])
def get_employees():
    conn = get_db_connection()
    employees_rows = conn.execute('SELECT DISTINCT employeeName FROM users ORDER BY employeeName').fetchall()
    conn.close()
    employees = [row['employeeName'] for row in employees_rows]
    return jsonify(employees)

# 현재 로그인 사용자 정보 API (employeeId 포함)
@app.route('/api/current_user')
def current_user():
    if 'employeeName' in session and 'employeeId' in session:
        return jsonify({
            'employeeName': session['employeeName'],
            'employeeId': session['employeeId']
        })
    else:
        return jsonify({'error': 'Not logged in'}), 401

# --- 페이지 라우팅 ---

# 루트 경로: 관리자 로그인 여부 확인
@app.route('/')
def index():
    if session.get('admin_logged_in'):
        return render_template('admin.html')
    return redirect(url_for('admin_login_page'))

# 관리자 로그인 페이지
@app.route('/admin_login')
def admin_login_page():
    return render_template('admin_login.html')

# 사원 로그인 페이지
@app.route('/login')
def login_page():
    return render_template('login.html')

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# 사원 메인 페이지 (이제 사용 안 함, QR 페이지로 바로 보냄)
@app.route('/employee')
def employee_main_page():
    if 'employeeName' not in session:
        return redirect(url_for('login_page'))
    return redirect(url_for('qr_generator_page'))

# QR 생성 페이지
@app.route('/qr_generator')
def qr_generator_page():
    if 'employeeName' in session:
        return render_template('index.html')
    return redirect(url_for('login_page'))

# 나의 근무 페이지
@app.route('/my_work')
def my_work_page():
    if 'employeeName' in session:
        return render_template('my_work.html')
    return redirect(url_for('login_page'))

# 공지사항 페이지
@app.route('/notices')
def notices_page():
    if 'employeeName' in session:
        return render_template('notices.html')
    return redirect(url_for('login_page'))

# 스캐너 페이지
@app.route('/scanner')
def scanner_page():
    return render_template('scanner.html')

@app.route('/api/today_stats')
def get_today_stats():
    # 오늘 날짜를 'YYYY-MM-DD' 형식의 문자열로 만듭니다.
    today_str = date.today().strftime('%Y-%m-%d')
    conn = get_db_connection()
    
    # 1. 오늘 근무 예정인 총인원 수 (schedules 테이블 기준)
    total_scheduled = conn.execute('SELECT COUNT(DISTINCT employeeId) FROM schedules WHERE scheduleDate = ?',
                                   (today_str,)).fetchone()[0]
                                   
    # 2. 오늘 출근 기록 중 안전장비 '양호' 인원 수 (logs 테이블 기준)
    safety_ok = conn.execute("SELECT COUNT(*) FROM logs WHERE date = ? AND safetyCheck = '양호'",
                             (today_str,)).fetchone()[0]
                             
    # 3. 오늘 출근 기록 중 안전장비 '불량' 인원 수 (logs 테이블 기준)
    safety_nok = conn.execute("SELECT COUNT(*) FROM logs WHERE date = ? AND safetyCheck = '불량'",
                              (today_str,)).fetchone()[0]
    
    conn.close()
    
    # 계산된 통계 데이터를 JSON 형태로 반환합니다.
    return jsonify({
        'totalScheduled': total_scheduled,
        'safetyOk': safety_ok,
        'safetyNok': safety_nok
    })

@app.route('/api/all_teams_today')
def get_all_teams_today():
    today_str = date.today().strftime('%Y-%m-%d')
    conn = get_db_connection()
    
    # schedules 테이블에서 오늘 날짜의 모든 팀 배정 정보를 가져옵니다.
    schedules_rows = conn.execute('SELECT teamName, employeeId FROM schedules WHERE scheduleDate = ? ORDER BY teamName',
                                  (today_str,)).fetchall()
    conn.close()
    
    # 팀별로 팀원을 정리하기 위한 딕셔너리를 생성합니다.
    teams = {}
    for row in schedules_rows:
        team_name = row['teamName']
        employee_id = row['employeeId']
        
        # 딕셔너리에 팀 이름이 없으면 새로 추가하고, 있으면 기존 목록에 추가합니다.
        if team_name not in teams:
            teams[team_name] = []
        
        # employeeId를 employeeName으로 변환해서 추가합니다. (이 부분은 개선 가능)
        # 우선은 ID를 이름으로 가정하고 추가합니다.
        # 실제로는 users 테이블과 JOIN하여 이름을 가져와야 합니다.
        # 지금은 프로토타입이므로 employeeId를 그대로 사용하겠습니다.
        # -> 수정보완: users 테이블과 JOIN하여 실제 이름을 가져오도록 수정
        conn_inner = get_db_connection()
        user = conn_inner.execute('SELECT employeeName FROM users WHERE employeeId = ?', (employee_id,)).fetchone()
        conn_inner.close()
        if user:
             teams[team_name].append(user['employeeName'])

    return jsonify(teams)

# --- 서버 실행 ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

