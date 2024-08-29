# TOTP SSH Automation

Objective: Automatically connect to ssh servers which require 2FA for each connection.

>[!WARNING] This is only tested on MacOS. It may work on Linux but will require some tinkering.

# Setup Steps (MacOS)

1. Clone this repo

    ```bash
    git clone https://github.com/caxon/totp.git
    ```

2. cd into the directory you just cloned: 

    ```bash
    cd totp
    ```

3. Install `conda` or simlar. Many tutorials online e.g. [installing miniforge](https://github.com/conda-forge/miniforge?tab=readme-ov-file#unix-like-platforms-mac-os--linux)

4. Create a conda environment:

    ```bash
    conda env create -f environment.yml
    ```
5. Activate the environemnt 
    ```
    conda activate totp
    ```
6. Obtain your FASRC username, FASRC password, and FASRC TOTP token. [Link to tutorial](./docs/OBTAIN_FASRC_TOKEN.md).

> [!NOTE] This is not the same as the Harvard-wide 2FA system, and is specific to FASRC.

7. Run the installation script and following the instructions. I recommend setting up passwords, aliases, and ssh config.

    ```bash
    ./scripts/install
    ```

8. Test the ssh connection
   ```bash
   start-ssh
   ```

> [!NOTE] MacOS may ask you if you want to let python access the keychain. You can click "allow always" to ignore this prompt in the future. Just note this will allow any python app to access the specific secrets you have authorized.


# Running Steps

Once setup is done, you should have the following commands as aliases: `start-ssh`, `stop-ssh`, and `uninstall-totp-app`

Run `start-ssh` from any terminal to create a connection. You will not have to manually enter your 2FA code or password. As long as this connection is open (even if the terminal is closed), any ssh command that uses your ssh config file will use the shared connection without re-authentication. 
E.g. `ssh`, `rsync`, `scp`, etc.

## Usage Notes

* To close the shared ssh conncetion run the command, run `stop-ssh`.
* The shared connection may time-out if your computer is disconnected for too long. To re-connect, just run `start-ssh` again.
* By default `start-ssh` returns nothing if it is successful. To show more logs, enable the verbose argument: `start-ssh -v`
* This will only work for the main login node by default (e.g. ssh user@login.rc.fas.harvard.edu) - if you want to log onto a specific node e.g. `boslogin` or `holylogin02` you will need to enter your password & 2FA token 

## Advanced Configuration

* Most constants in the app are stored in `./src/constants.py`
* You can uninstall the app, modify constants here, and re-run the install script
* If you need to change your password or 2FA token, you can reset passwords without uninstalling the other components: from this repo's base directory run: `python -m src.cleanup_all -t password`. To set the passwords again, re-run `./scripts/install` and just enter "Yes" for the option to set passwords.

# Uninstallation

1. Run the following command to remove passwords, aliases, and ssh config sections set by this app

    ```bash
    ./scripts/install
    ```

2. Remove the conad environment:

    If the `totp` environmetn is currently asctive, run:

    ```bash
    conda deactivate
    ```

    Then you can remove the environment with:
    ```bash
    conda remove -n totp --all
    ```

3. Finally, you can delete the `totp` folder