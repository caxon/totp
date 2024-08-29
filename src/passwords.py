import getpass
import logging

import keyring
from keyring.errors import PasswordDeleteError
import pyotp
from .constants import (
    PASSWORD_SERVICE_NAME,
    SECRET_TOKEN_SERVICE_NAME,
    SSH_USER_SERVICE_NAME,
)

username = getpass.getuser()


def get_totp_code():
    return keyring.get_password(SECRET_TOKEN_SERVICE_NAME, username)


def get_rc_password():
    return keyring.get_password(PASSWORD_SERVICE_NAME, username)


def get_ssh_user():
    return keyring.get_password(SSH_USER_SERVICE_NAME, username)


def generate_otp():
    SECRET_totp_code = get_totp_code()
    if SECRET_totp_code is None:
        return None

    return pyotp.TOTP(SECRET_totp_code).now()


def prompt_and_store_passwords(override_username=None):
    """Prompt user for passwords and store them in keychain"""

    local_username = getpass.getuser()

    if override_username:
        user_input_ssh_uname = override_username
    else:
        ### SSH USERNAME
        user_input_ssh_uname = getpass.getpass(
            "Enter you username on the fasrc server (will be stored locally and encrypted in keyring): "
        )

        if len(user_input_ssh_uname) < 3:
            raise Exception(
                "Username is too short. Did you even enter a name? Exiting script."
            )

    ### FASRC USER PASSWORD
    user_input_pass = getpass.getpass(
        "Enter your fasrc password (will be stored locally and encrypted in keyring): "
    )

    if len(user_input_pass) < 10:
        raise Exception("Password is too short to be valid. Exiting script.")

    ### TOTP SECRET CODE
    user_input_token = getpass.getpass(
        "Enter your totp secret token (will be stored locally and encrypted in keyring): "
    )

    if len(user_input_token) < 10:
        raise Exception(
            "Token is too short to be valid. Should be ~16 charcters. Exiting script."
        )

    # Save all passwords to keyring
    try:
        keyring.set_password(PASSWORD_SERVICE_NAME, local_username, user_input_pass)
        keyring.set_password(
            SECRET_TOKEN_SERVICE_NAME, local_username, user_input_token
        )
        keyring.set_password(
            SSH_USER_SERVICE_NAME, local_username, user_input_ssh_uname
        )

    except Exception:
        raise Exception("Unable to save all passwords to keyring. Exiting script.")

    logging.info("Saved passwords to keyring successfully. Done!")


def remove_passwords():
    local_username = getpass.getuser()

    del_errors = 0

    try:
        keyring.delete_password(PASSWORD_SERVICE_NAME, local_username)
    except PasswordDeleteError as e:
        del_errors += 1
        logging.warning(str([*e.args, PASSWORD_SERVICE_NAME, local_username]))
    try:
        keyring.delete_password(SECRET_TOKEN_SERVICE_NAME, local_username)
    except PasswordDeleteError as e:
        del_errors += 1
        logging.warning(str([*e.args, SECRET_TOKEN_SERVICE_NAME, local_username]))
    try:
        keyring.delete_password(SSH_USER_SERVICE_NAME, local_username)
    except PasswordDeleteError as e:
        del_errors += 1
        logging.warning(str([*e.args, SSH_USER_SERVICE_NAME, local_username]))

    if del_errors > 0:
        logging.warning(
            "At least one error removing passwords from keychain. This could mean they have already been deleted. If you are concerned, open the keychain app and manually delete them."
        )
        logging.warning(
            f"Look for the following service names in the keychain app: \n\t- {PASSWORD_SERVICE_NAME}\n\t- {SSH_USER_SERVICE_NAME}\n\t- {SECRET_TOKEN_SERVICE_NAME}"
        )

    else:
        logging.info("Keyring passwords removed successfully.")
