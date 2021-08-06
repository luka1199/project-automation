#!/usr/bin/python
from github import Github
import yaml
import os
from getpass import getpass
from shutil import copyfile
import webbrowser


class ProjectAutomation:
    def __init__(self):
        self.reset()
        self.loadConfig()

    def reset(self):
        """Reset all attributes
        """
        self.state = 0
        self.config = None
        self.user = None
        self.username = ""
        self.project_name = ""
        self.project_description = ""
        self.project_private = True
        self.project_path = ""
        self.project_parent = ""
        self.confirmed = False

    def runLoop(self):
        while (True):
            # Load GitHub user
            if self.state == 0:
                self.loadUser()
                if self.state == 0: self.state += 1

            # Set project name
            elif self.state == 1:
                self.project_name = input("Project name: ")
                if self.state == 1: self.state += 1

            # Set project description
            elif self.state == 2:
                self.project_description = input("Project description: ")
                if self.state == 2: self.state += 1

            # Set project privacy
            elif self.state == 3:
                self.setPrivacy()
                if self.state == 3: self.state += 1

            # Set parent path and project path
            elif self.state == 4:
                self.setPaths()
                if self.state == 4: self.state += 1

            # Confirm the project creation
            elif self.state == 5:
                self.setConfirmation()
                if self.state == 5: self.state += 1

            # Create the project
            elif self.state == 6:
                self.createProject()
                if self.state == 6: self.state += 1
            
            else:
                break
            print()

    def loadUser(self):
        """Loads GitHub user specified in config.yaml or with user inputs.
        """
        use_token = True
        token = ""
        password = ""

        # No credentials block in config.yaml
        if "credentials" not in self.config.keys():
            print("No credentials set in config.yaml")
            self.username = input("Username: ")

            # User input to set credentials
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
        
        # Credentials block in config.yaml
        else:
            # No username in config.yaml
            if "username" not in self.config["credentials"].keys() \
                    or self.config["credentials"]["username"] == "":
                print("No username config.yaml")
                self.username = input("Username: ")

            # Username in config.yaml
            else:
                self.username = self.config["credentials"]["username"]

            # Access token in config.yaml
            if "access_token" in self.config["credentials"].keys() \
                    and self.config["credentials"]["access_token"] != "":
                token = self.config["credentials"]["access_token"]

            # No Access token in config.yaml
            else:
                # Password in config.yaml
                if "password" in self.config["credentials"].keys() \
                        and self.config["credentials"]["password"] != "":
                    password = self.config["credentials"]["password"]
                    use_token = False

                # No password in config.yaml 
                else:
                    print("No access token or password set in config.yaml")

                    # User input to set credentials
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
            self.user = self.getAccountWithToken(token).get_user()
        else:
            self.user = self.getAccount(self.username, password).get_user()
        
    def setPrivacy(self):
        """Sets the project privacy with user inputs.
        """
        while(True):
            project_private_input = input(
                "Project private (Default: yes)? (y or n): ")
            if project_private_input == "" or project_private_input.lower() == "y":
                break
            elif project_private_input.lower() == "n":
                self.project_private = False
                break
            else:
                print("Invalid input")

    def setPaths(self):
        """Sets the project path and parent path with user inputs.
        """
        while(True):
            # No paths in config
            if "paths" not in self.config.keys():
                self.project_parent = input("Project path: ")

            # Paths in config
            else:
                paths = self.config["paths"]
                names_dict = dict(enumerate(paths.keys()))
                paths_dict = dict(enumerate(paths.values()))
                while(True):
                    j = 0
                    for i in names_dict.keys():
                        print("{}: {} (\"{}\")".format(
                            i+1, names_dict[i], paths_dict[i]))
                        j = i + 2
                    print("{}: Custom path".format(j))
                    path_input = input("Chose a path: ")
                    if path_input == str(j):
                        self.project_parent = input("Project path: ")
                        if self.project_parent == ".":
                            self.project_parent = os.getcwd()
                        break
                    elif path_input.isdigit() and int(path_input) - 1 in dict(names_dict).keys():
                        self.project_parent = dict(paths_dict)[int(path_input) - 1]
                        break

            # Project does not exist yet
            if not os.path.isdir(os.path.join(self.project_parent, self.project_name)):
                print("Project path set to \"{}\"".format(
                    os.path.join(self.project_parent, self.project_name)))
                break

            # Project already exists
            else:
                print("\"{}\" already exists in \"{}\"".format(
                    self.project_name, self.project_parent))
                self.reset()
                break

        self.project_path = os.path.join(self.project_parent, self.project_name)


    def setConfirmation(self):
        """Confirms project creation with user inputs.
        """
        while(True):
            confirm_input = input(
                "Create project \"{}\"? (y or n): ".format(self.project_name))
            if confirm_input == "" or confirm_input.lower() == "y":
                self.confirmed = True
                break
            elif confirm_input.lower() == "n":
                break
            else:
                print("Invalid input")

        if not self.confirmed:
            quit()

    def createProject(self):
        """Creates a GitHub repository, the local project folder, the .gitignore file,
        the README.md and does the first commit.
        """
        print("Creating project \"{}\"...".format(self.project_name)) 
        if not self.createRepo(self.user, self.project_name, self.project_description, self.project_private):
            self.reset()
        else:
            os.system("mkdir {}".format(self.project_path))
            f = open(os.path.join(self.project_path, ".gitignore"), "a").close()
            f = open(os.path.join(self.project_path, "README.md"), "a")
            f.write("# {}\n{}".format(self.project_name, self.project_description))
            f.close()
            os.system("sh {}/create_repo.sh '{}' '{}' '{}'".format(os.path.dirname(
                os.path.realpath(__file__)), self.project_name, self.project_path, self.username))
        webbrowser.open("https://github.com/{}/{}".format(self.username, self.project_name))


    def loadConfig(self):
        """Loads the config.yaml file and saves the config.
        """
        pwd = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(pwd, 'config.yaml')
        config_default_path = os.path.join(pwd, 'config_default.yaml')
        if not os.path.isfile(config_path):
            print("Creating config.yaml...")
            if os.path.isfile(config_default_path):
                copyfile(config_default_path, config_path)
            else:
                f = open("config.yaml", "a").close()

        self.config = yaml.safe_load(open(config_path))
        if self.config is None:
            self.config = {}


    def getAccount(self, username, password):
        """Loads and saves a GitHub Account
        
        Arguments:
            username {str} -- The username of the GitHub account.
            password {str} -- The password of the GitHub account
        """
        return Github(username, password)


    def getAccountWithToken(self, token):
        """Loads and saves a GitHub Account
        
        Arguments:
            token {str} -- The access token of the GitHub account.
        """
        return Github(token)


    def getRepos(self, account):
        """Returns a list of all repository names of the specified GitHub user.
        
        Arguments:
            account {GitHub Object} -- A GitHub user account.
        
        Returns:
            list -- A list of repository names.
        """
        return [repo.name for repo in self.user.get_repos()]


    def createRepo(self, account, name, description="", private=True):
        """Creates a GitHub repository for the specified GitHub user.
        
        Arguments:
            account {GitHub Object} -- A GitHub user account.
            name {str} -- The desired repository name.
        
        Keyword Arguments:
            description {str} -- The desired repository description. (default: {""})
            private {bool} -- The desired repository privacy setting. (default: {True})
        
        Returns:
            bool -- Success of the repository creation.
        """
        repos = self.getRepos(account)
        if name in repos:
            print("This repository already exists")
            return False
        else:
            self.user.create_repo(name, description=description, private=private)
            return True
    

if __name__ == "__main__":
    project_automation = ProjectAutomation()
    project_automation.runLoop()
