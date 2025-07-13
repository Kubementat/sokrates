# README.md update workflow

## General guidelines
Please add comprehensive documentation for to the README.md file.
Ensure that the documentation is easily accessible to other developers and is updated as the repository evolves.

## Updating information
Only update contents of the README.md file that do not contain up to date information. __DO NOT__ change entries if they are correct in terms of the meaning. __DO NOT__ change formulation for the correct entries.

## Setup Instructions
Add proper setup instructions including console commands to execute for setting up the repo in the github standard format.

## List of commands generation
Step 1. - Generate a list of all files in the complete project ending with '.py', '.sh' or '.html'
Step 2. - Iterate over the list of filenames

For each file:
Step 2.1 - Read the first 100 lines of the file
Step 2.2 - Extract the script's main purpose and remember it

Step 3. - Update the README.md file with the current list of scripts available within the repository in the following format.

# Script List Format
```
## <Script Name A>
<Description of the script A>
### Usage
- <Execution example 1 of script A>
- <Execution example 2 of script A>

## <Script Name B>
<Description of the script B>
### Usage
- <Execution example 1 of script B>
- <Execution example 2 of script B>

... (and so on)
```

## Examples
```
## `find_duplicates.py`
Finds duplicate files for a given directory and it's sub-directory. Optional: Cleanup duplicates.
### Usage
- `find_duplicates.py --directory $HOME/mydir/`
- `find_duplicates.py --directory $HOME/mydir/ --remove --verbose`

## `continue_switch_env.sh`
Switches the environment (configuration) used by the continue.dev VSCode plugin.
### Usage
- `continue_switch_env.sh local`
- `continue_switch_env.sh evobox`
```

## Script Usage examples
Provide up to 2 example calls that can be executed in the shell for each of the scripts in the project's root directory.

# Task
Execute the workflow described above and update the README.md file as needed.