import logging
import os
from pathlib import Path
import argparse
import sys

from src.aliases import create_aliases, make_rc_file
from src.constants import (
    RC_FILE,
    SSH_CONFIG_FILE,
    SSH_CONTROLMASTERS_FOLDER,
    SSH_FOLDER,
)
from src.passwords import prompt_and_store_passwords, are_all_passwords_set
from src.ssh_config import (
    add_ssh_config_section,
    make_controlmasters_folder,
    make_ssh_config_file,
    make_ssh_folder,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="enable verbose logging (for debugging)",
    )
    args = parser.parse_args()
    verbose = args.verbose

    if verbose:
        logging.basicConfig(
            format="[%(levelname)s][%(asctime)s] %(message)s", level=logging.DEBUG
        )
    else:
        logging.basicConfig(format="%(message)s", level=logging.INFO)

    base_repo_dir = os.getcwd()

    logging.warning(
        "This script will ask you if you want to change various settings on your system to make it easier to run the TOTP app.\n"
    )
    logging.warning(
        "If you aren't sure what the a question means, you should probably enter Y and allow the install script to make each change.\n"
    )

    ## Check if important files exist

    rc_file_exists = Path(RC_FILE).expanduser().exists()
    ssh_folder_exists = Path(SSH_FOLDER).expanduser().is_dir()
    ssh_config_file_exists = Path(SSH_CONFIG_FILE).expanduser().exists()
    controlmasters_folder_exists = Path(SSH_CONTROLMASTERS_FOLDER).expanduser().is_dir()
    all_passwords_set = are_all_passwords_set()

    ## Check if SSH folder exists (~/.ssh)
    ## MANDATORY
    if not ssh_folder_exists:
        logging.warning(
            "---\n"
            + f"SSH folder does not exist ({SSH_FOLDER}).\n"
            + "This is mandatory to setup the TOTP app.\n"
            + 'If you are using a non-standard ssh folder, you can update SSH_FOLDER in "$TOTP/src/constants.py"'
        )
        user_input = input("Would you like to set up the ssh folder? (Y/N): ").lower()
        if user_input == "y" or user_input == "yes":
            ssh_folder_exists = make_ssh_folder()
        else:
            logging.error(
                'Did not input "yes". SSH folder required to continue setup. Exiting.'
            )
            sys.exit(1)
    else:
        logging.debug("SSH folder already exists.")

    ## Check if ssh config file exists (~/.ssh/config)
    ## MANDATORY
    if not ssh_config_file_exists:
        logging.warning(
            "---\n"
            + f"SSH config file does not exist ({SSH_CONFIG_FILE}).\n"
            + "This is mandatory to setup the TOTP app.\n"
            + 'If you are using a non-standard ssh config file, you can update SSH_CONFIG_FILE in "$TOTP/src/constants.py".'
        )
        user_input = input(
            "Would you like to create the ssh config file? (Y/N): "
        ).lower()
        if user_input == "y" or user_input == "yes":
            ssh_config_file_exists = make_ssh_config_file()
        else:
            logging.warning(
                'Did not input "yes". SSH config file required to continue setup. Exiting.'
            )
            sys.exit(1)
    else:
        logging.debug("SSH config file already exists.")

    ## check if ssh controlmasters folder exists (~/.ssh/controlmasters)
    ## MANDATORY
    if not controlmasters_folder_exists:
        logging.warning(
            "---\n"
            + f"SSH controlmasters folder does not exist ({SSH_CONTROLMASTERS_FOLDER}).\n"
            + "This is required to setup the TOTP app.\n"
            + 'If you are using a non-standard controlmasters folder, you can update SSH_CONTROLMASTERS_FOLDER in "$TOTP/src/constants.py".'
        )
        user_input = input(
            "Would you like to create the controlmasters folder? (Y/N): "
        ).lower()
        if user_input == "y" or user_input == "yes":
            controlmasters_folder_exists = make_controlmasters_folder()
        else:
            logging.error(
                'Did not input "yes". Controlmastesr folder required to continue setup. Exiting'
            )
            sys.exit(1)
    else:
        logging.debug("SSH controlmasters folder already exists.")

    ## Check if shell config file exists (~/.zshrc)
    ## MANDATORY FOR ALIASES
    if not rc_file_exists:
        logging.warning(
            "---\n"
            + f"Shell config file ({RC_FILE}) does not exist.\n"
            + "If you use a different shell .rc file, update constant RC_FILE in file $TOTP/src/constants.py.\n"
            + "This is optional, but required if you want to set aliases (recommended)."
        )
        user_input = input("Would you like create a shell config file? (Y/N): ").lower()
        if user_input == "y" or user_input == "yes":
            rc_file_exists = make_rc_file()
        else:
            logging.error(
                'Did not input "yes". Shell config file (.rc file) required to set up aliases.'
            )
    else:
        logging.debug(".rc file already exists.")

    ## set up passwords
    ## MANDATORY
    if all_passwords_set:
        logging.warning("---\n" + "Passwords already appear to be set.")
        user_input = input("Would you like to update them? (Y/N): ").lower()
    else:
        logging.warning("---\n" + "Passwords do not appear to be set.")
        user_input = input(
            "Would you like to initialize your passwords? (Y/N): "
        ).lower()
    if user_input == "y" or user_input == "yes":
        all_passwords_set = prompt_and_store_passwords()
    if not all_passwords_set:
        logging.error(
            "Passwords were not set correctly. They must be set before using TOTP app. Exiting."
        )
        sys.exit(1)

    ## set up aliases
    ## OPTIONAL (not possible if shell config file is not set)
    if not rc_file_exists:
        logging.warning(
            "---\n"
            + "Shell config file (.rc file) must exist to configure shell aliases. Skipping alias setup."
        )
    else:
        logging.warning("---\n")
        user_input = input(
            f"Would you like to set aliases in the shell config file ({RC_FILE})? (Y/N): "
        ).lower()
        if user_input == "y" or user_input == "yes":
            create_aliases(totp_project_dir=base_repo_dir)
        else:
            logging.warning('Did not input "yes". Skipping alias setup')

    ## set up ssh section
    ## OPTIONAL
    logging.warning("---\n")
    user_input = input(
        f"Would you like to set up the ssh config file {SSH_CONFIG_FILE}? (Y/N): "
    ).lower()
    if user_input == "y" or user_input == "yes":
        add_ssh_config_section()
    else:
        logging.warning(
            'Did not input "yes". You must manually set up ssh config section for TOTP app scripts to work.'
        )

    ## All done :)

    logging.info(
        f"\nSETUP COMPLETE! To use commands (e.g. start-ssh), open a new shell or run: `source {RC_FILE}`"
    )
