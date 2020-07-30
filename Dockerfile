FROM openjdk:8

WORKDIR /tw_stock_crawler

COPY requirements.txt ./

RUN \
    echo "deb https://dl.bintray.com/sbt/debian /" | tee -a /etc/apt/sources.list.d/sbt.list && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 642AC823 && \
    apt-get update && \
    apt-get install sbt && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip && \
    pip3 install --no-cache-dir -r requirements.txt

ADD . /tw_stock_crawler

CMD sbt run enable
