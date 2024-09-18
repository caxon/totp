import logging
import os
from pathlib import Path

from .aliases import create_aliases
from .constants import RC_FILE, SSH_CONFIG_FILE, SSH_CONTROLMASTERS_FOLDER
from .passwords import prompt_and_store_passwords
from .ssh_config import add_ssh_config_section, make_controlmasters_folder

if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    base_repo_dir = os.getcwd()

    # set up passwords
    user_input = input("\nWould you like to initialize your passwords? (Y/N): ").lower()
    if user_input == "y" or user_input == "yes":
        prompt_and_store_passwords()
    else:
        logging.warning('Did not input "yes". Skipping password initialization')

    # set up aliases
    user_input = input(f"\nWould you like to set aliases in {RC_FILE}? (Y/N): ").lower()
    if user_input == "y" or user_input == "yes":
        create_aliases(totp_project_dir=base_repo_dir)
    else:
        logging.warning('Did not input "yes". Skipping alias setup')

    # set up ssh config
    user_input = input(
        f"\nWould you like to set up the ssh config file {SSH_CONFIG_FILE}: "
    ).lower()
    if user_input == "y" or user_input == "yes":
        add_ssh_config_section()
    else:
        logging.warning('Did not input "yes". Skipping ssh config file setup')

    # set up controlmasters folder if necessary
    if not Path(SSH_CONTROLMASTERS_FOLDER).expanduser().is_dir():
        user_input = input(
            f"\nIt looks like the contorlmasters folder does not exist at {SSH_CONTROLMASTERS_FOLDER}. Would you like to create it? "
        ).lower()
        if user_input == "y" or user_input == "yes":
            make_controlmasters_folder()
        else:
            logging.warning(
                'Did not input "yes". Skipping controlmasters folder creation'
            )

    logging.info(
        f"\nSETUP COMPLETE! To use commands (e.g. start-ssh), open a new shell or run: `source {RC_FILE}`"
    )
