FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED=1


RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt install -y libsm6 libxext6

RUN apt-get -y install tesseract-ocr tk

RUN apt-get install -y \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev
    
COPY . ./
RUN mv nep.traineddata /usr/share/tesseract-ocr/4.00/tessdata
RUN mv eng.traineddata /usr/share/tesseract-ocr/4.00/tessdata 
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

