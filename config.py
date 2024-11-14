import json

def check_config():
    # Frankly at least some of this should be getting stored in environment variables
    # with some kind of setup script. Bare minimum edge pw and email api key shouldn't
    # be getting stored in plain text.

    # Format: dict with key matching the value in the config file.
    # key: ("default value", "error message")
    errors_and_defaults = {
        "edge_em": ("thisis@myedgelogin.com", "Error: The edge user is missing or unconfigured."),
        "edge_key": ("edgePasswordGoesHere", "Error: The edge password is missing or unconfigured."),
        "edge_url": ("https://my-edge-installation.net/","Error: The edge url is missing or unconfigured."),
        "email_sender": ("smtp-username", "Error: The smtp user is missing or unconfigured."),
        "email_key": ("api key goes here", "Error: The smtp key is missing or unconfigured."),
        "smtp_url": ("smtp.server.com", "Error: The smtp url is missing or unconfigured."),
        "smtp_port": ("","Error: The smtp port is missing."),
        "sql_ip": ("", " Error: The sql server ip is missing.")
    }

    passFlag = True

    # Catch exceptions to have the program gracefully fail if the config file is missing
    # or there are value errors.
    try:
        with open("config.json") as f:
            config_file = json.load(f)
            for key in errors_and_defaults:
                default, error = errors_and_defaults[key]
                if (config_file[key] != default): continue
                passFlag = False
                print(error)

    except KeyError as e:
        print(str(e) + "\nMissing Value from Config File")
        passFlag = False

    except FileNotFoundError as e:
        print("The config file could not be found. Please refer to the README and ensure that you have a config.json file.")
        passFlag = False

    return passFlag
    
if __name__ == "__main__":
    if check_config():
        print("Success: Config file is present and has all needed values filled out.")
    else:
        print("Failure: Config file could not be validated.")