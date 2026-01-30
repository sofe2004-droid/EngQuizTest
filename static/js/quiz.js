/**
 * PDFtoQuiz - 문제풀기 클라이언트 로직
 */

// 전역 변수
let currentQuestion = 0;
const answers = [];
const totalQuestions = questionsData.length;

// DOM 요소
const questionContainer = document.getElementById('question-container');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');

/**
 * 문제 표시 함수
 */
function showQuestion(index) {
  const question = questionsData[index];
  
  // 문제 HTML 생성
  const questionHTML = `
    <h4 class="mb-4">문제 ${index + 1}</h4>
    <div class="question-text mb-4">
      <p class="lead">${question.Question}</p>
    </div>
    
    <div class="options">
      <div class="form-check mb-3">
        <input class="form-check-input" 
               type="radio" 
               name="answer" 
               id="option-a" 
               value="A"
               ${answers[index] === 'A' ? 'checked' : ''}>
        <label class="form-check-label option-label" for="option-a">
          <strong>A.</strong> ${question.Example_A}
        </label>
      </div>
      
      <div class="form-check mb-3">
        <input class="form-check-input" 
               type="radio" 
               name="answer" 
               id="option-b" 
               value="B"
               ${answers[index] === 'B' ? 'checked' : ''}>
        <label class="form-check-label option-label" for="option-b">
          <strong>B.</strong> ${question.Example_B}
        </label>
      </div>
      
      <div class="form-check mb-3">
        <input class="form-check-input" 
               type="radio" 
               name="answer" 
               id="option-c" 
               value="C"
               ${answers[index] === 'C' ? 'checked' : ''}>
        <label class="form-check-label option-label" for="option-c">
          <strong>C.</strong> ${question.Example_C}
        </label>
      </div>
      
      <div class="form-check mb-3">
        <input class="form-check-input" 
               type="radio" 
               name="answer" 
               id="option-d" 
               value="D"
               ${answers[index] === 'D' ? 'checked' : ''}>
        <label class="form-check-label option-label" for="option-d">
          <strong>D.</strong> ${question.Example_D}
        </label>
      </div>
    </div>
  `;
  
  questionContainer.innerHTML = questionHTML;
  
  // 진행 상황 업데이트
  updateProgress();
  
  // 버튼 상태 업데이트
  updateButtons();
}

/**
 * 진행 상황 업데이트
 */
function updateProgress() {
  const progress = ((currentQuestion + 1) / totalQuestions) * 100;
  progressBar.style.width = `${progress}%`;
  progressBar.setAttribute('aria-valuenow', progress);
  progressText.textContent = `문제 ${currentQuestion + 1}/${totalQuestions}`;
}

/**
 * 버튼 상태 업데이트
 */
function updateButtons() {
  // 이전 버튼
  prevBtn.disabled = currentQuestion === 0;
  
  // 다음 버튼 텍스트 변경
  if (currentQuestion === totalQuestions - 1) {
    nextBtn.textContent = '결과보기';
    nextBtn.classList.remove('btn-primary');
    nextBtn.classList.add('btn-success');
  } else {
    nextBtn.textContent = '다음 문제';
    nextBtn.classList.remove('btn-success');
    nextBtn.classList.add('btn-primary');
  }
}

/**
 * 답안 저장
 */
function saveAnswer() {
  const selectedAnswer = document.querySelector('input[name="answer"]:checked');
  
  if (!selectedAnswer) {
    return false;
  }
  
  answers[currentQuestion] = selectedAnswer.value;
  return true;
}

/**
 * 다음 문제로 이동
 */
function nextQuestion() {
  // 답안 확인
  if (!saveAnswer()) {
    alert('답을 선택해주세요.');
    return;
  }
  
  // 마지막 문제인 경우 제출
  if (currentQuestion === totalQuestions - 1) {
    submitQuiz();
    return;
  }
  
  // 다음 문제로 이동
  currentQuestion++;
  showQuestion(currentQuestion);
}

/**
 * 이전 문제로 이동
 */
function prevQuestion() {
  if (currentQuestion > 0) {
    // 현재 답안 저장 (선택하지 않았어도 괜찮음)
    saveAnswer();
    
    currentQuestion--;
    showQuestion(currentQuestion);
  }
}

/**
 * 퀴즈 제출
 */
async function submitQuiz() {
  // 모든 문제에 답했는지 확인
  if (answers.length !== totalQuestions) {
    alert('모든 문제에 답을 선택해주세요.');
    return;
  }
  
  // 확인 메시지
  if (!confirm('제출하시겠습니까?')) {
    return;
  }
  
  // 로딩 표시
  nextBtn.disabled = true;
  nextBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>제출 중...';
  
  try {
    // 서버로 답안 전송
    const response = await fetch('/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        answers: answers
      })
    });
    
    const result = await response.json();
    
    if (response.ok && result.success) {
      // 결과 페이지로 이동
      window.location.href = '/result';
    } else {
      alert('오류가 발생했습니다: ' + (result.error || '알 수 없는 오류'));
      nextBtn.disabled = false;
      nextBtn.textContent = '결과보기';
    }
  } catch (error) {
    alert('서버와의 통신 중 오류가 발생했습니다.');
    console.error('Submit error:', error);
    nextBtn.disabled = false;
    nextBtn.textContent = '결과보기';
  }
}

/**
 * 이벤트 리스너 등록
 */
nextBtn.addEventListener('click', nextQuestion);
prevBtn.addEventListener('click', prevQuestion);

// 엔터키로 다음 문제
document.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    nextQuestion();
  }
});

/**
 * 초기화
 */
document.addEventListener('DOMContentLoaded', () => {
  // 첫 번째 문제 표시
  showQuestion(0);
});
