FROM ubuntu:16.04

LABEL MAINTAINER mihael.arcan@insight-centre.org

RUN apt-get update && apt-get install -y vim apache2 build-essential libboost-dev libboost-all-dev cmake git-core libplack-perl libjson-perl libcgi-pm-perl python3-pip python-pip wget cron

RUN pip install numpy

RUN git clone https://github.com/eigenteam/eigen-git-mirror.git /home/tools/eigen/
ENV EIGEN3=/home/tools/eigen/
WORKDIR $EIGEN3
RUN mkdir $EIGEN3/build_dir
WORKDIR $EIGEN3/build_dir
RUN cmake /home/tools/eigen
RUN make install

RUN git clone https://github.com/OpenNMT/CTranslate.git /home/tools/CTranslate/
ENV CT=/home/tools/CTranslate/
WORKDIR $CT
RUN git submodule update --init
RUN mkdir -p $CT/build
WORKDIR $CT/build
RUN cmake ..
RUN make
RUN mkdir -p /home/tools/CTranslate/lib/tokenizer/build
WORKDIR $CT/lib/tokenizer/build
RUN cmake -DCMAKE_BUILD_TYPE=Release ..
RUN make

RUN apt-get update && apt-get install -q -y unzip make g++ wget git git-core mercurial bzip2 autotools-dev automake libtool zlib1g-dev libbz2-dev libboost-all-dev libxmlrpc-core-c3-dev libxmlrpc-c++8-dev build-essential pkg-config python-dev cmake libcmph-dev libcmph-tools libcmph0 libgoogle-perftools-dev liblzma-dev
RUN git clone https://github.com/moses-smt/mosesdecoder.git /tmp/mosesdecoder
RUN mkdir -p /home/tools/mosesdecoder
WORKDIR /tmp/mosesdecoder
RUN ./bjam --prefix=/home/tools/mosesdecoder --install-scripts --with-cmph=/usr/include/cmph -j2
RUN rm -rf /tmp/mosesdecoder
WORKDIR /

RUN wget http://server1.nlp.insight-centre.org/docker_files/iris_files.zip
RUN unzip iris_files.zip

RUN mv html/* /var/www/
RUN rm -r html/
RUN mkdir -p /var/www/cgi-bin
RUN mv cgi-bin/* /var/www/cgi-bin
RUN rm -r cgi-bin/
RUN chmod 777 /var/www/cgi-bin/*

RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN mv 000-default.conf /etc/apache2/sites-available/000-default.conf 

RUN mkdir -p /var/www/models
RUN chmod 777 -R /var/www/models

## Open port 80
EXPOSE 80
RUN a2enmod cgi
## Start Apache service
CMD service apache2 start && sleep infinity

