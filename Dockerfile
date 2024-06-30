###############################################################################
## Final image
###############################################################################
FROM alpine:3.18

LABEL maintainer="CROKETILLO (croketillo@gmail.com)"

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONIOENCODING=utf-8 \
    PYTHONUNBUFFERED=1 \
    USER=app \
    UID=1000

RUN echo "**** install Python ****" && \
    apk add --update --no-cache --virtual \
            .build-deps \
            gcc~=12.2 \
            musl-dev~=1.2 \
            python3-dev~=3.11 \
            python3~=3.11 \
            py3-pip~=23.1 

COPY ./src /app/

RUN pip3 install -r /app/requirements.txt


RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/${USER}" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    "${USER}" && \
    chown -R app:app /app 

WORKDIR /app
USER app

CMD ["/bin/sh", "/app/entrypoint.sh"]
