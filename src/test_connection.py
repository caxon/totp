import subprocess
import os
import logging

MAX_TIMOUT_CHECK_TUNNEL = 10  # seconds


def is_controlmaster_open(
    ssh_dest, controlmaster_path="~/.ssh/controlmasters", ssh_port=22
):
    """Test if controlmaster tunnel is open"""

    socket_filename = f"{ssh_dest}:{ssh_port}"
    socket_path = os.path.join(controlmaster_path, socket_filename)
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
        logging.debug(f"Check tunnel process OUTPUT: { str(completed_process.stdout)}")
        logging.debug(f"Check tunnel process ERROR: {str(completed_process.stderr) }")
    except subprocess.TimeoutExpired:
        print(
            f"Timeout expired. Unable to verify tunnel exists in under {MAX_TIMOUT_CHECK_TUNNEL} seconds"
        )
    if completed_process.returncode == 0:
        # code 0 means success
        logging.info(f"Tunnel exists: {socket_path}")
        return True
    else:
        logging.info(f"Tunnel does not exist: {socket_path}")
        # anything else means the test failed
        return False


if __name__ == "__main__":
    ret_val = is_controlmaster_open("caxon@login.rc.fas.harvard.edu")
    print(f"IS CONTROLMASTER OPEN? { 'True' if ret_val else 'False'} ")
