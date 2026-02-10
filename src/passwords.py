import getpass
import logging
import re
from binascii import Error as BinasciiError
from urllib.parse import parse_qs, urlparse

import keyring
from keyring.errors import PasswordDeleteError
import pyotp
from src.constants import (
    PASSWORD_SERVICE_NAME,
    SECRET_TOKEN_SERVICE_NAME,
    SSH_USER_SERVICE_NAME,
)

username = getpass.getuser()
BASE32_ALPHABET = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567=")


def get_totp_code():
    return keyring.get_password(SECRET_TOKEN_SERVICE_NAME, username)


def get_rc_password():
    return keyring.get_password(PASSWORD_SERVICE_NAME, username)


def get_ssh_user():
    return keyring.get_password(SSH_USER_SERVICE_NAME, username)


def normalize_totp_secret(raw_secret):
    """Normalize TOTP input into a plain base32 secret string."""
    if raw_secret is None:
        return None

    secret = raw_secret.strip().strip('"').strip("'")

    # Accept full otpauth URIs by extracting the secret query parameter.
    if secret.lower().startswith("otpauth://"):
        parsed = urlparse(secret)
        uri_secret = parse_qs(parsed.query).get("secret", [None])[0]
        if uri_secret is not None:
            secret = uri_secret

    # Ignore spacing/group separators commonly used when displaying secrets.
    secret = re.sub(r"[\s-]+", "", secret).upper()

    return secret


def validate_totp_secret(raw_secret):
    """Return normalized secret or raise ValueError with a user-facing message."""
    secret = normalize_totp_secret(raw_secret)

    if not secret:
        raise ValueError("TOTP secret is empty after normalization.")

    invalid_chars = sorted({char for char in secret if char not in BASE32_ALPHABET})
    if invalid_chars:
        preview = "".join(invalid_chars[:10])
        raise ValueError(
            "TOTP secret contains invalid characters for base32 decoding: "
            f"{preview}"
        )

    try:
        pyotp.TOTP(secret).byte_secret()
    except (BinasciiError, TypeError, ValueError) as e:
        raise ValueError(
            "TOTP secret is not valid base32. Re-run ./scripts/install and update "
            "passwords with your raw secret token."
        ) from e

    return secret


def generate_otp():
    SECRET_totp_code = get_totp_code()
    if SECRET_totp_code is None:
        return None

    normalized_totp_code = validate_totp_secret(SECRET_totp_code)

    return pyotp.TOTP(normalized_totp_code).now()


def prompt_and_store_passwords(override_username=None):
    """Prompt user for passwords and store them in keychain. Return true if all passwords are set successfully"""

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
        "Enter your TOTP secret token (long base32 key from FASRC page, not the 6-digit code; stored locally in keyring): "
    )

    try:
        normalized_user_input_token = validate_totp_secret(user_input_token)
    except ValueError as e:
        raise Exception(f"Invalid TOTP token: {e}") from e

    if len(normalized_user_input_token) < 10:
        raise Exception(
            "Token is too short to be valid. Should be ~16 characters. Exiting script."
        )

    # Save all passwords to keyring
    try:
        keyring.set_password(PASSWORD_SERVICE_NAME, local_username, user_input_pass)
        keyring.set_password(
            SECRET_TOKEN_SERVICE_NAME, local_username, normalized_user_input_token
        )
        keyring.set_password(
            SSH_USER_SERVICE_NAME, local_username, user_input_ssh_uname
        )

    except Exception:
        raise Exception("Unable to save all passwords to keyring. Exiting script.")

    logging.info("Saved passwords to keyring successfully. Done!")

    # check that all passwords are set successfully
    return are_all_passwords_set()


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


def are_all_passwords_set():
    """Check if all passwords are set. Return TRUE if any password is not set"""
    attempts = [
        get_totp_code() is not None,
        get_rc_password() is not None,
        get_ssh_user() is not None,
    ]
    return all(attempts)
