import getpass
import sys

import keyring
import pexpect
import pyotp

import logging

from .constants import (
    FASRC_LOGIN_SSH_HOST,
    PASSWORD_SERVICE_NAME,
    SECRET_TOKEN_SERVICE_NAME,
    SSH_USER_SERVICE_NAME,
)
from .test_connection import is_controlmaster_open

from .set_passwords import prompt_and_store_passwords

#optionally configure logging level

LOG_LEVEL=logging.WARNING


# set up logigng (default is warn or higher)
logging.basicConfig(format="%(levelname)s:%(message)s", level=LOG_LEVEL)


def get_secrets():
    SECRET_totp_code = keyring.get_password(SECRET_TOKEN_SERVICE_NAME, username)
    SECRET_rc_password = keyring.get_password(PASSWORD_SERVICE_NAME, username)
    SECRET_ssh_user = keyring.get_password(SSH_USER_SERVICE_NAME, username)
    return {
        "totp_code": SECRET_totp_code,
        "rc_password": SECRET_rc_password,
        "ssh_user": SECRET_ssh_user,
    }


# local machine username
username = getpass.getuser()

# get passwords from MacOS Keychain
pass_dict = get_secrets()

SECRET_totp_code = pass_dict["totp_code"]
SECRET_rc_password = pass_dict["rc_password"]
SECRET_ssh_user = pass_dict["ssh_user"]

if SECRET_totp_code is None or SECRET_rc_password is None or SECRET_ssh_user is None:
    logging.warning("At least one password is missing from keyring")
    user_input = input("Would you like to initialize your passwords? (Y/N): ").lower()
    if user_input == "y" or user_input == "yes":
        prompt_and_store_passwords()

        # get passwords from MacOS Keychain
        pass_dict = get_secrets()

        SECRET_totp_code = pass_dict["totp_code"]
        SECRET_rc_password = pass_dict["rc_password"]
        SECRET_ssh_user = pass_dict["ssh_user"]

    else:
        logging.critical("\nDid not enter yes. Exiting.\n")
        sys.exit(1)


ssh_dest = f"{SECRET_ssh_user}@{FASRC_LOGIN_SSH_HOST}"

# test if controlmaster is alrady running

running = is_controlmaster_open(ssh_dest=ssh_dest)
if running:
    logging.info("SSH Tunnel already exists. Doing nothing")
    sys.exit(0)
else:
    logging.info("SSH Tunnel does not exist. Opening ssh tunnel:")


ssh_config_dict = {
    "TCPKeepAlive": "no",  # Use ServerKeepAlive instead
    "ServerAliveInterval": "30",  # prevent dropped connections
    "IdentitiesOnly": "yes",  # Don't attempt key-based ssh auth (disabled by FASRC)
    "ControlMaster": "yes",  # Use single control socket for SSH
    "ControlPath": "~/.ssh/controlmasters/%r@%h:%p",  # Path to ssh control sockets
    "ControlPersist": "yes",  # Keep master connection open in the background
    "StrictHostKeyChecking": "accept-new",  # accept new ssh host, but DO NOT ACCEPT existing hosts where key has changed
}

ssh_positional_options = [
    "-F",
    "none",  # Do not read from SSH config file (config_file = None)
    "-X",  # enable X11 forwarding (if you want to run graphical applicaitons over tunnel connection)
    "-N",  # do not execute remote commands (just open tunnel)
    # '-C', # not sure if compression helps - since file is encrypted and connection is likely very fast
]
ssh_config_options_as_list = []
for key in ssh_config_dict:
    val = ssh_config_dict[key]
    ssh_config_options_as_list.append("-o")
    ssh_config_options_as_list.append(f"{key}={val}")

subprocess_options = [*ssh_positional_options, *ssh_config_options_as_list, ssh_dest]

# generated 6-digit one-time authentication token
SECRET_totp_token = pyotp.TOTP(SECRET_totp_code).now()

logging.debug(f"Connecting to ssh with the following command: ssh {subprocess_options}")
child = pexpect.spawn("ssh", subprocess_options, encoding="UTF-8")

child.expect(".+ Password: ")
child.sendline(SECRET_rc_password)
child.expect(".+ VerificationCode: ")
child.sendline(SECRET_totp_token)

child.expect(pexpect.EOF)

logging.info(f"Successfully created SSH tunnel to {ssh_dest}")
