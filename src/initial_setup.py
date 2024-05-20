import os

from pathlib import Path
from set_passwords import prompt_and_store_passwords

print("Initial totp setup. You will need the following information for this process:")
print(" 1. host name (e.g. login.rc.fas.harvard.edu)")
print(" 2. ssh username")
print(" 3. ssh password")
print(" 4. totp secret key")
print('\n')


confirm_modify_ssh_config = input("Would you like to modify your ssh config file? (Y/N) ")
print()

if confirm_modify_ssh_config.lower() == "y" or confirm_modify_ssh_config.lower() == "yes":

    print("FIRST STEP: update ssh config")
    home_dir = os.environ['HOME']
    ssh_config_path = os.path.join(home_dir, '.ssh', 'config')

    ssh_config_content = Path(ssh_config_path).read_text()

    host_name = input("Enter the host name: ").strip()
    ssh_username = input("Enter your ssh username: ").strip()

    # output for the ssh config file
    ssh_config_template = f"""
Host {host_name}
    User {ssh_username}
    HostName {host_name}
    ServerKeepAliveInterval 60
    TCPKeepAlive no
    ControlMaster auto
    ControlPath ~/.ssh/controlmasters/%r@%h:%p
    ControlPersist yes""".strip()

    # create the new ssh config file
    ssh_config_content_new = f"""${ssh_config_content.strip()}

    {ssh_config_template}
    """

    Path(ssh_config_path).read_text(ssh_config_content_new)
    print("Updated ssh config at ~/.ssh/config\n")

else: # do not modify ssh config automatically
    ssh_username = None #populate later in the process
    print("Not changing ssh config. Make sure your ssh config entry for this host includes the following lines:")
    print("""...
ControlMaster auto
ControlPath ~/.ssh/controlmasters/%r@%h:%p
ControlPersist yes
...
""")
    
# prompt to setup initial passwords:

prompt_and_store_passwords(override_username=ssh_username)
