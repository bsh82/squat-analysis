import os
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Masking, Bidirectional, LSTM, Dense, Dropout, BatchNormalization
)
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

# 데이터 로드 및 정규화
base_dir = os.path.dirname(__file__)
X = np.load(os.path.join(base_dir, 'Features.npy'))  # 형태: (240, 191, 132)
y = np.load(os.path.join(base_dir, 'Labels.npy'))    # 형태: (240, 2)

# 데이터 정규화 (Z-score)
flat = X.reshape(-1, X.shape[-1])
mean, std = flat.mean(axis=0), flat.std(axis=0) + 1e-6
X = (X - mean) / std

# 정규화 파라미터 저장 (나중에 예측할 때 사용)
np.save(os.path.join(base_dir, 'mean.npy'), mean)
np.save(os.path.join(base_dir, 'std.npy'), std)

# 데이터 증강 함수들
def add_noise(seq, noise_level=0.01):
    """시퀀스에 가우시안 노이즈 추가"""
    noise = np.random.normal(0, noise_level, seq.shape)
    return seq + noise

def dropout_frames(seq, drop_prob=0.1):
    """랜덤하게 프레임 드롭아웃"""
    mask = np.random.rand(len(seq)) > drop_prob
    return seq[mask]

# 데이터 증강 적용
augmented = []
for seq in X:
    seq_aug = add_noise(seq)  # 노이즈 추가
    seq_aug = dropout_frames(seq_aug)  # 프레임 드롭아웃
    # 원래 길이로 패딩
    padded = tf.keras.preprocessing.sequence.pad_sequences(
        [seq_aug], maxlen=X.shape[1], padding='post', value=0.0
    )[0]
    augmented.append(padded)

# 원본 + 증강 데이터 결합
X_aug = np.vstack([X, np.array(augmented)])
y_aug = np.vstack([y, y])

# 훈련/테스트 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(
    X_aug, y_aug, test_size=0.2, random_state=42, stratify=y_aug
)

# BiLSTM 모델 빌더
def build_bilstm(input_shape, lstm_units=128, dropout_rate=0.3):
    """양방향 LSTM 모델 구성"""
    model = Sequential([
        Masking(mask_value=0., input_shape=input_shape),  # 패딩 마스킹
        Bidirectional(LSTM(lstm_units, return_sequences=True, activation='tanh')),
        Dropout(dropout_rate),
        Bidirectional(LSTM(lstm_units // 2, activation='tanh')),
        BatchNormalization(),
        Dropout(dropout_rate),
        Dense(32, activation='relu'),
        BatchNormalization(),
        Dropout(dropout_rate),
        Dense(2, activation='softmax')  # 2클래스 분류
    ])
    return model

# 콜백 설정
callbacks = [
    EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1),
    ModelCheckpoint('best_model.h5', monitor='val_accuracy', save_best_only=True, verbose=1)
]

# 모델 훈련 및 평가 함수
def train_and_evaluate(model, name, batch_size=64, epochs=50):
    """모델 훈련하고 성능 평가"""
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    print(f"\n>> {name} 모델 훈련 시작")
    
    # 모델 훈련
    model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=2
    )
    
    # 테스트 성능 평가
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"{name} -- 테스트 손실: {loss:.4f}, 정확도: {acc:.4f}\n")

# 모델 실행
input_shape = X_train.shape[1:]  # (191, 132)

# 모델 딕셔너리(향후 모델 추가 가능)
models = {
    'BiLSTM': build_bilstm(input_shape, lstm_units=128, dropout_rate=0.3)
}

# 모델 훈련 및 평가
for name, mdl in models.items():
    train_and_evaluate(mdl, name)