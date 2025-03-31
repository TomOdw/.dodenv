# .dodenv
Docker Development Environment

**Work in progress**

My attempt of creating a DevContainer-like environment for my projects.

Basically just a python script, which builds a docker image from a dockerfile, 
creates and starts a container, and opens a container-bash.

Repository can be cloned in any project. Multiple Dockerfiles can be used by dodenv.
They are referenced with the run command, and a possible file extension as a second 
argument. If no second argument is passed, the 'default' Dockerfile is used, which 
currently installs neovim and my configuration within the container.


## Prerequisites
- Python3
- docker-engine


## Derivates
Here I list my Derivates of dodenv (just other Dockerfiles for conveniently setting up my 
different types of projects, e.g. for developing with ESP-IDF)
- Dockerfile (default): Neovim 10.4 with my config, other stuff.
- Dockerfile.ESP-IDF: Builds ESP-IDF v5.4

## Usage
### Run the development environment
1. Within your project, clone the repository.
3. Add a Dockerfile with a custom extension or customize the default Dockerfile, e.g.: 
Dockerfile.MY_CUSTOM
4. Run ```sudo python3 .dodenv/dodenv.py run``` to use the default Dockerfile or: 
```sudo python3 .dodenv/dodenv.py run MY_CUSTOM``` to use the created (or existing) 
dockerfile

**Hint:**
Best practise is to place a shell-script within the project, e.g.: dodenv
```sh
#!/bin/bash

sudo python3 ./.dodenv/dodenv.py run MY_CUSTOM
```
Make it executable with chmod +x and you have an convenient way to start the development 
environment.

The current terminal gets a bash session within the container. To attach another 
terminal to the container, simply execute the command again and a new bash session 
will open in the new terminal. 

dodenv relies on docker cache, to run fast (every run execution will build a 
temporary docker image, it checks if the image id matches with a prior build, if it 
doesn't match, i.e. the Dockerfile was altered, the docker container is stopped, 
removed and recreated).

### Delete the development environment
Run ```sudo python3 .dodenv/dodenv.py delete```

Stops the container and removes it, deletes the docker image, cache remains untouched.

### Reset the developement environment
Run ```sudo python3 .dodenv/dodenv.py reset```

Simply executes the delete command, followed by the run command.
