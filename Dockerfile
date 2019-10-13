FROM python:3 AS base

WORKDIR /work/

CMD python index.py
EXPOSE 8050

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY sankey/sankey/*.py sankey/sankey/*.js sankey/sankey/*.json sankey/sankey/*.js.map /usr/local/lib/python3.7/site-packages/sankey/

ENV BIND_HOST 0.0.0.0

FROM base AS test

COPY requirements-test.txt .
RUN pip install -r requirements-test.txt
COPY *.py .pycodestyle ./
# Lint files.
RUN pycodestyle --config=.pycodestyle *.py
RUN pylint *.py --disable=C0111,W0511,C0103,R --additional-builtins=_

# Compile translation files.
COPY locales/fr/LC_MESSAGES/*.po locales/fr/LC_MESSAGES/
RUN pybabel compile -d locales -l fr

FROM base AS prod

COPY *.py ./
COPY assets ./assets
COPY data ./data
COPY --from=test /work/locales /work/locales

FROM base
