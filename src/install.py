import logging
import argparse
from .passwords import prompt_and_store_passwords
from .aliases import create_aliases
from .ssh_config import add_ssh_config_section
from .constants import RC_FILE, SSH_CONFIG_FILE
import os


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

    logging.info("\nSETUP COMPLETE!")
