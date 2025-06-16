import cv2
import numpy as np
import os
import tensorflow as tf
import mediapipe as mp

# MediaPipe 모델 초기화
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# MediaPipe로 키포인트 검출하는 함수
def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # BGR을 RGB로 변환
    image.flags.writeable = False                   # 이미지 읽기 전용으로 설정
    results = model.process(image)                  # 예측 수행
    image.flags.writeable = True                    # 이미지 쓰기 가능으로 변경
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # RGB를 BGR로 다시 변환
    return image, results

# 검출된 키포인트를 화면에 그리는 함수
def draw_styled_landmarks(image, results):
    # 얼굴 연결선 그리기
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION,
                             mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1),
                             mp_drawing.DrawingSpec(color=(80,256,121), thickness=1, circle_radius=1)
                             )
    # 포즈 연결선 그리기
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                             landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                             )
    # 왼손 연결선 그리기
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                             mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
                             mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                             )
    # 오른손 연결선 그리기
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                             mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                             mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                             )
    
# 비디오 크기 조정 함수
def scale_video(scale_percent):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dimensions = (width, height)
    return dimensions

# 포즈 키포인트만 추출하는 함수
def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    return pose

from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

# 예측할 동작 클래스
Squat_result = np.array(['Valid', 'Invalid'])

# 총 240개 비디오 (각 클래스당 120개)
no_of_vids = 120

# 데이터 저장 경로
VALID_SAVE_PATH = os.path.join('Squat_Data')

# 라벨을 숫자로 매핑
label_map = {label:num for num, label in enumerate(Squat_result)}

# 시퀀스와 라벨을 저장할 배열 초기화
sequences, labels = [], []
max_frame_num = 0

# 모든 비디오 데이터 로드
for action in Squat_result:
    for sequence in range(no_of_vids):
        counter = True
        window = []
        frame_no = 0
        while counter:
            try:
                # 각 프레임의 키포인트 데이터 로드
                res = np.load(os.path.join(VALID_SAVE_PATH, action, str(sequence), "{}.npy".format(frame_no)))
                print(sequence, action, frame_no)
                frame_no+=1
                if frame_no>max_frame_num:
                    max_frame_num=frame_no
                window.append(res)
            except:
                break

        sequences.append(window)
        labels.append(label_map[action])

# LSTM 모델은 모든 입력이 같은 크기여야 함
# 가장 긴 비디오(191프레임)에 맞춰서 패딩 처리
X = tf.keras.preprocessing.sequence.pad_sequences(sequences)

# 현재 240개 비디오, 각각 191프레임 x 132키포인트 형태
X.shape
y = to_categorical(labels).astype(int)
y.shape

# 나중에 사용하기 위해 특성과 라벨 저장
np.save("Features",X)
np.save("Labels",y)

# 훈련/테스트 데이터 분할 (8:2 비율)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import TensorBoard

# 텐서보드 콜백 설정
log_dir = os.path.join('Logs_Retrain')
tb_callback = TensorBoard(log_dir=log_dir)

# 기본 LSTM 모델 구성
model = Sequential()
model.add(LSTM(64, return_sequences=False, activation='relu', input_shape=(191,132)))
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(Squat_result.shape[0], activation='sigmoid'))

# 모델 컴파일
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

# 모델 훈련 (100 에포크)
model.fit(X_train, y_train, epochs=100, validation_data=(X_test, y_test), callbacks=[tb_callback])

# 훈련된 모델 저장
model.save('model.h5')

from sklearn.metrics import accuracy_score, confusion_matrix

# 테스트 데이터로 예측
yhat = saved_model.predict(X_test)

# 예측 결과를 클래스 인덱스로 변환
ytrue = np.argmax(y_test, axis=1).tolist()
yhat = np.argmax(yhat, axis=1).tolist()

# 혼동 행렬과 정확도 계산
confusion_matrix(ytrue, yhat)
accuracy_score(ytrue, yhat)

# 모델이 받는 시퀀스 길이에 맞춰 패딩할 배열
longest_sequence = np.load("Longest_Sequence.npy")

# 예측용 변수 초기화
sequence_for_prediction = [longest_sequence]
window = []

# 비디오 스트림 캡처
cap = cv2.VideoCapture(r'your video path here')

# MediaPipe 모델 설정
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        # 프레임 읽기
        ret, frame = cap.read()
        # 비디오 끝나면 종료
        if not ret:
            break

        # 키포인트 검출
        image, results = mediapipe_detection(frame, holistic)

        # 랜드마크 그리기
        draw_styled_landmarks(image, results)
        
        # 화면 크기 조정
        dim = scale_video(30)
        image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

        # 화면에 표시
        cv2.imshow('OpenCV Feed', image)

        # 예측을 위한 키포인트 추출
        keypoints = extract_keypoints(results)
        window.append(keypoints)

    cap.release()
    cv2.destroyAllWindows()

    # 예측용 시퀀스 준비
    sequence_for_prediction.append(window)
    padded_sequence = tf.keras.preprocessing.sequence.pad_sequences(sequence_for_prediction, maxlen=191)
    seq_to_predict = padded_sequence[1]

    print (seq_to_predict)

    # 스쿼트 유효성 예측
    res = model.predict(np.expand_dims(seq_to_predict, axis=0))
    print (Squat_result[np.argmax(res)])