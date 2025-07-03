# README.md update workflow

## General guidelines
Please add comprehensive documentation for to the README.md file.
Ensure that the documentation is easily accessible to other developers and is updated as the repository evolves.
ALWAYS CHECK THE EXSTING README.md file and only adjust missing information or update existing outdated information.

## Setup Instructions
Add proper setup instructions including console commands to execute for setting up the repo in the github standard format.

## Workflow
Scan the repository for all files with a .py extension and collect all features, classes and functions.
Write a short one sentence documentation for each class and each function.

Also read the pyproject.toml file and iterate over the list of available commands under the heading [project.scripts]:
Each definition begins with a command name followed by an empty char and then a = character
Only extract the command names and describe the according command functionality from the context of the project.

# Task
Execute the workflow described above and update the README.md file as needed.