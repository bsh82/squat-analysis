import React, { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { uploadApi } from '../services/api';

const Upload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);

  const fileInputRef = useRef(null);
  const { user, logout } = useAuth();

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type.startsWith('video/')) {
      setFile(selectedFile);
      setError('');
      setResult(null);
    } else {
      setError('비디오 파일만 업로드 가능합니다.');
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    handleFileSelect(selectedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('파일을 선택해주세요.');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('upload', file);

      const response = await uploadApi.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: true
      });

      setResult(response.data);
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      setError(error.response?.data?.message || '업로드 중 오류가 발생했습니다.');
    } finally {
      setUploading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="upload-container">
      <header className="upload-header">
        <h1>스쿼트 분석</h1>
        <div className="user-info">
          <span>환영합니다, {user?.realName || user?.username}님!</span>
          <button onClick={handleLogout} className="logout-button">
            로그아웃
          </button>
        </div>
      </header>

      <main className="upload-main">
        <div className="upload-section">
          <h2>비디오 업로드</h2>

          <div 
            className={`upload-area ${dragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="video/*"
              style={{ display: 'none' }}
            />

            {file ? (
              <div className="file-info">
                <p>선택된 파일: {file.name}</p>
                <p>크기: {(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            ) : (
              <div className="upload-placeholder">
                <p>비디오 파일을 드래그하거나 클릭하여 선택하세요</p>
                <p>지원 형식: MP4, AVI, MOV</p>
              </div>
            )}
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            onClick={handleUpload} 
            disabled={!file || uploading}
            className="upload-button"
          >
            {uploading ? '분석 중...' : '업로드 및 분석'}
          </button>
        </div>

        {result && (
          <div className="result-section">
            <h2>분석 결과</h2>
            <div className="result-content">
              <div className="score-section">
                <h3>점수</h3>
                <div className="score">{result.score}점</div>
              </div>

              <div className="feedback-section">
                <h3>피드백</h3>
                <div className="feedback">
                  {result.feedBack || '피드백이 없습니다.'}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Upload;