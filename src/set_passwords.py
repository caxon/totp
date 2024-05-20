import getpass
import logging

import keyring


from .constants import (
    SECRET_TOKEN_SERVICE_NAME,
    PASSWORD_SERVICE_NAME,
    SSH_USER_SERVICE_NAME,
)

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
        raise Exception("Unable to save passwords to keyring. Exiting script.")

    logging.info("Saved passwords to keyring successfully. Done!")

