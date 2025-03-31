# .dodenv
Docker Development Environment

**Work in progress**

My attempt of creating a DevContainer-like environment for my projects.

Basically just a python script, which builds a docker image from a dockerfile, 
creates and starts a container, and opens a container-bash.

Repository can be cloned in any project, dodenv uses any Dockerfile, which is 
present within the .dodenv directory. Currently neovim and my configuration is 
installed within the container.


## Prerequisites
- Python3
- docker-engine


## Branches
Here I list branches of dodenv (just other Dockerfiles for conveniently setting up my 
different types of projects, e.g. for developing with ESP-IDF)
- ESP-IDF: TODO Description

## Usage
### Run the development environment
1. Within your project, clone the repository.
2. Remove the .git folder within .dodenv.
3. Customize the Dockerfile
4. Run ```sudo python3 .dodenv/dodenv.py run```

The current terminal then is a bash session within the container. To attach another 
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
