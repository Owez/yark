# syntax=docker/dockerfile:1
FROM python:3.11 as build
ARG POETRY_VERSION=1.3.2
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install "poetry==${POETRY_VERSION}" \
 && poetry config virtualenvs.create false \
 && poetry install --no-dev \
 && poetry export --format=requirements.txt > requirements.txt

FROM python:3.11
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  DOCKER_CONTAINER=1

WORKDIR /app
COPY --from=build /app/requirements.txt /app/

RUN addgroup --system --gid 1000 yark \
 && adduser --system -u 1000 --gid 1000 yark \
 && pip install -r requirements.txt

COPY . /app/

VOLUME ["/yark"]

USER yark

WORKDIR /app

RUN pip install .

EXPOSE "7667/tcp"

ENTRYPOINT [ "/home/yark/.local/bin/yark" ]

WORKDIR /yark

CMD ["view"]
