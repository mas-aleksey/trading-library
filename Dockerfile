FROM python:3.11-slim-bullseye as build-image

RUN pip install --no-cache-dir --upgrade pip poetry && rm -rf /home/root/.cache/*

WORKDIR /opt

COPY ./pyproject.toml ./poetry.lock ./

RUN poetry config virtualenvs.create false || true && poetry install --no-root

FROM python:3.11-slim-bullseye as app-image

RUN apt-get update && apt-get install -y libglu1-mesa netcat curl dos2unix
COPY --from=build-image /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=build-image /usr/local/src/ /usr/local/src/
COPY --from=build-image /usr/local/bin/ /usr/local/bin/

WORKDIR /opt

COPY ./pyproject.toml ./alembic.ini ./entrypoint.sh ./
RUN dos2unix ./entrypoint.sh
RUN ["chmod", "+x", "./entrypoint.sh"]

COPY src/ src/
ENTRYPOINT ["/opt/entrypoint.sh"]

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "src/core/logging.yaml"]