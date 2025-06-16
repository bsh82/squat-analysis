# squat-analyze Spring Boot JWT 기반 분석 서버
Spring Boot, Spring Security, JWT를 활용한 스쿼트 자세 분석 백엔드 서버입니다. 딥러닝 모델을 통한 운동 자세 분석과 AWS S3 파일 저장, RDS 데이터베이스 연동을 제공합니다.

# 🚀 주요 기능
JWT 기반 인증/인가: Spring Security를 통한 토큰 기반 보안

스쿼트 자세 분석: MediaPipe + LSTM 딥러닝 모델을 활용한 실시간 자세 분석

파일 관리: AWS S3를 통한 비디오 파일 업로드/다운로드

데이터베이스: AWS RDS MySQL을 통한 사용자 및 분석 결과 관리

RESTful API: 표준화된 REST API 제공

# 🛠️ 기술 스택
Backend
Framework: Spring Boot 3.x

Security: Spring Security 6 + JWT

Database: Spring Data JPA + MySQL

AI/ML: TensorFlow Lite + MediaPipe

Cloud: AWS S3, AWS RDS

Build Tool
Maven 3.8+

DBMS
AWS RDS MySQL 8.0

# 📋 사전 요구사항
Java 17 이상

Maven 3.8+

AWS 계정 (S3, RDS 사용)

MySQL 8.0 (로컬 개발용)

# AWS S3 설정
aws:
  s3:
    bucket: ${S3_BUCKET_NAME}
    region: ${AWS_REGION}
    access-key: ${AWS_ACCESS_KEY}
    secret-key: ${AWS_SECRET_KEY}

# JWT 설정
jwt:
  secret: ${JWT_SECRET}
  expiration: 86400000 # 24시간

4. 환경 변수 설정
bash
export DB_USERNAME=your_db_username
export DB_PASSWORD=your_db_password
export JWT_SECRET=your_jwt_secret_key
export S3_BUCKET_NAME=your_s3_bucket
export AWS_REGION=ap-northeast-2
export AWS_ACCESS_KEY=your_aws_access_key
export AWS_SECRET_KEY=your_aws_secret_key

5. AWS RDS 데이터베이스 생성
AWS Console에서 RDS 서비스 접속

MySQL 8.0 인스턴스 생성 (Free Tier 선택)

데이터베이스 이름: squat_analyzer

보안 그룹에서 3306 포트 허용

6. AWS S3 버킷 생성
AWS Console에서 S3 서비스 접속

새 버킷 생성 (예: squat-analysis-videos)

퍼블릭 액세스 차단 해제 (필요시)

# 🚀 실행
개발 환경
bash
mvn spring-boot:run
프로덕션 환경
bash
mvn clean package
java -jar target/squat-analyzer-0.0.1-SNAPSHOT.jar
서버는 기본적으로 http://localhost:8080에서 실행됩니다.
