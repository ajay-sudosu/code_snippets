FROM ubuntu:20.04

ARG DEBIAN_FRONTEND="noninteractive"

# set the variables as per $(pyenv init -)
ENV LANG="C.UTF-8" \
    LC_ALL="C.UTF-8" \
    PATH="/opt/pyenv/shims:/opt/pyenv/bin:$PATH" \
    PYENV_ROOT="/opt/pyenv" \
    PYENV_SHELL="bash" \
    PYTHON_VERSION=3.8.10

RUN apt-get update
RUN apt-get install -y --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget ca-certificates curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev mecab-ipadic-utf8 libmysqlclient-dev python-dev git python3-cupshelpers command-not-found ec2-hibinit-agent hibagent libcairo2-dev python3-six python-six python3-systemd libdbus-1-dev libsystemd-dev ubuntu-advantage-tools ufw unattended-upgrades libcups2-dev python3-dev gcc python3-gi python3-gi-cairo gir1.2-gtk-3.0 libgirepository1.0-dev
# Install pyenv
RUN set -ex \
    && curl https://pyenv.run | bash \
    && pyenv update \
    && pyenv install $PYTHON_VERSION \
    && pyenv global $PYTHON_VERSION \
    && pyenv rehash

RUN curl https://bootstrap.pypa.io/get-pip.py | python
RUN pip install six cmake

RUN mkdir backend
WORKDIR backend
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN mkdir upload
COPY . .
EXPOSE 5039
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5039", "--reload"]

