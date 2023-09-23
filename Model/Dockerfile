# 기본 이미지로 ubuntu 사용
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive \
    JAVA_HOME = /usr/lib/jvm/java-17-openjdk-amd64
# 필요한 패키지 설치
RUN apt-get update -y && \
    apt-get install -y openjdk-17-jdk python3 python3-pip g++ default-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Flask 앱을 위한 작업 디렉토리 생성
WORKDIR /app

# Flask 앱 소스 코드를 컨테이너로 복사
COPY app.py requirements.txt /app/
COPY check_function /app/check_function/

# Python 패키지 설치
RUN pip install -r requirements.txt

ARG FLASK_ENV
ENV FLASK_ENV=${FLASK_ENV}
EXPOSE 5000

# Flask 앱 실행
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]