# 🚀 Render 배포 가이드

## 📋 사전 준비

### 1. GitHub 계정 준비
- GitHub 계정이 필요합니다: https://github.com
- Git이 설치되어 있어야 합니다

### 2. Render 계정 생성
- Render 사이트: https://render.com
- "Get Started for Free" 클릭
- GitHub 계정으로 로그인

---

## 📂 1단계: GitHub에 코드 업로드

### 1-1. Git 저장소 초기화
프로젝트 폴더에서 다음 명령어 실행:

```bash
# Git 저장소 초기화
git init

# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: PDFtoQuiz Flask app"
```

### 1-2. GitHub 저장소 생성
1. GitHub 웹사이트 접속 (https://github.com)
2. 오른쪽 상단 "+" 클릭 → "New repository"
3. Repository name: `PDFtoQuiz`
4. Public 또는 Private 선택 (무료는 둘 다 가능)
5. "Create repository" 클릭

### 1-3. GitHub에 푸시
생성된 저장소 페이지의 명령어 복사 후 실행:

```bash
# GitHub 저장소 연결
git remote add origin https://github.com/your-username/PDFtoQuiz.git

# 기본 브랜치를 main으로 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

> **참고**: `your-username`을 본인의 GitHub 사용자명으로 변경하세요.

---

## 🌐 2단계: Render에 배포

### 2-1. Render에서 새 Web Service 생성

1. **Render 대시보드 접속**
   - https://dashboard.render.com

2. **New Web Service 생성**
   - 상단 "New +" 버튼 클릭
   - "Web Service" 선택

3. **GitHub 저장소 연결**
   - "Connect a repository" 클릭
   - GitHub 계정 연결 (처음이라면 권한 승인)
   - `PDFtoQuiz` 저장소 선택
   - "Connect" 클릭

### 2-2. 서비스 설정

다음과 같이 입력:

| 항목 | 값 |
|------|-----|
| **Name** | `pdftoquiz` (원하는 이름) |
| **Region** | `Singapore` (한국과 가까움) |
| **Branch** | `main` |
| **Root Directory** | (비워둠) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | `Free` |

### 2-3. 환경 변수 설정

"Advanced" 또는 "Environment" 섹션에서:

1. **"Add Environment Variable" 클릭**

2. **Google API 키 추가**:
   - Key: `GOOGLE_API_KEY`
   - Value: `여기에_본인의_Google_API_키_입력`

3. **Flask 환경 추가** (선택사항):
   - Key: `FLASK_ENV`
   - Value: `production`

4. **Python 버전 추가** (선택사항):
   - Key: `PYTHON_VERSION`
   - Value: `3.12.0`

### 2-4. 배포 시작

1. **"Create Web Service" 버튼 클릭**
2. 배포가 자동으로 시작됩니다 (약 3-5분 소요)
3. 로그를 확인하며 진행 상황을 볼 수 있습니다

---

## ✅ 3단계: 배포 확인

### 3-1. URL 확인
배포가 완료되면 상단에 URL이 표시됩니다:
- 예: `https://pdftoquiz.onrender.com`

### 3-2. 웹사이트 접속
1. URL 클릭하여 사이트 접속
2. 로그인 페이지 확인
3. 테스트 계정으로 로그인: `홍길동` / `1111`
4. 문제풀기 기능 테스트
5. 관리자 페이지에서 문제 생성 테스트

---

## 🔄 4단계: 업데이트 방법

코드를 수정한 후 자동 배포:

```bash
# 변경사항 커밋
git add .
git commit -m "수정 내용 설명"

# GitHub에 푸시
git push origin main
```

푸시하면 Render가 **자동으로 새 버전을 배포**합니다! 🎉

---

## ⚠️ 주의사항

### 무료 플랜 제한사항

1. **Sleep 모드**
   - 15분간 요청이 없으면 자동으로 sleep
   - 다시 접속 시 30-50초 소요 (첫 로딩)
   - 해결: 유료 플랜 사용 또는 주기적 ping

2. **데이터 영속성**
   - Render는 배포 시마다 새 컨테이너 생성
   - SQLite 데이터베이스는 배포 시 초기화됨
   - 해결: PostgreSQL 사용 (무료 추가 가능)

3. **월 사용량**
   - 무료: 750시간/월
   - 1개 서비스만 사용 시 충분함

### 데이터베이스 영구 저장 방법

현재는 배포 시 데이터가 초기화됩니다. 영구 저장이 필요하면:

**옵션 1: Render PostgreSQL (무료)**
1. Render 대시보드에서 "New PostgreSQL" 추가
2. app.py를 PostgreSQL로 변경
3. 환경변수로 DATABASE_URL 설정

**옵션 2: Render Disk (유료 $1/월)**
1. Web Service 설정에서 "Disks" 추가
2. Mount path 설정

---

## 🎯 배포 후 체크리스트

- [ ] 웹사이트 접속 확인
- [ ] 로그인 기능 테스트
- [ ] 문제풀기 기능 테스트
- [ ] 관리자 페이지 접속 확인
- [ ] Google AI API 키 정상 작동 확인
- [ ] 문제 생성 기능 테스트 (10개 생성)
- [ ] 결과 저장 및 조회 테스트

---

## 🆘 문제 해결

### 배포 실패 시

1. **Render 로그 확인**
   - 대시보드에서 "Logs" 탭 확인
   - 오류 메시지 확인

2. **일반적인 오류**
   - `ModuleNotFoundError`: requirements.txt 확인
   - `Port binding error`: Start Command 확인
   - `Application failed to start`: app.py 문법 오류 확인

3. **환경변수 문제**
   - GOOGLE_API_KEY가 올바르게 설정되었는지 확인
   - 따옴표 없이 키만 입력했는지 확인

### Sleep 모드 해결

**무료 Uptime 서비스 사용:**
- UptimeRobot (https://uptimerobot.com)
- 5분마다 사이트 ping
- 무료로 50개 모니터 가능

---

## 📞 지원

- Render 문서: https://render.com/docs
- Render 커뮤니티: https://community.render.com

---

## 🎉 완료!

이제 전 세계 어디서나 접속 가능한 웹 퀀즈 서비스가 완성되었습니다!

배포 URL을 친구들과 공유하세요: `https://your-app.onrender.com`
