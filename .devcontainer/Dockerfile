FROM registry.gitlab.com/islandoftex/images/texlive:TL2024-2024-11-10-full-doc-src

RUN apt update
RUN apt install -y python3 python3-pip git openssh-client


# tlmgr runs in usermode on debian, so we need to setup a usertree
RUN tlmgr init-usertree

# COPY latexminted file and put it into the right place
COPY ./.texmf/.latexminted_config ./.latexminted_config
RUN cp ./.latexminted_config $(kpsewhich --var-value TEXMFHOME)/.latexminted_config