import logging


# service names to be stored in keychain
APP_KEYCHAIN_PREFIX = "python-totp-ssh.app"

SECRET_TOKEN_SERVICE_NAME = f"{APP_KEYCHAIN_PREFIX}.totp-secret-code"
PASSWORD_SERVICE_NAME = f"{APP_KEYCHAIN_PREFIX}.ssh-password"
SSH_USER_SERVICE_NAME = f"{APP_KEYCHAIN_PREFIX}.ssh-username"

# SSH login server
LOGIN_HOST_ALIAS = "cannon"
LOGIN_SSH_HOST = "login.rc.fas.harvard.edu"

# RC_FILE FILE KEYPOINTS (looks for this string to automaticaly add/remove text)
TOTP_BLOCK_START = "### START OF TOTP ALIASES ###"
TOTP_BLOCK_END = "### END OF TOTP ALIASES ###"

# optionally configure logging level
DEFAULT_LOG_LEVEL = logging.WARNING
DEFAULT_LOG_FORMAT = "%(levelname)s: %(message)s"

# number of seconds waiting for server to return the expected phrase before a timeout occures
PEXPECT_TIMEOUT_SECONDS = 10

# when checking if a tunnel exists, max time in seconds to wait for a response before failing
MAX_TIMEOUT_CHECK_TUNNEL = 10

# path to shell config file: .zshrc, .bashrc, etc.
RC_FILE = "~/.zshrc"

# ssh folder
SSH_FOLDER = "~/.ssh"

# ssh config file
SSH_CONFIG_FILE = f"{SSH_FOLDER}/config"

# ssh contorlmasters folder
SSH_CONTROLMASTERS_FOLDER = f"{SSH_FOLDER}/controlmasters"
