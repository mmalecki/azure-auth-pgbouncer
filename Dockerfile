FROM python:3.13-alpine3.21 AS build

RUN pip install poetry

RUN poetry config virtualenvs.create false

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN python -m venv venv
RUN . ./venv/bin/activate && poetry install --no-root

FROM python:3.13-alpine3.21

ARG RUN_DIR=/run/pgbouncer

RUN addgroup -S pgbouncer && adduser -G pgbouncer -S -D -H -s /bin/false pgbouncer
RUN apk --no-cache add pgbouncer
RUN mkdir -p $RUN_DIR && chown pgbouncer:pgbouncer $RUN_DIR

WORKDIR /app
COPY --from=build /app/venv /app/venv/
COPY azure_auth_pgbouncer.py entrypoint.sh ./

USER pgbouncer
ENV PGBOUNCER_RUN_DIR=$RUN_DIR
ENTRYPOINT ["./entrypoint.sh"]
