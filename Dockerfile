FROM python:3
ENV PYTHONBUFFERED=1

# Instala las dependencias necesarias
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    python3-dev \
    ldap-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

COPY . /code/

EXPOSE 8000
RUN chmod +x /code/run.sh
ENTRYPOINT [ "sh", "/code/run.sh" ]
