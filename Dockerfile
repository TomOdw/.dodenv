FROM  debian:12

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

#Install with apt
RUN apt update && \
    apt upgrade -y && \
    apt install -y \
      wget \
      ripgrep \
      gcc \
      make \
      cmake \
      git \
      npm \
      unzip

#Install neovim 10.4
RUN cd ~ && \
    wget https://github.com/neovim/neovim-releases/releases/download/v0.10.4/nvim-linux-x86_64.deb && \
    apt install -y ./nvim-linux-x86_64.deb && \
    rm nvim-linux-x86_64.deb

#Clone my dotfiles for neovim
RUN cd ~ && \
    git clone https://github.com/TomOdw/dotfiles.git && \
    mkdir .config && \
    cp -a dotfiles/.config/nvim .config/ && \
    rm -r dotfiles

#Start neovim for lazy install
RUN nvim --headless +qall!

#Now MasonInstallAll
RUN nvim --headless +MasonInstallAll +qall!
