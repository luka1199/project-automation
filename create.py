#!/usr/bin/python
from github import Github
import yaml
import os
from getpass import getpass
from shutil import copyfile


# Loads the config.yaml file and returns the config
def getConfig():
    pwd = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(pwd, 'config.yaml')
    config_default_path = os.path.join(pwd, 'config_default.yaml')
    if not os.path.isfile(config_path):
        print("Creating config.yaml...")
        if os.path.isfile(config_default_path):
            copyfile(config_default_path, config_path)
        else:
            f = open("config.yaml", "a").close()

    config = yaml.safe_load(open(config_path))
    return config


# Returns a GitHub object
def getAccount(username, password):
    return Github(username, password)


# Returns a GitHub object
def getAccountWithToken(token):
    return Github(token)


# Returns list of all repository names
def getRepos(user):
    return [repo.name for repo in user.get_repos()]


def createRepo(user, name, description="", private=True):
    repos = getRepos(user)
    if name in repos:
        print("This repository already exists")
        return False
    else:
        user.create_repo(name, description=description, private=private)
        return True


if __name__ == "__main__":
    state = 0
    config = None
    user = None
    username = ""
    project_name = ""
    project_description = ""
    project_private = True
    project_path = ""
    project_parent = ""

    while(True):
        # user
        if state == 0:
            use_token = True
            token = ""
            password = ""
            config = getConfig()
            if config is None:
                config = {}
            if "credentials" not in config.keys():
                print("No credentials set in config.yaml")
                username = input("Username: ")

                while(True):
                    credentials_input = input(
                        "Use token (Default: yes)? (y or n): ")
                    if credentials_input == "" or credentials_input.lower() == "y":
                        break
                    elif credentials_input.lower() == "n":
                        use_token = False
                        break
                    else:
                        print("Invalid input")
                
                if use_token:
                    token = input("Access token: ")
                else:
                    password = input("Password: ")

            else:
                if "username" not in config["credentials"].keys() \
                        or config["credentials"]["username"] == "":
                    print("No username config.yaml")
                    username = input("Username: ")
                else:
                    username = config["credentials"]["username"]

                if "access_token" in config["credentials"].keys() \
                        and config["credentials"]["access_token"] != "":
                    token = config["credentials"]["access_token"]
                else:
                    if "password" in config["credentials"].keys() \
                            and config["credentials"]["password"] != "":
                        password = config["credentials"]["password"]
                        use_token = False
                    else:
                        print("No access token or password set in config.yaml")
                        while(True):
                            credentials_input = input(
                                "Use token (Default: yes)? (y or n): ")
                            if credentials_input == "" or credentials_input.lower() == "y":
                                break
                            elif credentials_input.lower() == "n":
                                use_token = False
                                break
                            else:
                                print("Invalid input")

                        if use_token:
                            token = input("Access token: ")
                        else:
                            password = input("Password: ")

            if use_token:
                user = getAccountWithToken(token).get_user()
            else:
                user = getAccount(username, password).get_user()
            if state == 0: state += 1

        # project_name
        elif state == 1:
            project_name = input("Project name: ")
            if state == 1: state += 1

        # project_description
        elif state == 2:
            project_description = input("Project description: ")
            if state == 2: state += 1
        
        # project_private
        elif state == 3:
            project_private = True
            while(True):
                project_private_input = input(
                    "Project private (Default: yes)? (y or n): ")
                if project_private_input == "" or project_private_input.lower() == "y":
                    break
                elif project_private_input.lower() == "n":
                    project_private = False
                    break
                else:
                    print("Invalid input")
            if state == 3: state += 1
        
        # project_path and project_parent
        elif state == 4:
            while(True):
                if "paths" not in config.keys():
                    project_parent = input("Project path: ")
                else:
                    paths = config["paths"]
                    names_dict = dict(enumerate(paths.keys()))
                    paths_dict = dict(enumerate(paths.values()))
                    while(True):
                        for i in names_dict.keys():
                            print("{}: {} (\"{}\")".format(
                                i+1, names_dict[i], paths_dict[i]))
                        print("ENTER: Custom path")
                        path_input = input("Chose a path: (eg. 1 2 3): ")
                        if path_input == "":
                            project_parent = input("Project path: ")
                            if project_parent == ".":
                                project_parent = os.getcwd()
                            break
                        elif path_input.isdigit() and int(path_input) - 1 in dict(names_dict).keys():
                            project_parent = dict(paths_dict)[int(path_input) - 1]
                            break
                if not os.path.isdir(os.path.join(project_parent, project_name)):
                    print("Project path set to \"{}\"".format(
                        os.path.join(project_parent, project_name)))
                    break
                else:
                    print("\"{}\" already exists in \"{}\"".format(
                        project_name, project_parent))
                    state = 0
                    break
            project_path = os.path.join(project_parent, project_name)
            if state == 4: state += 1
        
        # project_private
        elif state == 5:
            confirm = False
            while(True):
                confirm_input = input(
                    "Create project \"{}\"? (y or n): ".format(project_name))
                if confirm_input == "" or confirm_input.lower() == "y":
                    confirm = True
                    break
                elif project_private_input.lower() == "n":
                    break
                else:
                    print("Invalid input")

            if not confirm:
                quit()
            if state == 5: state += 1

        
        elif state == 6:
            if not createRepo(user, project_name, project_description, project_private):
                state = 0
            else:
                os.system("mkdir {}".format(project_path))
                f = open(os.path.join(project_path, ".gitignore"), "a").close()
                f = open(os.path.join(project_path, "README.md"), "a")
                f.write("# {}\n{}".format(project_name, project_description))
                f.close()
                os.system("{}/create_repo.sh '{}' '{}' '{}'".format(os.path.dirname(
                    os.path.realpath(__file__)), project_name, project_path, username))

                if state == 6:
                    state += 1

        else:
            break
