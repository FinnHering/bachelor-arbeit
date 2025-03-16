FROM registry.gitlab.com/islandoftex/images/texlive:TL2025-2025-03-16-full-doc-src

RUN apt update \
    && apt upgrade -y \
    && apt install -y \ 
        python3 \ 
        python3-pip \ 
        git \ 
        openssh-client \ 
        wget \
        apt-utils \
        openssh-client \
        gnupg2 \
        dirmngr \
        iproute2 \
        procps \
        lsof \
        htop \
        net-tools \
        psmisc \
        curl \
        wget \
        rsync \
        ca-certificates \
        unzip \
        zip \
        nano \
        vim-tiny \
        less \
        jq \
        lsb-release \
        apt-transport-https \
        dialog \
        libc6 \
        libgcc1 \
        libkrb5-3 \
        libgssapi-krb5-2 \
        libicu* \
        liblttng-ust* \
        libstdc++6 \
        zlib1g \
        locales \
        sudo \
        ncdu \
        man-db \
        strace \
        manpages \
        manpages-dev \
        init-system-helpers

# tlmgr runs in usermode on debian, so we need to setup a usertree
RUN tlmgr init-usertree

# COPY latexminted file and put it into the right place
COPY ./.texmf/.latexminted_config ./.latexminted_config
RUN cp ./.latexminted_config $(kpsewhich --var-value TEXMFHOME)/.latexminted_config

# Setup Java for Ltex plugin, and set JAVA_HOME
RUN apt install -y default-jre
ENV JAVA_HOME="/usr/lib/jvm/default-java"