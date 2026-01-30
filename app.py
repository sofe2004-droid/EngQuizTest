# -*- coding: utf-8 -*-
"""
PDFtoQuiz - Flask 기반 퀴즈 학습 관리 시스템
테스트용 애플리케이션이므로 비밀번호를 평문으로 저장합니다.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import pandas as pd
import random
import json
import os
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = 'pdftoquiz-secret-key-2026'  # 실제 운영 시 환경변수 사용

# 설정
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# 상수
NUM_QUESTIONS = 5
DATABASE_PATH = 'database.db'
CSV_FILE_PATH = 'quiz/quiz.csv'
RESULTS_DIR = 'results'


def init_database():
    """데이터베이스 초기화 및 테이블 생성"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # users 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # 테스트 계정이 없으면 추가
    cursor.execute("SELECT * FROM users WHERE username=?", ('홍길동',))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('홍길동', '1111'))
    
    conn.commit()
    conn.close()


def initialize_app():
    """애플리케이션 초기화"""
    # CSV 파일 검증
    if not os.path.exists(CSV_FILE_PATH):
        raise FileNotFoundError("quiz.csv 파일이 없습니다.")
    
    # 필수 컬럼 검증
    try:
        df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_FILE_PATH, encoding='cp949')
    
    required_columns = ['Question', 'Example_A', 'Example_B', 
                       'Example_C', 'Example_D', 'Answer', 'Explanation']
    
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"필수 컬럼이 없습니다: {col}")
    
    # 데이터베이스 초기화
    if not os.path.exists(DATABASE_PATH):
        init_database()
    else:
        # 데이터베이스가 있어도 테이블 확인
        init_database()
    
    # results 디렉토리 생성
    os.makedirs(RESULTS_DIR, exist_ok=True)


def authenticate_user(username, password):
    """사용자 인증 함수"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", 
                      (username, password))
        user = cursor.fetchone()
        conn.close()
        return user is not None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def get_random_questions(num_questions=NUM_QUESTIONS):
    """CSV에서 랜덤 문제 선택"""
    try:
        df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_FILE_PATH, encoding='cp949')
    
    # 문제 수가 부족한 경우 처리
    if len(df) < num_questions:
        raise ValueError(f"문제가 부족합니다. 필요: {num_questions}, 현재: {len(df)}")
    
    # 랜덤으로 인덱스 선택 (중복 없음)
    selected_indices = random.sample(range(len(df)), num_questions)
    
    # 선택된 문제들을 딕셔너리 리스트로 변환
    questions = df.iloc[selected_indices].to_dict('records')
    
    return questions, selected_indices


def grade_quiz(answers, question_ids):
    """답안 채점"""
    try:
        df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_FILE_PATH, encoding='cp949')
    
    results = []
    score = 0
    
    for idx, (answer, qid) in enumerate(zip(answers, question_ids)):
        correct_answer = df.iloc[qid]['Answer']
        
        # Answer 컬럼의 첫 글자만 추출하여 대문자로 변환 (예: "a. more better" -> "A")
        if isinstance(correct_answer, str) and len(correct_answer) > 0:
            correct_answer_letter = correct_answer[0].upper()
        else:
            correct_answer_letter = correct_answer
        
        # 학생 답안과 비교
        is_correct = (answer.upper() == correct_answer_letter)
        
        if is_correct:
            score += 1
        
        results.append({
            'question_num': idx + 1,
            'question_id': qid,
            'correct': is_correct
        })
    
    return score, results


def save_result(username, score, total, details):
    """결과를 JSON 파일에 저장"""
    filepath = os.path.join(RESULTS_DIR, f'{username}.json')
    
    # results 디렉토리가 없으면 생성
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # 새로운 시도 데이터
    new_attempt = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'score': score,
        'total': total,
        'details': details
    }
    
    # 기존 파일 읽기
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            # 손상된 파일인 경우 새로 시작
            data = {
                'username': username,
                'attempts': []
            }
    else:
        data = {
            'username': username,
            'attempts': []
        }
    
    # 새로운 시도 추가
    data['attempts'].append(new_attempt)
    
    # 파일에 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_results(username):
    """사용자의 전체 결과 불러오기"""
    filepath = os.path.join(RESULTS_DIR, f'{username}.json')
    
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('attempts', [])
        except json.JSONDecodeError:
            return []
    return []


def generate_quiz_with_google(num_questions=10):
    """
    Google AI API(Gemini)를 사용하여 영어 문법 문제 생성
    
    Args:
        num_questions (int): 생성할 문제 수 (기본값: 10)
    
    Returns:
        list: 생성된 문제 리스트
    
    Raises:
        ValueError: API 키가 없거나 응답 파싱 실패 시
        Exception: API 호출 실패 시
    """
    # API 키 확인
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'your-google-api-key-here':
        raise ValueError("Google AI API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
    
    try:
        # Google AI API 설정
        genai.configure(api_key=api_key)
        
        # Gemini 모델 초기화
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 프롬프트 구성
        prompt = f"""당신은 고등학교 학생들을 위한 영어 문법 전문 교사입니다.
학생들이 쉽게 이해할 수 있는 영어 문법 문제를 출제해주세요.

다음 조건에 맞는 영어 문법 문제를 {num_questions}개 만들어주세요:

- 대상: 고등학교 학생
- 난이도: 쉬움
- 출제 범위: 영문법 전체 (시제, 관계대명사, 비교급, 수동태, 조동사 등)
- 형식: 4지선다형 객관식

각 문제는 반드시 다음 형식의 JSON으로 작성해주세요:
{{
  "Question": "문제 내용",
  "Example_A": "보기 A",
  "Example_B": "보기 B",
  "Example_C": "보기 C",
  "Example_D": "보기 D",
  "Answer": "정답 (a, b, c, d 중 하나. 예: 'a', 'b', 'c', 'd')",
  "Explanation": "해설"
}}

반드시 다음 형식으로만 응답해주세요:
```json
[
  {{ "Question": "...", "Example_A": "...", "Example_B": "...", "Example_C": "...", "Example_D": "...", "Answer": "a", "Explanation": "..." }},
  ...
]
```

{num_questions}개의 문제를 JSON 배열 형태로만 반환해주세요. 다른 설명이나 마크다운 형식은 필요 없습니다."""
        
        # API 호출
        response = model.generate_content(prompt)
        
        # 응답 텍스트 추출
        content = response.text.strip()
        
        # JSON 코드 블록 제거 (```json ... ``` 형식)
        if content.startswith('```json'):
            content = content[7:]  # '```json' 제거
        elif content.startswith('```'):
            content = content[3:]  # '```' 제거
        
        if content.endswith('```'):
            content = content[:-3]  # '```' 제거
        
        content = content.strip()
        
        # JSON 파싱
        try:
            data = json.loads(content)
            
            # 배열 형태가 아니면 'questions' 또는 'quiz' 키 찾기
            if isinstance(data, dict):
                quiz_data = data.get('questions') or data.get('quiz') or data.get('problems') or list(data.values())[0]
            else:
                quiz_data = data
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Google AI 응답을 JSON으로 파싱할 수 없습니다: {e}\n응답 내용: {content[:500]}")
        
        # 데이터 검증
        required_fields = ['Question', 'Example_A', 'Example_B', 'Example_C', 'Example_D', 'Answer', 'Explanation']
        
        validated_data = []
        for idx, item in enumerate(quiz_data):
            # 필수 필드 확인
            for field in required_fields:
                if field not in item:
                    raise ValueError(f"{idx+1}번째 문제에 '{field}' 필드가 없습니다.")
            
            # Answer 필드 정규화 (소문자로 변환)
            answer = str(item['Answer']).strip().lower()
            if answer not in ['a', 'b', 'c', 'd']:
                # 'a.' 또는 'A)' 같은 형식 처리
                if len(answer) > 0 and answer[0] in ['a', 'b', 'c', 'd']:
                    answer = answer[0]
                else:
                    answer = 'a'  # 기본값
            
            item['Answer'] = answer
            validated_data.append(item)
        
        return validated_data
        
    except Exception as e:
        raise Exception(f"Google AI API 호출 중 오류가 발생했습니다: {str(e)}")


def save_quiz_to_csv(quiz_data):
    """
    생성된 문제를 CSV 파일에 추가
    
    Args:
        quiz_data (list): 문제 데이터 리스트
    
    Returns:
        int: 추가된 문제 수
    
    Raises:
        Exception: CSV 파일 쓰기 실패 시
    """
    try:
        # pandas DataFrame 생성
        new_df = pd.DataFrame(quiz_data)
        
        # 컬럼 순서 맞추기
        columns_order = ['Question', 'Example_A', 'Example_B', 'Example_C', 'Example_D', 'Answer', 'Explanation']
        new_df = new_df[columns_order]
        
        # 기존 CSV 파일이 있으면 읽어서 추가, 없으면 새로 생성
        if os.path.exists(CSV_FILE_PATH):
            # 기존 파일에 추가 (append)
            new_df.to_csv(CSV_FILE_PATH, mode='a', header=False, index=False, encoding='utf-8')
        else:
            # 새로 생성
            new_df.to_csv(CSV_FILE_PATH, mode='w', header=True, index=False, encoding='utf-8')
        
        return len(quiz_data)
        
    except Exception as e:
        raise Exception(f"CSV 파일 저장 중 오류가 발생했습니다: {str(e)}")


# 라우트 정의

@app.route('/')
def index():
    """로그인 페이지"""
    # 이미 로그인된 경우 /quiz로 리다이렉트
    if 'username' in session:
        return redirect(url_for('quiz'))
    
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    """로그인 처리"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    # 입력값 검증
    if not username or not password:
        return render_template('login.html', 
                             error='아이디와 비밀번호를 모두 입력해주세요.')
    
    # 사용자 인증
    if authenticate_user(username, password):
        session['username'] = username
        return redirect(url_for('quiz'))
    else:
        return render_template('login.html', 
                             error='아이디 또는 비밀번호가 일치하지 않습니다.')


@app.route('/signup', methods=['GET'])
def signup():
    """회원가입 페이지"""
    # 이미 로그인된 경우 /quiz로 리다이렉트
    if 'username' in session:
        return redirect(url_for('quiz'))
    
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_process():
    """회원가입 처리"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    password_confirm = request.form.get('password_confirm', '').strip()
    
    # 입력값 검증
    if not username or not password or not password_confirm:
        return render_template('signup.html', 
                             error='모든 항목을 입력해주세요.')
    
    # 이름 길이 검증
    if len(username) < 2:
        return render_template('signup.html', 
                             error='이름은 최소 2자 이상이어야 합니다.',
                             username=username)
    
    # 비밀번호 길이 검증
    if len(password) < 4:
        return render_template('signup.html', 
                             error='비밀번호는 최소 4자 이상이어야 합니다.',
                             username=username)
    
    # 비밀번호 확인 일치 검증
    if password != password_confirm:
        return render_template('signup.html', 
                             error='비밀번호가 일치하지 않습니다.',
                             username=username)
    
    # 중복 확인 및 회원가입
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 중복 체크
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone() is not None:
            conn.close()
            return render_template('signup.html', 
                                 error='이미 존재하는 이름입니다. 다른 이름을 사용해주세요.',
                                 username=username)
        
        # 회원가입
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                      (username, password))
        conn.commit()
        conn.close()
        
        # 가입 완료 후 자동 로그인
        session['username'] = username
        return redirect(url_for('quiz'))
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return render_template('signup.html', 
                             error='회원가입 중 오류가 발생했습니다.',
                             username=username)


@app.route('/quiz')
def quiz():
    """문제풀기 페이지"""
    # 세션 체크
    if 'username' not in session:
        return redirect(url_for('index'))
    
    try:
        # quiz.csv에서 5문제 랜덤 선택
        questions, question_ids = get_random_questions()
        
        # 세션에 문제 ID 리스트 저장
        session['question_ids'] = question_ids
        
        # quiz.html 렌더링
        return render_template('quiz.html', 
                             questions=questions, 
                             username=session['username'])
    
    except ValueError as e:
        return f"오류: {str(e)}", 500
    except Exception as e:
        return f"문제를 불러오는 중 오류가 발생했습니다: {str(e)}", 500


@app.route('/submit', methods=['POST'])
def submit():
    """답안 제출 및 채점"""
    # 세션 체크
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # 답안 수신
        data = request.get_json()
        answers = data.get('answers', [])
        question_ids = session.get('question_ids', [])
        
        # 답안 개수 검증
        if len(answers) != NUM_QUESTIONS:
            return jsonify({'error': '답안 개수가 올바르지 않습니다.'}), 400
        
        # 답안 형식 검증
        valid_answers = ['A', 'B', 'C', 'D']
        for answer in answers:
            if answer not in valid_answers:
                return jsonify({'error': '올바르지 않은 답안 형식입니다.'}), 400
        
        # 채점
        score, details = grade_quiz(answers, question_ids)
        
        # 결과 저장
        username = session['username']
        save_result(username, score, NUM_QUESTIONS, details)
        
        # 세션에 결과 저장
        session['last_score'] = score
        session['last_details'] = details
        session['last_answers'] = answers
        
        return jsonify({'success': True, 'score': score})
    
    except Exception as e:
        return jsonify({'error': f'오류가 발생했습니다: {str(e)}'}), 500


@app.route('/result')
def result():
    """결과보기 페이지"""
    # 세션 체크
    if 'username' not in session:
        return redirect(url_for('index'))
    
    username = session['username']
    
    # 세션에서 최근 결과 가져오기
    last_score = session.get('last_score', 0)
    last_details = session.get('last_details', [])
    last_answers = session.get('last_answers', [])
    question_ids = session.get('question_ids', [])
    
    # CSV에서 문제 데이터 가져오기
    try:
        df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_FILE_PATH, encoding='cp949')
    
    # 문제 상세 정보 구성
    detailed_results = []
    for idx, detail in enumerate(last_details):
        qid = detail['question_id']
        question_data = df.iloc[qid]
        
        # 정답의 첫 글자만 추출 (예: "a. more better" -> "A")
        correct_answer_full = question_data['Answer']
        if isinstance(correct_answer_full, str) and len(correct_answer_full) > 0:
            correct_answer_letter = correct_answer_full[0].upper()
        else:
            correct_answer_letter = correct_answer_full
        
        detailed_results.append({
            'question_num': detail['question_num'],
            'question': question_data['Question'],
            'example_a': question_data['Example_A'],
            'example_b': question_data['Example_B'],
            'example_c': question_data['Example_C'],
            'example_d': question_data['Example_D'],
            'correct_answer': correct_answer_letter,
            'student_answer': last_answers[idx] if idx < len(last_answers) else '',
            'explanation': question_data['Explanation'],
            'is_correct': detail['correct']
        })
    
    # 과거 기록 로드
    all_attempts = load_results(username)
    
    return render_template('result.html',
                         username=username,
                         score=last_score,
                         total=NUM_QUESTIONS,
                         detailed_results=detailed_results,
                         all_attempts=all_attempts[:-1] if len(all_attempts) > 1 else [])


@app.route('/logout')
def logout():
    """로그아웃 처리"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/admin')
def admin():
    """관리자 페이지 - 문제 생성 관리"""
    # 세션 체크
    if 'username' not in session:
        return redirect(url_for('index'))
    
    # 현재 문제 수 가져오기
    try:
        df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')
        total_questions = len(df)
    except:
        total_questions = 0
    
    return render_template('admin.html', 
                         username=session['username'],
                         total_questions=total_questions)


@app.route('/generate-quiz', methods=['POST'])
def generate_quiz_endpoint():
    """Google AI API(Gemini)를 사용하여 문제 생성"""
    # 세션 체크
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # 1. Google AI API로 문제 생성 (10개 고정)
        quiz_data = generate_quiz_with_google(10)
        
        # 2. CSV에 저장
        count = save_quiz_to_csv(quiz_data)
        
        # 3. 성공 응답
        return jsonify({
            'success': True, 
            'count': count,
            'message': f'{count}개의 문제가 추가되었습니다.'
        })
    
    except ValueError as e:
        # API 키 없음, 데이터 검증 실패 등
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        # 기타 모든 오류
        return jsonify({'error': str(e)}), 500


# 애플리케이션 시작
if __name__ == '__main__':
    # 애플리케이션 초기화
    initialize_app()
    
    # Flask 서버 실행
    # 프로덕션 환경에서는 gunicorn이 사용됨
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)

# 프로덕션 환경 초기화 (gunicorn이 직접 app 객체를 실행)
initialize_app()
