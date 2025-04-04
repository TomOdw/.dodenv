FROM  debian:12

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

# Install with apt
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

# Install neovim 10.4
RUN cd ~ && \
    wget https://github.com/neovim/neovim-releases/releases/download/v0.10.4/nvim-linux-x86_64.deb && \
    apt install -y ./nvim-linux-x86_64.deb && \
    rm nvim-linux-x86_64.deb

# Install tmux
RUN apt install -y tmux

# Clone my dotfiles, and load submodules
RUN cd ~ && \
    git clone https://github.com/TomOdw/dotfiles.git && \
    cp -a dotfiles/. . && \
    rm -r dotfiles &&\
    git submodule init && \
    git submodule update
 
# neovim installation
# Start neovim for lazy install
RUN nvim --headless +qall!
# Now MasonInstallAll
RUN nvim --headless +MasonInstallAll +qall!

# tmux installation
# autostart tmux
RUN echo "tmux -u" >> /root/.bashrc
