import argparse
import logging
import sys
from io import StringIO

import pexpect

from .constants import (
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    LOGIN_SSH_HOST,
    PEXPECT_TIMEOUT_SECONDS,
    SSH_CONTROLMASTERS_FOLDER,
)
from .passwords import (
    generate_otp,
    get_rc_password,
    get_ssh_user,
    get_totp_code,
    prompt_and_store_passwords,
)
from .test_connection import is_controlmaster_open


def init_logging(log_level=DEFAULT_LOG_LEVEL):
    # set up logigng (default is warn or higher)
    logging.basicConfig(format=DEFAULT_LOG_FORMAT, level=log_level)


def make_ssh_options(ssh_dest):
    """Make argument list for the ssh command to create a tunnel"""
    ssh_config_dict = {
        "TCPKeepAlive": "no",  # Use ServerKeepAlive instead
        "ServerAliveInterval": "60",  # prevent dropped connections by sending a ping every X seconds
        "IdentitiesOnly": "yes",  # Don't attempt key-based ssh auth (connection cannot use identies anyways)
        "ControlMaster": "yes",  # Use single control socket for SSH
        "ControlPath": f"{SSH_CONTROLMASTERS_FOLDER}/%r@%h:%p",  # Path to ssh control sockets
        "ControlPersist": "yes",  # Keep master connection open in the background
        "StrictHostKeyChecking": "accept-new",  # accept new ssh host, but DO NOT accept existing hosts where key has changed
        "NumberOfPasswordPrompts": "1",
    }

    ssh_positional_options = [
        "-F",
        "none",  # Do not read from SSH config file (config_file = None)
        "-X",  # enable X11 forwarding (if you want to run graphical applicaitons over tunnel connection)
        "-N",  # do not execute remote commands (just open tunnel)
        # "-C",  # not sure if compression helps - since file is encrypted and connection is likely very fast
    ]
    ssh_config_options_as_list = []
    for key in ssh_config_dict:
        val = ssh_config_dict[key]
        ssh_config_options_as_list.append("-o")
        ssh_config_options_as_list.append(f"{key}={val}")

    subprocess_options = [
        *ssh_positional_options,
        *ssh_config_options_as_list,
        ssh_dest,
    ]

    return subprocess_options


def start_ssh_tunnel():
    # get passwords from MacOS Keychain
    SECRET_totp_code = get_totp_code()
    SECRET_rc_password = get_rc_password()
    SECRET_ssh_user = get_ssh_user()

    # if at least one of the secrets is missing then offer to initilaize them
    if (
        SECRET_totp_code is None
        or SECRET_rc_password is None
        or SECRET_ssh_user is None
    ):
        logging.error("At least one required password is missing from keyring")
        logging.error("Run ./scripts/install to set up totp app")
        sys.exit(1)

    ssh_dest = f"{SECRET_ssh_user}@{LOGIN_SSH_HOST}"

    # test if controlmaster is alrady running

    running = is_controlmaster_open(ssh_dest=ssh_dest)
    if running:
        logging.info("Doing nothing and exiting")
        sys.exit(0)
    else:
        logging.info("Creating new ssh tunnel")

    # generated 6-digit one-time authentication token
    totp_otp = generate_otp()

    subprocess_options = make_ssh_options(ssh_dest=ssh_dest)

    logging.info(
        f"Connecting to ssh with the following command: ssh {subprocess_options}"
    )
    child = pexpect.spawn(
        "ssh", subprocess_options, encoding="UTF-8", timeout=PEXPECT_TIMEOUT_SECONDS
    )
    try:
        logfile_read = StringIO()
        child.logfile_read = logfile_read
        child.expect(r".+ Password: ")
        child.sendline(SECRET_rc_password)
        child.expect(r".+ VerificationCode: ")
        child.sendline(totp_otp)
        idx = child.expect([pexpect.EOF, r".+ Permission denied"])
        if idx == 1:
            logging.error(
                "Permission denied by ssh server. Double check passwords and try again. Run ./scripts/install to update passwords."
            )
            sys.exit(1)

    except pexpect.TIMEOUT as e:
        logging.error(
            "Timed out waitings for specific ssh response. Try again with --verbose for more information."
        )
        logging.info("STDOUT from ssh process:\n\n{}".format(logfile_read.getvalue()))
        logging.info("FULL ERROR TEXT:\n\n{}".format(e))
        sys.exit(1)
    except pexpect.EOF as e:
        logging.error(
            "SSH process unexpectedly exited. Try again with --verbose for more information."
        )
        logging.info("Output from ssh process:\n\n{}".format(logfile_read.getvalue()))
        logging.info("FULL ERROR TEXT:\n\n{}".format(e))
        sys.exit(1)

    logging.info(f"Successfully created SSH tunnel for {ssh_dest}")


if __name__ == "__main__":
    # optionally specify verbose logging
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        help="enable verbose logging",
        action="store_true",
        dest="verbose",
    )
    args = parser.parse_args()

    if args.verbose:
        init_logging(log_level=logging.INFO)
        logging.info("Verbose logging enabled")
    else:
        init_logging()

    start_ssh_tunnel()
