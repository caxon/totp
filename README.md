# TOTP SSH Automation

**Warning: This is only tested on MacOS. It may work on Linux with the appropriate keychain alternative installed. It may work on Windows but it will require some tinkering.**

# One-time setup steps

1. Clone this repo (e.g. to `~/opt/totp`)
I recommend putting it in `~/opt/totp`, but you can put it anywere that you put source files or projects:  
 a. Create ~/opt directory if it does not exist: `mkdir -p ~/opt`  
 b. Go to ~/opt directory: `cd ~/opt`  
 c. Clone the repo: `git clone git@github.com:caxon/totp.git` [SSH: preferred] or `https://github.com/caxon/totp.git` [HTTP: less github setup required]  

2. cd into the directory you just cloned: `cd totp`
3. Install `conda` or `mamba` if not already installed (find instructions online e.g. [installing miniconda](https://docs.anaconda.com/free/miniconda/)). If you use mamba (preferred), alias or replace all conda commands with mamba.
4. Create a conda environment:
    ```
    conda env create -f environment.yml
    ```
5. Activate the environemnt `conda activate totp`
6. Obtain your FASRC username, FASRC password, and FASRC TOTP token. Note: this is **not the same as the harvard-wide duo 2FA system!** See tutorial [here](./tutorial/OBTAIN_FASRC_TOKEN.md).
7. Run the python script for the first time and it will prompt you to enter your information: `./scripts/start-ssh`


## Running Steps: 
1. Activate environemnt: `conda activate totp`
2. run the python script: `python -m gen-totp`


## [ADVANCED] Alernative Running Steps
Why: Add the `start-ssh` script to your path so you can run it from anywhere
1. make a `~/bin` folder: `mkdir -p ~/bin`
2. add the bin folder to your shell's path. This varries depending on your shell (e.g. zsh vs bash). E.g. for zsh, open the zshrc file (`vi ~/.zshrc`). And add the following line near the top: 
    ```bash
    export PATH=/home/YOUR_USERNAME_HERE/bin:$PATH 
    ```
3. Restart your shell (or `source ~/.zhsrc` to update for the current shell)
4. Now you can call `start-ssh` from anywhere. If it is successfull there will be no cli output, but you should not need a password to ssh to cannon.



## Other notes:
- This will only work for the default login node by default (e.g. ssh user@login.rc.fas.harvard.edu) - if you want to log onto a specific node e.g. `boslogin` or `holylogin02` you will need to edit your ssh config or some files in this code [not officially supported] 
- If you have to change your password, totp code, or login info, follow the section below for "Removing passwords set by this app", then run `start-ssh` again and it will re-prompt you for this information.
- The ssh connection will occasionally timeout. You just need to run `start-ssh` again to fix.

# Uninstallation

## Removing passwords set by this app
1. cd to the repo directory (totp)
2. `conda activate totp`
3. `python -m src.remove_passwords`
If you run this multiple times, you will get errors, because the passwords have already been deleted.


## Deleting the totp conda environment
1. If the totp environment is currently active, run `conda deactivate`
2. Run the following command: `conda remove -n totp --all` and enter `y` to confirm.

You will need to re-install the conda environment (see "One-Time Setup  Steps" section above for these instructions).


