FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-devel
USER root

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG HTTP_PROXY
ARG HTTPS_PROXY
ENV http_proxy=$HTTP_PROXY
ENV https_proxy=$HTTPS_PROXY

# cronのインストール
RUN apt-get update && apt-get install -y cron
RUN apt-get install -y nfs-common
RUN mkdir -p /root/src
RUN mkdir -p /root/src/nas
COPY requirements.txt /root/src
WORKDIR /root/src

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

RUN pip install -r requirements.txt

RUN apt-get install -y tmux

# cronjobファイルのコンテナへのコピー
COPY cronjob /etc/cron.d/cronjob

# ファイルのパーミッションを設定
RUN chmod 0644 /etc/cron.d/cronjob

# cronデーモンを起動するためのスクリプトを追加（後で作成）
# COPY start-cron.sh /root/start-cron.sh
# RUN chmod +x /root/start-cron.sh
