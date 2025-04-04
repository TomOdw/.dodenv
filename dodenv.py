#!/usr/bin/env python3

# @file     dodenv.py
# @author   Tom Christ
# @date     2025-03-31
#
# @brief    Python script for building dockerfiles, creating/starting/
#           attaching to them. Realizes a Docker Development Environment.
#
# @version  0.1   -  Initial Version   -  Tom Christ
#
# @copyright  Copyright (c) 2025 Tom Christ; MIT License


import sys
import os
import subprocess


# ### Functions ####
def main():
    # Global declarations
    global const_ProjectPath
    global const_ContainerName
    global const_ImageName
    global static_Dockerfile_extension
    global static_ImageGotUpdate
    global static_AdditionalDockerArgs

    # Set project path
    current_path = os.path.abspath(__file__)
    const_ProjectPath = os.path.abspath(
        os.path.join(current_path, "..", ".."))

    # Set Container and image Name
    const_ContainerName = os.path.basename(const_ProjectPath).lower()
    const_ImageName = const_ContainerName + "_img"

    # initilize global static vars
    static_Dockerfile_extension = ""
    static_ImageGotUpdate = False
    static_AdditionalDockerArgs = ""

    # Evaluate Arguments
    command = ""
    argv = sys.argv[1:]  # Get the file name out of here
    argc = len(argv)
    if argc >= 1:
        # set the command update arg
        command = argv[0]
        argv = argv[1:]
        argc = len(argv)
        # next argument might be the dockerfile extension, test that
        if argc >= 1:
            the_possible_path = os.path.join(const_ProjectPath,
                                             ".dodenv",
                                             "Dockerfile." + argv[0])
            if os.path.exists(the_possible_path):
                # Yes next arg is a dockerfile extension
                static_Dockerfile_extension = "." + argv[0]
                # Update arg
                argv = argv[1:]
                argc = len(argv)
        # Next args are additional docker flags
        if argc >= 1:
            # Have additional args
            static_AdditionalDockerArgs = " ".join(argv)
    else:
        return show_help()

    # Show what we have evaluated
    print(
        "[INFO]: " +
        "Docker image name will be: " + const_ImageName)
    print(
        "[INFO]: " +
        "Docker container name will be: " + const_ContainerName)
    print(
        "[INFO]: " +
        "Using Dockerfile: Dockerfile" + static_Dockerfile_extension)
    if static_AdditionalDockerArgs != "":
        print(
            "[INFO]: " +
            "Additional Docker run args: " + static_AdditionalDockerArgs)

    # Execute the command
    match command:
        case "run":
            return run()
        case "delete":
            return delete()
        case "reset":
            return reset()
        case _:
            return show_help()


def show_help():
    print(
        "Usage: python3 dodenv.py COMMAND [DOCKFILE-EXT] [DOCKER-RUN-ARGS...]\n\n" +
        "Commands:\n" +
        "   run     Run the Docker Developemnt Environment. Builds the container\n" +
        "           image (or rebuild if the Dockerfile was changed). Executes\n" +
        "           docker run and attatches the terminal to a container bash.\n" +
        "           Container is rm after exit of the bash, if the run command\n" +
        "           is called within another terminal, a new bash is opened with\n" +
        "           the same container. Takes (DOCKFILE_EXT and DOCKER-RUN-ARGS)\n" +
        "           as arugments.\n" +
        "   delete  Stops and removes the container, removes the container image.\n" +
        "   reset   Calls delete follwed by run, takes the same arguments as run.\n" +
        "           (DOCKFILE_EXT and DOCKER-RUN-ARGS)\n" +
        "\n\n" +
        "DOCKFILE-EXT:      If present, the container image is build with a file\n" +
        "                   named: Dockerfile.{DOCKFILE-EXT} (need to be present\n" +
        "                   within the .dodenv folder.) Otherwise the container\n" +
        "                   is build with the default 'Dockerfile' file.\n\n" +
        "DOCKER-RUN-ARTGS:  These are an arbitrary number of arguments, which are\n" +
        "                   passed to the 'docker run' command, e.g. to attach a\n" +
        "                   device to the container with '--device=/dev/...'\n"
    )
    return 0


def run():
    # Call Build, which Checks if the dockerfile was updated,
    # If thats the case, a possibly running container is stopped
    # and removed.
    print(
        "[STAGE RUN  ][INFO]: " +
        "Calling build stage...")
    result = build()
    if result != 0:
        return result
    print(
        "[STAGE RUN  ][INFO]: " +
        "Build stage returned sucessfully.")
    # Check if the container is running.
    print(
        "[STAGE RUN  ][INFO]: " +
        "Cecking if container is running...")
    subprocessout = subprocess.run(
            "sudo docker ps -a --format \"{{.Names}}\"",
            shell=True, capture_output=True)
    outstring = subprocessout.stdout.decode().strip()
    if outstring != "":
        # There are existing containers
        lines = outstring.split("\n")
        for line in lines:
            if line.find(const_ContainerName) != -1:
                # The Container Exsits, attach to it
                print(
                    "[STAGE RUN  ][INFO]: " +
                    "Conatiner is running, " +
                    "starting new bash within container...")
                subprocessout = subprocess.run(
                    "sudo docker exec -it -w /root/workspace "
                    + const_ContainerName +
                    " bash", shell=True)
                print(
                    "[STAGE RUN  ][INFO]: " +
                    "Done, container exec bash returned.")
                return 0
    else:
        # The Container is not running.
        print(
            "[STAGE RUN  ][INFO]: " +
            "Conatiner is not running, " +
            "calling docker run command...")
        this_files_path = os.path.abspath(__file__)
        project_path = os.path.abspath(
            os.path.join(this_files_path, "..", "..")
        )
        subprocessout = subprocess.run(
            "sudo docker run -it --name " + const_ContainerName +
            " -v " + project_path + ":/root/workspace " +
            " -w /root/workspace "
            " --rm " +
            static_AdditionalDockerArgs + " " +
            const_ImageName + " bash",
            shell=True)
        print(
            "[STAGE RUN  ][INFO]: " +
            "Done, container run bash returned.")
        return 0
    # Should not be reached
    return -1


def build():
    # Build the Dockerfile as temp
    tempImageName = const_ImageName + "_temp"
    print(
        "[STAGE BUILD][INFO]: " +
        "Building temporary container image...")
    print(static_Dockerfile_extension)
    subprocessout = subprocess.run(
            "sudo docker build . -f " + const_ProjectPath +
            "/.dodenv/Dockerfile" + static_Dockerfile_extension +
            " -t " + tempImageName, shell=True)
    # Dont capture the output here, next step is verifying it...

    # Get Existing images, id from names:
    print(
        "[STAGE BUILD][INFO]: " +
        "Check Existing container images...")
    subprocessout = subprocess.run(
        "sudo docker images --format \"{{.Repository}},{{.ID}}\"",
        shell=True, capture_output=True)
    outstring = subprocessout.stdout.decode().strip()
    if outstring == "":
        print(
            "[STAGE BUILD][ERROR]: " +
            "Docker images returned empty string")
        return -1  # Should not happen, we built at least the temp...
    image_id = ""
    image_temp_id = ""
    lines = outstring.split("\n")
    for line in lines:
        values = line.split(",")
        if len(values) != 2:
            print(
                "[STAGE BUILD][ERROR]: " +
                "Docker images returned unexpected format")
            return -1  # Should not happen, output line looks like name,id
        if values[0] == tempImageName:
            image_temp_id = values[1]
        if values[0] == const_ImageName:
            image_id = values[1]
    # Verify that the temp building step was sucessfull
    if image_temp_id == "":
        print(
            "[STAGE BUILD][ERROR]: " +
            "Temp contianer was not created")
        return -1
    print(
        "[STAGE BUILD][INFO]: " +
        "Temp container image built sucessfully, " +
        "check if container image exist...")

    # Check if non-temp image exisits
    if image_id != "":
        print(
            "[STAGE BUILD][INFO]: " +
            "Container image already existed, check if update needed...")
        # Non-temp image exisits
        # Check if id of temp and non-temp are matching
        if image_id == image_temp_id:
            # Ids match, builds equal, rm temp and nothing to do
            print(
                "[STAGE BUILD][INFO]: " +
                "Container image was up to date, removing temp...")
            subprocessout = subprocess.run(
                "sudo docker image rm " + tempImageName,
                shell=True, capture_output=True)
            outstring = subprocessout.stdout.decode().strip()
            if outstring.find(tempImageName) == -1:
                print(
                    "[STAGE BUILD][ERROR]: " +
                    "Error removing temp container img")
                return -1
            static_ImageGotUpdate = False
            print(
                "[STAGE BUILD][INFO]: " +
                "Done, Container image was up to date.")
            return 0
        else:
            # Ids dont match, old image needs to be removed
            print(
                "[STAGE BUILD][INFO]: " +
                "Container image got update, " +
                "stopping and removing old container and image...")
            # But first stop an evtl. running container
            subprocessout = subprocess.run(
                "sudo docker stop " + const_ContainerName,
                shell=True)
            # Remove the container (if it exists)
            subprocessout = subprocess.run(
                "sudo docker rm " + const_ContainerName,
                shell=True)
            # Now delete the image
            subprocessout = subprocess.run(
                "sudo docker image rm " + const_ImageName,
                shell=True, capture_output=True)
            outstring = subprocessout.stdout.decode().strip()
            if outstring.find(const_ImageName) == -1:
                print(
                    "[STAGE BUILD][ERROR]: " +
                    "Error removing old container image")
                return -1
    else:
        print(
            "[STAGE BUILD][INFO]: " +
            "Container image does not exsist.")

    # Re-Tag Temp-Img to non-tmp image
    print(
        "[STAGE BUILD][INFO]: " +
        "Renaming temp to non-temp image...")
    subprocessout = subprocess.run(
        "sudo docker image tag " + tempImageName + " " + const_ImageName,
        shell=True)
    # No output to check here...
    # Delete Temp image
    print(
        "[STAGE BUILD][INFO]: " +
        "Removing temp image...")
    subprocessout = subprocess.run(
        "sudo docker image rm " + tempImageName,
        shell=True, capture_output=True)
    outstring = subprocessout.stdout.decode().strip()
    if outstring.find(tempImageName) == -1:
        print(
            "[STAGE BUILD][ERROR]: " +
            "Error removing temp container image")
        return -1
    static_ImageGotUpdate = True
    print(
        "[STAGE BUILD][INFO]: " +
        "Done, container image (re)build sucessfull.")
    return 0


def delete():
    print(
        "[DELETE][INFO]: " +
        "Starting delete, stopping/removing container and image...")
    # First stop an evtl. running container
    subprocessout = subprocess.run(
        "sudo docker stop " + const_ContainerName,
        shell=True)
    # Remove the container (if it exists)
    subprocessout = subprocess.run(
        "sudo docker rm " + const_ContainerName,
        shell=True)
    # Now delete the image
    subprocessout = subprocess.run(
        "sudo docker image rm " + const_ImageName,
        shell=True, capture_output=True)
    outstring = subprocessout.stdout.decode().strip()
    if outstring.find(const_ImageName) == -1:
        print(
            "[DELETE][ERROR]: " +
            "Error removing container image")
        return -1
    print(
        "[DELETE][INFO]: " +
        "Done.")
    return 0


def reset():
    print(
        "[RESET][INFO]: " +
        "Reset, calling delete...")
    result = delete()
    if result != 0:
        return result
    print(
        "[RESET][INFO]: " +
        "Delete returned sucessfully, calling run...")
    # Now Call Run stage.
    result = run()
    if result != 0:
        return result
    return 0


# ### Program Execution ####
result = main()
if result != 0:
    print("Exit With Error", file=sys.stderr)
    exit(-1)
exit(0)
