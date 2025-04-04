# .dodenv

## Docker Development Environment

🚧 **Work in Progress** 🚧

`.dodenv` is a Python-based script designed to create a DevContainer-like environment for 
development projects. It automates building and running Docker containers, providing a 
seamless development experience.

## Overview

`.dodenv` simplifies containerized development by:

- Building a Docker image from a specified Dockerfile.
- Running a container and attaching the terminal to an interactive bash session.
- Removing the container upon exit.
- Supporting multiple terminals attaching to the same container.
- Allowing selection of different Dockerfiles and passing additional `docker run` arguments.

This repository can be cloned into any project, and multiple Dockerfiles can be managed 
using `.dodenv`. By default, a `Dockerfile` is provided, which installs Neovim and tmux along 
with my custom configuration inside the container.

## Prerequisites

- Python 3
- Docker Engine

## Variants

Different Dockerfiles can be used for various project setups. Below are some available variants:

- Dockerfile (default): Installs Neovim 10.4 and tmux with my custom configurations and some additional utilities.
- Dockerfile.ESP-IDF: Builds ESP-IDF v5.4 for ESP-based development.

## Usage

### Running the Development Environment

1. Clone this repository inside your project:
   ```sh
   git clone <repository_url> .dodenv
   ```
2. Create a custom Dockerfile or modify the default one (e.g., `Dockerfile.MY_CUSTOM`).
3. Run the following command to start the container using the default Dockerfile:
   ```sh
   sudo ./.dodenv/dodenv.py run
   ```
   To use a custom Dockerfile:
   ```sh
   sudo ./.dodenv/dodenv.py run MY_CUSTOM
   ```
4. Optionally, pass arguments to `docker run`, for example:
   ```sh
   sudo ./.dodenv/dodenv.py run MY_CUSTOM --device=/dev/tty0
   ```

Each execution of the `run` command attaches the terminal to a bash session inside the container. 
If executed in another terminal, a new bash session opens within the same container.

`.dodenv` leverages Docker's caching mechanism for efficiency. If the Dockerfile changes, the 
container is stopped, removed, and recreated to reflect the updates.

**Tip:** If you are using tmux, try my plugin [projactions](https://github.com/TomOdw/projactions). 
Add a project specific `.dodenv` `run` command to the `Environment` keybind, to easily start dodenv.

### Deleting the Development Environment

To stop and remove the container along with its associated Docker image (while keeping the cache 
intact), run:

```sh
sudo python3 .dodenv/dodenv.py delete
```

### Resetting the Development Environment

To delete and immediately recreate the environment, run:

```sh
sudo python3 .dodenv/dodenv.py reset
```

This effectively executes `delete` followed by `run`, ensuring the latest configuration is applied.

---

For contributions, issues, or feature requests, feel free to open an issue or submit a pull request. 🚀


