# squat-analyze
스쿼트 자세 분석 AI 모델
MediaPipe와 Bidirectional LSTM을 활용한 스쿼트 운동 자세 분석 및 분류 시스템입니다. 딥러닝 모델을 통해 스쿼트 동작의 유효성을 실시간으로 판별합니다.

🚀 주요 기능
실시간 포즈 감지: MediaPipe Holistic을 통한 전신 키포인트 추출

딥러닝 분류: Bidirectional LSTM 모델을 통한 스쿼트 자세 유효성 판별

데이터 증강: 가우시안 노이즈 및 프레임 드롭아웃을 통한 모델 일반화 성능 향상

실시간 분석: 웹캠 또는 비디오 파일을 통한 실시간 자세 분석

🛠️ 기술 스택
AI/ML
MediaPipe: 실시간 포즈 감지 및 키포인트 추출

TensorFlow/Keras: 딥러닝 모델 구축 및 훈련

Bidirectional LSTM: 시계열 데이터 분석을 위한 양방향 순환 신경망

OpenCV: 컴퓨터 비전 및 이미지 처리

Data Processing
NumPy: 수치 연산 및 배열 처리

Scikit-learn: 데이터 분할 및 평가 메트릭

📋 사전 요구사항
Python 3.8 이상

CUDA 지원 GPU (선택사항, 훈련 가속화용)

웹캠 (실시간 분석용)

⚙️ 설치 및 설정
1. 프로젝트 클론
bash
git clone https://github.com/your-username/squat-pose-analyzer.git
cd squat-pose-analyzer
2. 가상환경 생성 및 활성화
bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
3. 의존성 설치
bash
pip install -r requirements.txt
4. 필요한 패키지 목록 (requirements.txt)
text
tensorflow>=2.10.0
mediapipe>=0.9.0
opencv-python>=4.6.0
numpy>=1.21.0
scikit-learn>=1.1.0
matplotlib>=3.5.0

# 비디오 분석
191: 최대 프레임 수

132: 33개 포즈 랜드마크 × 4차원 (x, y, z, visibility)

출력: 2클래스 분류 (Valid/Invalid)

📊 성능 최적화 기법
1. 데이터 증강
python
# 가우시안 노이즈 추가
def add_noise(seq, noise_level=0.01)

# 프레임 드롭아웃
def dropout_frames(seq, drop_prob=0.1)
2. 정규화
Z-score 정규화: 각 특성을 평균 0, 표준편차 1로 조정

배치 정규화: 내부 공변량 이동 문제 해결

3. 콜백 시스템
조기 종료: 과적합 방지

학습률 감소: 세밀한 최적화

모델 체크포인트: 최적 모델 자동 저장

python

# 모델 파일 경로 확인
if os.path.exists('best_model.h5'):
    model = tf.keras.models.load_model('best_model.h5')
