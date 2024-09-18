# OPERATIONS ON THE SSH CONFIG FILE

import argparse
import logging
import re
import sys
from pathlib import Path

from .constants import (
    DEFAULT_LOG_FORMAT,
    LOGIN_HOST_ALIAS,
    LOGIN_SSH_HOST,
    SSH_CONFIG_FILE,
    SSH_CONTROLMASTERS_FOLDER,
    TOTP_BLOCK_END,
    TOTP_BLOCK_START,
)
from .passwords import get_ssh_user

# aliases useful for f-strings (left, right brace)
LBRACE = "{"
RBRACE = "}"

#  String templates for ssh files


def template_ssh_main_config(include_config_path):
    return f"""{TOTP_BLOCK_START}
# auto-generated by totp-app
# includes host definition used for totp app
# to remove, run "uninstall-totp-app"
Host *
    Include {str(include_config_path)}
{TOTP_BLOCK_END}

"""


def template_ssh_include_config(ssh_user):
    return f"""# SSH config file auto-generated by totp app
# this should be included the main ssh config file
# to uninstall, run "uninstall-totp-app"

Host {LOGIN_HOST_ALIAS}
    User {ssh_user}
    HostName {LOGIN_SSH_HOST}
    IdentitiesOnly yes
    ServerAliveInterval 60
    TCPKeepAlive no
    ControlMaster auto
    ControlPath {SSH_CONTROLMASTERS_FOLDER}/%r@%h:%p
    ControlPersist yes

"""


def check_custom_block_main_config(filetext: str, delete_and_return=False):
    """Return filetext with the custom entry removed"""
    pattern = rf"^{TOTP_BLOCK_START}\n(.+?\n){LBRACE}0,10{RBRACE}{TOTP_BLOCK_END}$(\n)*"
    m = re.search(pattern, filetext, re.MULTILINE)

    if not m:
        # string not detected in filetext
        return False

    if not delete_and_return:
        # string found, no need to do anything else
        return True

    # return the original filetext without the mached section
    # delete_and_return is True
    subbed_text = re.sub(pattern, "", filetext, flags=re.MULTILINE)
    return subbed_text


def check_host_already_defined(filetext):
    """Check if there is already the host_name defined in the main ssh config"""
    m = re.search(rf"^Host {LOGIN_HOST_ALIAS}", filetext, re.MULTILINE)
    return bool(m)


def add_ssh_config_section(config_file=SSH_CONFIG_FILE):
    config_file_full = Path(config_file).expanduser()

    with open(config_file_full, "rt") as f:
        main_config_text = f.read()

    is_host_defined = check_host_already_defined(filetext=main_config_text)
    if is_host_defined:
        logging.error(
            f"There already exists an entry in your ssh config file ({str(config_file)}) with the Host {LOGIN_HOST_ALIAS}."
        )
        logging.error("Exiting without making changes")
        sys.exit(1)

    is_section_defined = check_custom_block_main_config(filetext=main_config_text)
    if is_section_defined:
        logging.error(f"""TOTP section already in ssh config file
If this is an error, remove text from your config file including and between: {TOTP_BLOCK_START} ... {TOTP_BLOCK_END}
Exiting without making changes\n""")
        sys.exit(1)

    ssh_user = get_ssh_user()
    include_config_text = template_ssh_include_config(ssh_user=ssh_user)
    include_config_dir = Path(config_file_full.parent, "config.d")
    logging.info(
        f"Making ssh include config folder (if not exists): {str(include_config_dir)}"
    )
    include_config_dir.mkdir(exist_ok=True)
    include_config_path = Path(include_config_dir, "cannon-totp")
    include_config_path.write_text(data=include_config_text)
    logging.info(f"Writing TOTP config to file: {str(include_config_path)}")

    main_config_new_section = template_ssh_main_config(include_config_path)
    main_config_text_new = f"{main_config_text}{main_config_new_section}"

    config_file_full.write_text(main_config_text_new)
    logging.info(f"Saved ssh config file ({str(config_file)}) with TOTP section added")


def remove_ssh_config_section(config_file=SSH_CONFIG_FILE):
    config_file_full = Path(config_file).expanduser()
    include_config_dir = Path(config_file_full.parent, "config.d")
    include_config_path = Path(include_config_dir, "cannon-totp")

    main_text = config_file_full.read_text()

    logging.info(f"Removing TOTP config: {str(include_config_path)}")
    include_config_path.unlink(missing_ok=True)

    is_empty = not any(include_config_dir.iterdir())
    if is_empty:
        logging.info(f"Removing empty ssh config directory: {str(include_config_dir)}")
        include_config_path.rmdir()
    else:
        logging.warning(f"ssh config directory is not empty: {str(include_config_dir)}")

    new_text = check_custom_block_main_config(main_text, delete_and_return=True)
    if not new_text:
        logging.warning("Unable to locate section in ssh config. Continuing.")
        return

    config_file_full.write_text(new_text)
    logging.warning(
        f"Removed totp section and re-wrote to ssh config: {str(config_file_full)}"
    )


def make_controlmasters_folder(controlmasters_folder=SSH_CONTROLMASTERS_FOLDER):
    controlmasters_folder_full = Path(controlmasters_folder).expanduser()
    try:
        controlmasters_folder_full.mkdir()
        logging.warning(
            f"Created controlmasters folder at: {controlmasters_folder_full}"
        )
    except FileExistsError:
        logging.warning(
            f"Controlmasters folder already exists at: {controlmasters_folder_full}"
        )


if __name__ == "__main__":
    logging.basicConfig(format=DEFAULT_LOG_FORMAT, level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        help='action involving .ssh/config file (e.g "create" or "remove")',
    )
    args = parser.parse_args()
    action = args.action.lower()
    match action:
        case "create":
            try:
                add_ssh_config_section()
            except Exception as e:
                sys.exit(1)
        case "remove":
            try:
                remove_ssh_config_section()
            except Exception as e:
                sys.exit(1)
        case _:
            raise Exception(f"Action arg is not defined: {action}")
