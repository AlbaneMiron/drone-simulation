FROM python:3

WORKDIR /work/

CMD python index.py
EXPOSE 8050

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV BIND_HOST 0.0.0.0
