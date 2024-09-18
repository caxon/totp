import argparse
import logging
import sys

from .aliases import remove_aliases
from .constants import (
    DEFAULT_LOG_FORMAT,
    RC_FILE,
    SSH_CONFIG_FILE,
    SSH_CONTROLMASTERS_FOLDER,
)
from .passwords import remove_passwords
from .ssh_config import remove_ssh_config_section


def cleanup_all():
    logging.warning(
        "This script will remove all setup steps of the TOTP app (assuming the user did not modify the installation)"
    )

    logging.warning(
        f"This includes removing: \n\t- ssh password, ssh username, and secret TOTP token from the MacOS keychain\n\t- aliases for start-ssh and stop-ssh set in {RC_FILE}\n\t- blocks in ~/.ssh/config set by this app"
    )
    user_input = input("Are you sure you would like to continue? (Y/N): ").lower()
    if user_input == "y" or user_input == "yes":
        pass
    else:
        logging.critical("\nDid not enter yes. Exiting.\n")
        sys.exit(1)

    logging.warning("Beginning removal")
    logging.warning("1. Removing Keychain passwords")

    remove_passwords()

    logging.warning(f"2. Removing aliases in {RC_FILE}")

    remove_aliases()

    logging.warning(f"3. Removing block in {SSH_CONFIG_FILE}")

    remove_ssh_config_section()

    logging.warning(
        f"You can optionally delete the ssh controlmasters folder at :{SSH_CONTROLMASTERS_FOLDER}"
    )
    logging.warning("Succesfully cleaned up TOTP app installation changes")
    logging.warning(
        "You can now deactive (if active) and remove the conda environment: conda deactivate && conda remove -n totp --all"
    )
    logging.warning(
        "Finally you can delete totp repository folder from your computer to complete removal"
    )


if __name__ == "__main__":
    logging.basicConfig(format=DEFAULT_LOG_FORMAT, level=logging.WARNING)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--target",
        help='remove a specific component set by the totp app e.g. "all" [DEFAULT], "password", "alias", or "ssh"',
        default="all",
    )
    args = parser.parse_args()

    match args.target:
        case "all":
            cleanup_all()
        case "password":
            logging.info("Removing saved passwords for totp app")
            remove_passwords()
        case "ssh":
            logging.info("Removing ssh config sections created for totp app")
            remove_ssh_config_section()
        case "alias":
            logging.info("Removing aliases created for totp app")
            remove_aliases()
