FROM python:3.10-slim
LABEL maintainer="guillaume@gauvr.it"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv/casualcms
EXPOSE 8000

RUN pip install poetry

RUN useradd casualcms --home /home/casualcms && \
    mkdir -p /home/casualcms && \
    chown -R casualcms:casualcms /home/casualcms && \
    chown -R casualcms:casualcms /srv/casualcms
USER casualcms

COPY pyproject.toml poetry.lock /srv/casualcms/
# Bug in poetry for hypercorn
# See https://github.com/python-poetry/poetry/issues/7572#issuecomment-1447608308
RUN poetry config installer.modern-installation false && poetry install --only main
COPY . /srv/casualcms/
RUN poetry install --only main

CMD ["poetry", "run", "casualcms"]
