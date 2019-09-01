FROM python:3 AS base

WORKDIR /work/

CMD python index.py
EXPOSE 8050

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV BIND_HOST 0.0.0.0

FROM base AS test

COPY requirements-test.txt .
RUN pip install -r requirements-test.txt
COPY *.py .pycodestyle ./
# Lint files.
RUN pycodestyle --config=.pycodestyle *.py
RUN pylint *.py --disable=C0111,W0511,C0103,R

FROM base