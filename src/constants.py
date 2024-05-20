# service names to be stored in keychain
APP_KEYCHAIN_PREFIX = "python-totp-ssh.app"

SECRET_TOKEN_SERVICE_NAME = f"{APP_KEYCHAIN_PREFIX}.totp-secret-code"
PASSWORD_SERVICE_NAME = f"{APP_KEYCHAIN_PREFIX}.ssh-password"
SSH_USER_SERVICE_NAME = f"{APP_KEYCHAIN_PREFIX}.ssh-username"

# SSH login server
FASRC_LOGIN_SSH_HOST = "login.rc.fas.harvard.edu"
