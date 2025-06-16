# React JWT 비디오 분석 애플리케이션
백엔드와 연동되는 JWT 기반 인증 시스템을 갖춘 React 애플리케이션입니다.

# 🚀주요 기능

- JWT 기반 사용자 인증 (ACCESS/REFRESH 토큰)
- 비디오 파일 업로드 및 분석
- 드래그 앤 드롭 파일 업로드
- 자동 토큰 갱신
- 반응형 디자인

# 설치 및 실행

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm start

# 빌드
npm run build
```

# API 엔드포인트

- `POST /login` - 로그인
- `POST /join` - 회원가입
- `POST /upload` - 비디오 업로드 및 분석
- `POST /reissue` - 토큰 재발급
- `POST /logout` - 로그아웃

# 🛠️기술 스택

- React 18
- React Router DOM
- Axios
- Context API
- CSS Grid/Flexbox

# 폴더 구조

```
src/
├── components/     # 재사용 가능한 컴포넌트
├── pages/         # 라우팅 페이지
├── services/      # API 통신 로직
├── context/       # Context API
├── utils/         # 유틸리티 함수
└── styles/        # CSS 스타일
```

# 보안 특징

- ACCESS 토큰은 메모리에 저장 (XSS 방지)
- REFRESH 토큰은 HttpOnly 쿠키에 저장
- 자동 토큰 갱신 시스템
- CORS 정책 준수
