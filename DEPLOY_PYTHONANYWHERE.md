# 🐍 PythonAnywhere 배포 가이드 (가장 간단!)

> **Git 불필요! 명령어 불필요! 웹 인터페이스만으로 5분 배포!**

---

## 📋 1단계: 계정 생성 (1분)

1. **PythonAnywhere 웹사이트 접속**
   - https://www.pythonanywhere.com

2. **무료 계정 생성**
   - 우측 상단 "Pricing & signup" 클릭
   - "Create a Beginner account" 선택 (완전 무료!)
   - 회원가입 정보 입력:
     - Username (영문, 이게 URL에 사용됨)
     - Email
     - Password
   - "Register" 클릭

3. **이메일 인증**
   - 받은 이메일에서 인증 링크 클릭

---

## 📂 2단계: 파일 업로드 (2분)

### 2-1. 프로젝트 폴더 압축

1. **프로젝트 폴더를 ZIP 파일로 압축**
   - `d:\VibeCoding\PDFtoQuiz` 폴더를 우클릭
   - "압축" → "ZIP 파일로 압축"
   - 파일명: `PDFtoQuiz.zip`

### 2-2. PythonAnywhere에 업로드

1. **대시보드 접속**
   - https://www.pythonanywhere.com/user/your-username/

2. **Files 탭 클릭**
   - 상단 메뉴에서 "Files" 클릭

3. **ZIP 파일 업로드**
   - "Upload a file" 섹션에서 `PDFtoQuiz.zip` 선택
   - "Upload" 버튼 클릭

4. **압축 해제**
   - 업로드된 `PDFtoQuiz.zip` 옆의 링크 클릭
   - 또는 Bash console에서:
   ```bash
   unzip PDFtoQuiz.zip
   cd PDFtoQuiz
   ```

---

## ⚙️ 3단계: 웹 앱 설정 (2분)

### 3-1. Web 탭으로 이동

1. 상단 메뉴에서 **"Web"** 클릭
2. **"Add a new web app"** 버튼 클릭

### 3-2. 설정 마법사

1. **도메인 확인**
   - `your-username.pythonanywhere.com` 확인
   - "Next" 클릭

2. **프레임워크 선택**
   - "Manual configuration" 선택
   - Python 버전: **Python 3.10** 선택
   - "Next" 클릭

3. **완료**
   - "Manual configuration" 완료 메시지 확인

### 3-3. WSGI 설정 파일 수정

1. Web 탭에서 **"WSGI configuration file"** 링크 클릭
   - 예: `/var/www/your-username_pythonanywhere_com_wsgi.py`

2. **파일 내용을 모두 삭제하고 다음으로 교체**:

```python
import sys
import os

# 프로젝트 경로 추가
path = '/home/your-username/PDFtoQuiz'
if path not in sys.path:
    sys.path.insert(0, path)

# Flask 앱 import
from app import app as application

# 환경 변수 설정 (Google API 키)
os.environ['GOOGLE_API_KEY'] = 'your-google-api-key-here'
```

**중요**: 
- `your-username`을 본인의 PythonAnywhere 사용자명으로 변경
- `your-google-api-key-here`를 실제 Google API 키로 변경

3. **"Save"** 버튼 클릭 (우측 상단)

### 3-4. 가상환경 및 패키지 설치

1. **Consoles 탭 클릭**
2. **"Bash" 콘솔 시작**
3. 다음 명령어 입력:

```bash
# 프로젝트 폴더로 이동
cd PDFtoQuiz

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 데이터베이스 초기화 (Python 실행)
python3 -c "from app import initialize_app; initialize_app()"
```

### 3-5. 가상환경 경로 설정

1. **Web 탭으로 돌아가기**
2. **"Virtualenv" 섹션 찾기**
3. 다음 경로 입력:
   ```
   /home/your-username/PDFtoQuiz/venv
   ```
4. **체크 아이콘 클릭** (저장)

### 3-6. 정적 파일 설정

Web 탭의 "Static files" 섹션에서:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/your-username/PDFtoQuiz/static/` |

"Enter URL" 과 "Enter path"에 위 내용 입력 후 체크 아이콘 클릭

---

## 🎉 4단계: 배포 완료!

### 4-1. 웹 앱 재시작

1. Web 탭 상단의 **"Reload your-username.pythonanywhere.com"** 버튼 클릭 (초록색 버튼)
2. 몇 초 대기

### 4-2. 웹사이트 접속

URL 클릭: `https://your-username.pythonanywhere.com`

### 4-3. 테스트

1. 로그인 페이지 확인
2. 테스트 계정으로 로그인: `홍길동` / `1111`
3. 문제풀기 기능 테스트
4. 관리자 페이지에서 문제 생성 테스트

---

## 🔄 파일 수정 방법

### 방법 1: 웹 에디터 사용

1. **Files 탭** 클릭
2. 수정할 파일 클릭 (예: `PDFtoQuiz/app.py`)
3. 웹 에디터에서 수정
4. "Save" 버튼 클릭
5. **Web 탭에서 "Reload" 버튼** 클릭

### 방법 2: 파일 재업로드

1. 로컬에서 파일 수정
2. 수정된 파일을 다시 업로드
3. **Web 탭에서 "Reload" 버튼** 클릭

---

## ⚠️ 무료 플랜 제한사항

### 제한 사항

1. **하루 CPU 시간 제한**
   - 100초/일 (일반 사용에는 충분)

2. **외부 사이트 접속 제한**
   - **중요**: 무료 플랜은 화이트리스트에 있는 사이트만 접속 가능
   - Google AI API (generativelanguage.googleapis.com)는 **허용 목록에 없을 수 있음**
   - 이 경우 유료 플랜 필요 ($5/월)

3. **저장 공간**
   - 512MB (충분함)

4. **웹 앱 개수**
   - 1개만 가능

### 해결 방법

**Google API 호출 문제가 있는 경우:**

**옵션 1**: 유료 플랜 ($5/월)
- 외부 API 호출 제한 해제
- CPU 시간 무제한

**옵션 2**: Render 사용 (무료)
- 외부 API 호출 제한 없음
- GitHub 필요하지만 더 강력함

---

## 🔧 문제 해결

### 1. 웹사이트가 안 열릴 때

**Error log 확인**:
1. Web 탭의 "Log files" 섹션
2. "Error log" 클릭
3. 오류 메시지 확인

**일반적인 오류**:
- `ModuleNotFoundError`: 가상환경에서 패키지 재설치
- `ImportError`: WSGI 파일의 경로 확인
- `Database locked`: Bash console에서 `rm database.db` 후 재초기화

### 2. Google API가 작동하지 않을 때

무료 플랜의 화이트리스트 제한 때문일 수 있습니다.

**확인 방법**:
1. Bash console에서:
```bash
cd PDFtoQuiz
source venv/bin/activate
python3 -c "import google.generativeai as genai; print('OK')"
```

2. 오류가 나면: 유료 플랜 필요 또는 Render 사용

### 3. 정적 파일이 안 보일 때

- Web 탭의 "Static files" 설정 확인
- 경로가 정확한지 확인
- Reload 버튼 클릭

### 4. 세션이 작동하지 않을 때

WSGI 파일에 다음 추가:
```python
# Flask secret key 설정
application.secret_key = 'your-secret-key-here'
```

---

## 📊 PythonAnywhere vs Render 비교

| 항목 | PythonAnywhere | Render |
|------|----------------|--------|
| **난이도** | ⭐ 매우 쉬움 | ⭐⭐⭐ 보통 |
| **Git 필요** | ❌ 불필요 | ✅ 필수 |
| **파일 업로드** | 웹 인터페이스 | GitHub |
| **외부 API** | ⚠️ 화이트리스트만 | ✅ 제한 없음 |
| **무료 플랜** | 제한적 | 더 관대 |
| **자동 재배포** | ❌ 수동 | ✅ Git push로 자동 |
| **추천 대상** | 초보자, 테스트용 | 실제 서비스 |

---

## 💡 추천 사항

### PythonAnywhere를 사용하기 좋은 경우:
- ✅ Git을 모르거나 배우고 싶지 않음
- ✅ 빠르게 테스트하고 싶음
- ✅ Google API 사용 안 함 (또는 $5/월 지불 가능)
- ✅ 간단한 개인 프로젝트

### Render를 사용하기 좋은 경우:
- ✅ Google AI API 반드시 사용해야 함 (무료)
- ✅ Git을 배울 의향 있음
- ✅ 실제 서비스로 운영
- ✅ 자동 재배포 필요

---

## 🎯 완료 체크리스트

- [ ] PythonAnywhere 계정 생성
- [ ] 프로젝트 파일 업로드
- [ ] Web 앱 생성
- [ ] WSGI 파일 수정
- [ ] 가상환경 설정
- [ ] 패키지 설치
- [ ] 정적 파일 설정
- [ ] Google API 키 설정
- [ ] 웹 앱 Reload
- [ ] 사이트 접속 테스트
- [ ] 로그인 테스트
- [ ] 문제풀기 테스트
- [ ] 관리자 기능 테스트 (Google API)

---

## 📞 지원

- PythonAnywhere 도움말: https://help.pythonanywhere.com
- PythonAnywhere 포럼: https://www.pythonanywhere.com/forums/

---

## 🎉 완료!

이제 간단하게 웹에 배포되었습니다!

**배포 URL**: `https://your-username.pythonanywhere.com`

친구들과 공유하세요! 🚀
