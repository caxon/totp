import logging
import os
import subprocess
from pathlib import Path

from src.constants import (
    DEFAULT_LOG_FORMAT,
    LOGIN_SSH_HOST,
    MAX_TIMEOUT_CHECK_TUNNEL,
    SSH_CONTROLMASTERS_FOLDER,
)
from src.passwords import get_ssh_user


def is_controlmaster_open(
    ssh_dest, controlmaster_path=SSH_CONTROLMASTERS_FOLDER, ssh_port=22
):
    """Test if controlmaster tunnel is open"""

    socket_filename = f"{ssh_dest}:{ssh_port}"
    controlmaster_path_full = Path(controlmaster_path).expanduser()
    if not controlmaster_path_full.is_dir():
        raise Exception(
            f"Controlmaster folder does not exist. Try creating a folder at: {SSH_CONTROLMASTERS_FOLDER}"
        )
    socket_path = os.path.join(controlmaster_path, socket_filename)
    logging.info("checking ssh tunnel at: {}".format(socket_path))
    args = [
        "ssh",
        "-o",
        f"ControlPath={socket_path}",
        "-O",
        "check",
        "dummy_arg",  # needs a dummy arg or else this fails
    ]
    try:
        completed_process = subprocess.run(args, timeout=10, capture_output=True)
        completed_process.stderr
        out = str(completed_process.stdout)
        err = str(completed_process.stderr)
        logging.info(f"Check tunnel process OUTPUT: {out}")
        logging.info(f"Check tunnel process ERROR: {err}")
    except subprocess.TimeoutExpired:
        logging.warning(
            f"Timeout expired. Unable to verify tunnel exists in under {MAX_TIMEOUT_CHECK_TUNNEL} seconds"
        )
    if completed_process.returncode == 0:
        # code 0 means success
        logging.info("Tunnel is open")
        return True
    else:
        logging.info("Tunnel is not open")
        # anything else means the test failed
        return False


if __name__ == "__main__":
    logging.basicConfig(format=DEFAULT_LOG_FORMAT, level=logging.INFO)
    ssh_user = get_ssh_user()
    ret_val = is_controlmaster_open(f"{ssh_user}@{LOGIN_SSH_HOST}")
    logging.warning(f"IS CONTROLMASTER OPEN? { 'True' if ret_val else 'False'} ")
