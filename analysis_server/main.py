from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import tensorflow as tf
import mediapipe as mp
import cv2
import os
import tempfile
import shutil
from typing import List, Dict, Any
import uvicorn

app = FastAPI(title="Squat Analysis API", version="1.0.0")

# 파일 경로 설정 (동일 폴더 기준)
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "best_model.h5")
mean_path = os.path.join(base_dir, "mean.npy")
std_path = os.path.join(base_dir, "std.npy")

# MediaPipe 초기화
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)

class SquatAnalyzer:
    def __init__(self):
        # 정규화 파라미터 로드
        self.mean = np.load(mean_path)
        self.std = np.load(std_path)
        self._load_model()
    
    def _load_model(self):
        base_model = tf.keras.models.load_model(model_path)
        converter = tf.lite.TFLiteConverter.from_keras_model(base_model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        # TFLite 변환 옵션 추가 (LSTM 등 변환 오류 방지)
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS
        ]
        converter._experimental_lower_tensor_list_ops = False
        self.tflite_model = converter.convert()
        self.interpreter = tf.lite.Interpreter(model_content=self.tflite_model)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def _is_squat_video(self, video_path):
        """스쿼트 영상인지 판별하는 함수"""
        cap = cv2.VideoCapture(video_path)
        squat_frames = 0
        total_frames = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            total_frames += 1
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # 스쿼트 관련 관절점들 추출
                left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
                right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
                left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
                right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
                left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
                right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                
                # 스쿼트 자세 판별 조건들
                # 1. 무릎이 엉덩이보다 아래에 있는지 (앉은 자세)
                knee_below_hip = (left_knee.y > left_hip.y) or (right_knee.y > right_hip.y)
                
                # 2. 발목이 무릎보다 아래에 있는지 (서있는 자세)
                ankle_below_knee = (left_ankle.y > left_knee.y) and (right_ankle.y > right_knee.y)
                
                # 3. 어깨-엉덩이-무릎이 일정한 각도를 이루는지
                hip_knee_angle_left = self._calculate_angle(
                    [left_shoulder.x, left_shoulder.y],
                    [left_hip.x, left_hip.y],
                    [left_knee.x, left_knee.y]
                )
                hip_knee_angle_right = self._calculate_angle(
                    [right_shoulder.x, right_shoulder.y],
                    [right_hip.x, right_hip.y],
                    [right_knee.x, right_knee.y]
                )
                
                # 4. 상체가 적절히 숙여져 있는지 (스쿼트 특징)
                torso_angle = abs(left_shoulder.y - left_hip.y) / abs(left_shoulder.x - left_hip.x) if abs(left_shoulder.x - left_hip.x) > 0.01 else 0
                
                # 스쿼트 조건 확인
                is_squat_pose = (
                    knee_below_hip and 
                    ankle_below_knee and
                    (30 < hip_knee_angle_left < 150 or 30 < hip_knee_angle_right < 150) and
                    torso_angle > 0.5  # 상체가 적절히 기울어져 있음
                )
                
                if is_squat_pose:
                    squat_frames += 1
        
        cap.release()
        
        # 전체 프레임의 20% 이상이 스쿼트 자세면 스쿼트 영상으로 판별
        if total_frames == 0:
            return False
        
        squat_ratio = squat_frames / total_frames
        return squat_ratio >= 0.2

    def _calculate_angle(self, a, b, c):
        """세 점 사이의 각도 계산"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle

    def _preprocess_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        sequence = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                frame_data = []
                for lm in landmarks:
                    frame_data.extend([lm.x, lm.y, lm.z, lm.visibility])
                sequence.append(frame_data)
        cap.release()
        if len(sequence) == 0:
            raise ValueError("No pose landmarks detected in video.")
        sequence = np.array(sequence)
        sequence = self._pad_or_trim_sequence(sequence, target_length=191)  # 프레임 수 191로 맞춤
        return (sequence - self.mean) / self.std

    def _pad_or_trim_sequence(self, sequence, target_length=191):
        if len(sequence) < target_length:
            padding = np.zeros((target_length - len(sequence), sequence.shape[1]))
            return np.vstack((sequence, padding))
        return sequence[:target_length]

    def _generate_feedback(self, joints_sequence):
        feedback = []
        # 힙슈팅 감지
        left_hip_y = joints_sequence[:, mp_pose.PoseLandmark.LEFT_HIP.value * 4 + 1]
        left_shoulder_y = joints_sequence[:, mp_pose.PoseLandmark.LEFT_SHOULDER.value * 4 + 1]
        if np.mean(left_hip_y[95:]) < np.mean(left_shoulder_y[95:]):
            feedback.append("힙이 어깨보다 먼저 올라와 힙슈팅이 발생할 수 있습니다.")
        # 무릎 전진 감지
        left_knee_x = joints_sequence[:, mp_pose.PoseLandmark.LEFT_KNEE.value * 4]
        left_foot_x = joints_sequence[:, mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value * 4]
        if np.mean(left_knee_x - left_foot_x) > 0.1:
            feedback.append("무릎이 발끝보다 너무 많이 나갔습니다.")
        # 허리 굽힘 감지
        mean_shoulder = np.mean(joints_sequence[:, mp_pose.PoseLandmark.LEFT_SHOULDER.value * 4 : mp_pose.PoseLandmark.LEFT_SHOULDER.value * 4 + 2], axis=0)
        mean_hip = np.mean(joints_sequence[:, mp_pose.PoseLandmark.LEFT_HIP.value * 4 : mp_pose.PoseLandmark.LEFT_HIP.value * 4 + 2], axis=0)
        trunk_angle = self._angle_between(mean_hip, mean_shoulder)
        if trunk_angle < 45:
            feedback.append("상체가 너무 앞으로 숙여졌습니다. 허리를 곧게 유지해주세요.")
        if not feedback:
            feedback.append("자세가 전반적으로 양호합니다.")
        return feedback

    def _angle_between(self, p1, p2):
        vector = p2 - p1
        angle = np.arctan2(vector[1], vector[0])
        return np.degrees(angle)

    def analyze(self, video_path):
        # 먼저 스쿼트 영상인지 확인
        if not self._is_squat_video(video_path):
            return 0.0, ["스쿼트 영상만 업로드 해주세요"]
        
        try:
            sequence = self._preprocess_video(video_path)
        except ValueError as e:
            return 0.0, [str(e)]
        # TFLite 추론
        self.interpreter.set_tensor(
            self.input_details[0]['index'],
            sequence[np.newaxis, ...].astype(np.float32)
        )
        self.interpreter.invoke()
        raw_score = self.interpreter.get_tensor(self.output_details[0]['index'])[0][1]
        squat_score = self._calculate_score(raw_score)
        feedback = self._generate_feedback(sequence)
        return squat_score, feedback

    def _calculate_score(self, raw_score):
        if raw_score < 0.3:
            score = raw_score * 90
        else:
            score = 60 + (raw_score - 0.5) * 90
        return min(score + 20, 100)

# 전역 분석기 인스턴스 생성
analyzer = None

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 로드"""
    global analyzer
    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(mean_path):
            raise FileNotFoundError(f"Mean file not found: {mean_path}")
        if not os.path.exists(std_path):
            raise FileNotFoundError(f"Std file not found: {std_path}")
        analyzer = SquatAnalyzer()
        print("✅ 스쿼트 분석 모델이 성공적으로 로드되었습니다.")
    except Exception as e:
        print(f"❌ 모델 로드 실패: {str(e)}")
        raise e

@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "message": "Squat Analysis API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "model_loaded": analyzer is not None
    }

@app.post("/analyze")
async def analyze_squat_video(
    videoUrl: str = None,
    username: str = None,
    videoId: int = None,
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    스쿼트 영상 분석 API
    """
    if analyzer is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    if not file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=400,
            detail="Only video files are allowed"
        )
    if file.size > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 100MB"
        )
    temp_file = None
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()
        score, feedback = analyzer.analyze(temp_file.name)
        return {
            "score": round(float(score), 2),
            "feedback": feedback,
            "status": "success",
            "message": "분석이 완료되었습니다.",
            "metadata": {
                "filename": file.filename,
                "username": username,
                "videoId": videoId,
                "videoUrl": videoUrl
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
    finally:
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        file.file.close()

@app.post("/analyze-batch")
async def analyze_multiple_videos(
    files: List[UploadFile] = File(...)
) -> Dict[str, Any]:
    """
    여러 스쿼트 영상 일괄 분석 API
    """
    if analyzer is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 files allowed per batch"
        )
    results = []
    for file in files:
        if not file.content_type.startswith('video/'):
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": "Only video files are allowed"
            })
            continue
        if file.size > 100 * 1024 * 1024:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": "File size must be less than 100MB"
            })
            continue
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            shutil.copyfileobj(file.file, temp_file)
            temp_file.close()
            score, feedback = analyzer.analyze(temp_file.name)
            results.append({
                "filename": file.filename,
                "score": round(float(score), 2),
                "feedback": feedback,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": f"Analysis failed: {str(e)}"
            })
        finally:
            if temp_file and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            file.file.close()
    return {
        "results": results,
        "total_files": len(files),
        "successful_analyses": len([r for r in results if r["status"] == "success"])
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
