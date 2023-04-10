FROM python:3.10
RUN mkdir /app
WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY . .

RUN chmod a+x *.sh