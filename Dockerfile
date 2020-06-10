FROM ubuntu:18.04 as openvmdk-build
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install \
        build-essential zlib1g-dev git
WORKDIR /build
RUN git clone https://github.com/vmware/open-vmdk
RUN cd open-vmdk && make && make install
CMD mkova.sh --help
