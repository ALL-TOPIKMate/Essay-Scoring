# 기본 이미지로 OpenJDK 11 이미지 사용
FROM openjdk:11

# 필요한 패키지 설치
RUN apt-get update -y && apt-get install -y python3 python3-pip

# Flask 앱을 위한 작업 디렉토리 생성
WORKDIR /app

# Flask 앱 소스 코드를 컨테이너로 복사
COPY . /app

ENV JAVA_HOME /usr/lib/jvm/java-1.7-openjdk/jre
RUN apt-get update && apt-get install -y g++ default-jdk
RUN apt-get update -y && apt-get install -y python3 python3-pip

# Python 패키지 설치
RUN pip3 install -r requirements.txt

ARG FLASK_ENV
ENV FLASK_ENV=${FLASK_ENV}
EXPOSE 5000

# Flask 앱 실행
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]