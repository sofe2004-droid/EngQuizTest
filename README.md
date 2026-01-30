# 📚 PDFtoQuiz - 영어 문법 퀴즈 학습 시스템

Flask 기반의 웹 퀴즈 학습 관리 시스템입니다. Google AI (Gemini)를 활용하여 영어 문법 문제를 자동으로 생성할 수 있습니다.

## ✨ 주요 기능

- 🔐 **로그인/회원가입**: SQLite 기반 사용자 인증
- 📝 **문제풀기**: CSV 파일에서 랜덤으로 5문제 출제
- 📊 **결과보기**: 채점 결과 표시 및 JSON 파일에 저장
- 🤖 **AI 문제 생성**: Google Gemini API로 자동 문제 생성 (10개)
- 📈 **학습 기록**: 과거 시도 기록 저장 및 조회

## 🛠️ 기술 스택

### Backend
- Python 3.12
- Flask 3.0.0
- pandas 2.1.4
- SQLite3

### AI
- Google Generative AI (Gemini 2.5 Flash)

### Frontend
- HTML5 / CSS3 / JavaScript (ES6+)
- Bootstrap 5

### 데이터 저장
- SQLite: 회원 정보
- CSV: 문제 데이터
- JSON: 학생별 결과 데이터

## 📋 사전 요구사항

- Python 3.8 이상
- Google AI API 키 ([발급 링크](https://aistudio.google.com/apikey))

## 🚀 로컬 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/PDFtoQuiz.git
cd PDFtoQuiz
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 Google API 키를 입력:

```env
GOOGLE_API_KEY=your-google-api-key-here
```

### 4. 애플리케이션 실행

```bash
python app.py
```

브라우저에서 접속: http://localhost:5000

### 5. 로그인

기본 테스트 계정:
- **아이디**: 홍길동
- **비밀번호**: 1111

## 🌐 웹 배포 (Render)

자세한 배포 가이드는 [DEPLOY.md](DEPLOY.md)를 참고하세요.

### 빠른 배포 단계

1. GitHub에 코드 업로드
2. Render 계정 생성 (https://render.com)
3. GitHub 저장소 연결
4. 환경 변수 설정 (GOOGLE_API_KEY)
5. 배포 완료!

배포 URL: `https://your-app.onrender.com`

## 📁 프로젝트 구조

```
PDFtoQuiz/
├── app.py                  # Flask 메인 애플리케이션
├── requirements.txt        # Python 패키지 목록
├── render.yaml            # Render 배포 설정
├── .gitignore             # Git 제외 파일
├── .env                   # 환경 변수 (Google API 키)
├── database.db            # SQLite 회원 DB
├── quiz/
│   └── quiz.csv          # 문제 데이터
├── results/              # 학생별 결과 JSON 저장
├── templates/            # HTML 템플릿
│   ├── login.html
│   ├── signup.html
│   ├── quiz.html
│   ├── result.html
│   └── admin.html        # 관리자 페이지
├── static/               # 정적 파일
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── quiz.js
├── README.md             # 프로젝트 설명
└── DEPLOY.md             # 배포 가이드
```

## 🎯 주요 기능 설명

### 1. 문제풀기
- CSV 파일에서 랜덤으로 5문제 선택 (중복 없음)
- 1문제씩 순차적으로 표시
- 4지선다형 객관식

### 2. 결과 확인
- 채점 결과 및 정답률 표시
- 문제별 상세 해설 제공
- 과거 시도 기록 조회

### 3. AI 문제 생성 (관리자)
- Google Gemini 2.5 Flash 모델 사용
- 고등학교 학생 대상, 쉬운 난이도
- 10개 문제 자동 생성 및 CSV 추가
- 영문법 전체 범위 (시제, 관계대명사, 비교급 등)

## 🔑 환경 변수

| 변수명 | 설명 | 필수 여부 |
|--------|------|-----------|
| `GOOGLE_API_KEY` | Google AI API 키 | 필수 |
| `FLASK_ENV` | Flask 환경 (production/development) | 선택 |
| `PORT` | 서버 포트 (기본값: 5000) | 선택 |

## 🔒 보안

- 테스트용 애플리케이션으로 비밀번호를 평문으로 저장
- **실제 서비스에서는 bcrypt 또는 werkzeug.security 사용 권장**
- 세션 기반 인증 (쿠키 사용)
- HTTPONLY, SameSite 쿠키 설정 적용

## 📊 데이터 구조

### SQLite (users 테이블)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
```

### CSV (quiz.csv)
- Question: 문제 내용
- Example_A/B/C/D: 보기
- Answer: 정답 (a, b, c, d)
- Explanation: 해설

### JSON (results/{username}.json)
```json
{
  "username": "홍길동",
  "attempts": [
    {
      "date": "2026-01-29",
      "time": "14:30:25",
      "score": 4,
      "total": 5,
      "details": [...]
    }
  ]
}
```

## 🐛 문제 해결

### 1. 모듈을 찾을 수 없음
```bash
pip install -r requirements.txt
```

### 2. Google API 키 오류
- `.env` 파일에 올바른 API 키 입력 확인
- Google AI Studio에서 API 키 발급 확인

### 3. 데이터베이스 오류
```bash
# database.db 삭제 후 재시작 (초기화)
rm database.db
python app.py
```

## 📝 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

## 👥 기여

이슈 및 Pull Request를 환영합니다!

## 📞 문의

문제가 있거나 질문이 있으시면 이슈를 등록해주세요.

---

**Made with ❤️ for English Grammar Learning**
