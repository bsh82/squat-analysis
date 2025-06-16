# 스쿼트 자세 분석 FastAPI 서버
MediaPipe와 TensorFlow Lite를 활용한 스쿼트 운동 자세 분석 REST API 서버입니다. 실시간 비디오 분석을 통해 스쿼트 자세의 정확성을 평가하고 피드백을 제공합니다.

# 🚀 주요 기능
실시간 스쿼트 자세 분석: TensorFlow Lite 모델을 통한 빠른 추론

스쿼트 영상 자동 감지: MediaPipe를 활용한 스쿼트 동작 판별

상세 피드백 제공: 힙슈팅, 무릎 전진, 허리 굽힘 등 구체적인 자세 교정 가이드

배치 처리: 여러 비디오 파일 동시 분석

RESTful API: 표준화된 HTTP API 인터페이스

# 🛠️ 기술 스택
Backend Framework
FastAPI: 고성능 비동기 웹 프레임워크

Uvicorn: ASGI 서버

AI/ML
TensorFlow Lite: 경량화된 딥러닝 모델 추론

MediaPipe: 실시간 포즈 감지 및 키포인트 추출

OpenCV: 비디오 처리 및 컴퓨터 비전

Data Processing
NumPy: 수치 연산 및 배열 처리

# 📋 사전 요구사항
Python 3.8 이상

훈련된 모델 파일들:

best_model.h5 (Keras 모델)

mean.npy (정규화 평균값)

std.npy (정규화 표준편차)

# 📚 API 문서
기본 엔드포인트
서버 상태 확인
text
GET /
응답:

json
{
  "message": "Squat Analysis API",
  "status": "running",
  "version": "1.0.0"
}
헬스 체크
text
GET /health
응답:

json
{
  "status": "healthy",
  "model_loaded": true
}
분석 API
단일 비디오 분석
text
POST /analyze
Content-Type: multipart/form-data

file: (video file)
videoUrl: "optional_video_url"
username: "optional_username"
videoId: 123
응답:

json
{
  "score": 85.5,
  "feedback": [
    "자세가 전반적으로 양호합니다.",
    "무릎이 발끝보다 너무 많이 나갔습니다."
  ],
  "status": "success",
  "message": "분석이 완료되었습니다.",
  "metadata": {
    "filename": "squat_video.mp4",
    "username": "user123",
    "videoId": 123,
    "videoUrl": "https://example.com/video.mp4"
  }
}
배치 비디오 분석
text
POST /analyze-batch
Content-Type: multipart/form-data

files: (multiple video files, max 5)
응답:

json
{
  "results": [
    {
      "filename": "video1.mp4",
      "score": 85.5,
      "feedback": ["자세가 전반적으로 양호합니다."],
      "status": "success"
    },
    {
      "filename": "video2.mp4",
      "status": "error",
      "message": "Only video files are allowed"
    }
  ],
  "total_files": 2,
  "successful_analyses": 1
}

# 🤖 AI 모델 정보
포즈 감지 (MediaPipe)
모델: MediaPipe Pose
스쿼트 분류 (TensorFlow Lite)
입력 형태: (1, 191, 132)

191: 최대 프레임 수

132: 33개 포즈 랜드마크 × 4차원

출력: 스쿼트 유효성 점수 (0-100)

점수 계산 알고리즘
python
def _calculate_score(self, raw_score):
    if raw_score < 0.3:
        score = raw_score * 90
    else:
        score = 60 + (raw_score - 0.5) * 90
    return min(score + 20, 100)
    
# 📊 분석 기능
스쿼트 영상 자동 감지
무릎 위치: 엉덩이 대비 무릎 높이 확인

발목 위치: 무릎 대비 발목 높이 확인

관절 각도: 어깨-엉덩이-무릎 각도 분석

상체 기울기: 적절한 상체 전경 확인

상세 피드백 시스템
힙슈팅 감지: 엉덩이가 어깨보다 먼저 올라오는 현상

무릎 전진 감지: 무릎이 발끝을 넘어가는 현상

허리 굽힘 감지: 상체가 과도하게 앞으로 숙여지는 현상

# 🔧 설정 및 제한사항
파일 업로드 제한
파일 형식: 비디오 파일만 허용 (video/*)

파일 크기: 최대 100MB

배치 처리: 최대 5개 파일 동시 처리

# 성능 최적화
TensorFlow Lite: 모델 경량화로 빠른 추론

임시 파일 관리: 자동 정리로 메모리 효율성

비동기 처리: FastAPI의 비동기 기능 활용

# 🚨 에러 처리
일반적인 에러들
모델 로드 실패

json
{
  "detail": "Model not loaded"
}
잘못된 파일 형식

json
{
  "detail": "Only video files are allowed"
}
파일 크기 초과

json
{
  "detail": "File size must be less than 100MB"
}
스쿼트 영상 아님

json
{
  "score": 0.0,
  "feedback": ["스쿼트 영상만 업로드 해주세요"]
}
# 🔍 API 문서 확인
서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

# 🧪 테스트
cURL을 이용한 테스트
bash
# 단일 비디오 분석
curl -X POST "http://localhost:8000/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@squat_video.mp4" \
  -F "username=testuser" \
  -F "videoId=1"

# 헬스 체크
curl -X GET "http://localhost:8000/health"
Python을 이용한 테스트
python
import requests

# 비디오 파일 분석
with open('squat_video.mp4', 'rb') as f:
    files = {'file': f}
    data = {
        'username': 'testuser',
        'videoId': 1
    }
    response = requests.post(
        'http://localhost:8000/analyze',
        files=files,
        data=data
    )
    print(response.json())