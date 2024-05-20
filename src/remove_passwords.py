import getpass
import logging

import keyring
from keyring.errors import PasswordDeleteError

from .constants import (
    SECRET_TOKEN_SERVICE_NAME,
    PASSWORD_SERVICE_NAME,
    SSH_USER_SERVICE_NAME,
)


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
       logging.warning("At least one error removing passwords from keychain. This could mean they have already been deleted. If you are concerned, open the keychain app and manually delete them.") 

    else:
        logging.info("Keyring passwords removed successfully.")


if __name__ == "__main__":
    remove_passwords()
