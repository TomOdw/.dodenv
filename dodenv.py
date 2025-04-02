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

    # Evaluate Arguments
    argc = len(sys.argv)
    if argc == 2 or argc == 3:
        if argc == 3:
            # Other dockerfile used than default
            static_Dockerfile_extension = "." + sys.argv[2]
        match sys.argv[1]:
            case "run":
                return run()
            case "delete":
                return delete()
            case "reset":
                return reset()
            case _:
                return show_help()
    else:
        return show_help()


def show_help():
    print("TODO: show help")
    return -1


def run():
    print(
        "[STAGE RUN   ][INFO]: " +
        "Calling attach stage...")
    result = attach()
    if result != 0:
        return result
    print(
        "[STAGE RUN   ][INFO]: " +
        "Done, attach stage returned sucessfully.")
    return 0


def attach():
    print(
        "[STAGE ATTACH][INFO]: " +
        "Calling start stage...")
    result = start()
    if result != 0:
        return result
    print(
        "[STAGE ATTACH][INFO]: " +
        "Start stage returned sucessfully.")
    # Attach to running container
    print(
        "[STAGE ATTACH][INFO]: " +
        "Attaching to running container...")
    subprocessout = subprocess.run(
        "sudo docker exec -it -w /root/workspace " + const_ContainerName +
        " bash", shell=True)
    print(
        "[STAGE ATTACH][INFO]: " +
        "Done, returned from attached container.")
    return 0


def start():
    print(
        "[STAGE START ][INFO]: " +
        "Calling create stage...")
    result = create()
    if result != 0:
        return result
    print(
        "[STAGE START ][INFO]: " +
        "Create stage returned sucessfully.")

    # Start the container
    print(
        "[STAGE START ][INFO]: " +
        "Starting the container...")
    subprocessout = subprocess.run(
            "sudo docker start " + const_ContainerName,
            shell=True, capture_output=True)
    outstring = subprocessout.stdout.decode().strip()
    if outstring.find(const_ContainerName) == -1:
        print(
            "[STAGE START ][ERROR]: " +
            "Error while starting container")
        return -1
    print(
        "[STAGE START ][INFO]: " +
        "Done, container started sucessfully.")
    return 0


def create():
    # Run Build (Rebuild)
    print(
        "[STAGE CREATE][INFO]: " +
        "Calling build stage...")
    result = build()
    if result != 0:
        return result
    print(
        "[STAGE CREATE][INFO]: " +
        "Build stage returned sucessfully.")

    # Check if Container exisits
    print(
        "[STAGE CREATE][INFO]: " +
        "Checking if container exsist...")
    subprocessout = subprocess.run(
            "sudo docker ps -a --format \"{{.Names}}\"",
            shell=True, capture_output=True)
    outstring = subprocessout.stdout.decode().strip()
    if outstring != "":
        # Containers exsist
        lines = outstring.split("\n")
        for line in lines:
            if line.find(const_ContainerName) != -1:
                # Container Exsits
                if static_ImageGotUpdate is False:
                    # Image not update and container exist, nothing to do
                    print(
                        "[STAGE CREATE][INFO]: " +
                        "Done, container exsists with up to date image.")
                    return 0
                else:
                    # Image was updated, stop the container
                    print(
                        "[STAGE CREATE][INFO]: " +
                        "Container exsists, but image was updated, " +
                        "stopping container...")
                    subprocessout = subprocess.run(
                        "sudo docker stop " + const_ContainerName,
                        shell=True, capture_output=True)
                    outstring = subprocessout.stdout.decode().strip()
                    if outstring.find(const_ContainerName) == -1:
                        print(
                            "[STAGE CREATE][ERROR]: " +
                            "Error stopping container to remove")
                        return -1
                    # Delete the container
                    print(
                        "[STAGE CREATE][INFO]: " +
                        "Removing container")
                    subprocessout = subprocess.run(
                        "sudo docker rm " + const_ContainerName,
                        shell=True, capture_output=True)
                    outstring = subprocessout.stdout.decode().strip()
                    if outstring.find(const_ContainerName) == -1:
                        print(
                            "[STAGE CREATE][ERROR]: " +
                            "Error removing the old contianer")
                        return -1
    # Create the Container
    print(
        "[STAGE CREATE][INFO]: " +
        "Creating container from image...")
    this_files_path = os.path.abspath(__file__)
    project_path = os.path.abspath(os.path.join(this_files_path, "..", ".."))
    print(project_path)
    subprocessout = subprocess.run(
        "sudo docker create -it --name " + const_ContainerName +
        " -v /dev:/dev" +
        " -v " + project_path + ":/root/workspace " + const_ImageName,
        shell=True, capture_output=True)
    # This returns the full container id...
    outstring = subprocessout.stdout.decode().strip()
    if outstring == "":
        print(
            "[STAGE CREATE][ERROR]: " +
            "Error creating container")
        return -1
    else:
        print(
            "[STAGE CREATE][INFO]: " +
            "Done, container sucessfully (re)created.")
        return 0


def build():
    # Build the Dockerfile as temp
    tempImageName = const_ImageName + "_temp"
    print(
        "[STAGE BUILD ][INFO]: " +
        "Building temporary container image...")
    print(static_Dockerfile_extension)
    subprocessout = subprocess.run(
            "sudo docker build . -f " + const_ProjectPath +
            "/.dodenv/Dockerfile" + static_Dockerfile_extension +
            " -t " + tempImageName, shell=True)
    # Dont capture the output here, next step is verifying it...

    # Get Existing images, id from names:
    print(
        "[STAGE BUILD ][INFO]: " +
        "Check Existing container images...")
    subprocessout = subprocess.run(
        "sudo docker images --format \"{{.Repository}},{{.ID}}\"",
        shell=True, capture_output=True)
    outstring = subprocessout.stdout.decode().strip()
    if outstring == "":
        print(
            "[STAGE BUILD ][ERROR]: " +
            "Docker images returned empty string")
        return -1  # Should not happen, we built at least the temp...
    image_id = ""
    image_temp_id = ""
    lines = outstring.split("\n")
    for line in lines:
        values = line.split(",")
        if len(values) != 2:
            print(
                "[STAGE BUILD ][ERROR]: " +
                "Docker images returned unexpected format")
            return -1  # Should not happen, output line looks like name,id
        if values[0] == tempImageName:
            image_temp_id = values[1]
        if values[0] == const_ImageName:
            image_id = values[1]
    # Verify that the temp building step was sucessfull
    if image_temp_id == "":
        print(
            "[STAGE BUILD ][ERROR]: " +
            "Temp contianer was not created")
        return -1
    print(
        "[STAGE BUILD ][INFO]: " +
        "Temp container image built sucessfully, " +
        "check if container image exist...")

    # Check if non-temp image exisits
    if image_id != "":
        print(
            "[STAGE BUILD ][INFO]: " +
            "Container image already existed, check if update needed...")
        # Non-temp image exisits
        # Check if id of temp and non-temp are matching
        if image_id == image_temp_id:
            # Ids match, builds equal, rm temp and nothing to do
            print(
                "[STAGE BUILD ][INFO]: " +
                "Container image was up to date, removing temp...")
            subprocessout = subprocess.run(
                "sudo docker image rm " + tempImageName,
                shell=True, capture_output=True)
            outstring = subprocessout.stdout.decode().strip()
            if outstring.find(tempImageName) == -1:
                print(
                    "[STAGE BUILD ][ERROR]: " +
                    "Error removing temp container img")
                return -1
            static_ImageGotUpdate = False
            print(
                "[STAGE BUILD ][INFO]: " +
                "Done, Container image was up to date.")
            return 0
        else:
            # Ids dont match, old image needs to be removed
            print(
                "[STAGE BUILD ][INFO]: " +
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
                    "[STAGE BUILD ][ERROR]: " +
                    "Error removing old container image")
                return -1
    else:
        print(
            "[STAGE BUILD ][INFO]: " +
            "Container image does not exsist.")

    # Re-Tag Temp-Img to non-tmp image
    print(
        "[STAGE BUILD ][INFO]: " +
        "Renaming temp to non-temp image...")
    subprocessout = subprocess.run(
        "sudo docker image tag " + tempImageName + " " + const_ImageName,
        shell=True)
    # No output to check here...
    # Delete Temp image
    print(
        "[STAGE BUILD ][INFO]: " +
        "Removing temp image...")
    subprocessout = subprocess.run(
        "sudo docker image rm " + tempImageName,
        shell=True, capture_output=True)
    outstring = subprocessout.stdout.decode().strip()
    if outstring.find(tempImageName) == -1:
        print(
            "[STAGE BUILD ][ERROR]: " +
            "Error removing temp container image")
        return -1
    static_ImageGotUpdate = True
    print(
        "[STAGE BUILD ][INFO]: " +
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
