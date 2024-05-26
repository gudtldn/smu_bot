FROM python:3.12-slim

COPY ./ /data
WORKDIR /data

RUN pip install -r requirements.txt

CMD [ "python3", "-m", "src.main" ]
