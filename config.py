import json
import logger, logging

def check_config():
    # Setup logger
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)

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
                if (config_file[key] != default):
                    log.info(f"Confirmed key {key}.")
                    continue
                
                passFlag = False
                log.error(error)

    except KeyError as e:
        log.critical("KeyError: Missing values in config file.")
        passFlag = False

    except FileNotFoundError as e:
        print("The config file could not be found. Please refer to the README and ensure that you have a config.json file.")
        log.critical("MISSING: Config file could not be found.")
        passFlag = False
    if passFlag:
        log.info("Config check succeeded.")
    else:
        log.info("Config check failed.")

    return passFlag

if __name__ == "__main__":
    logger.init("config")

    if check_config():
        print("Success: Config file is present and has all needed values filled out.")
    else:
        print("Failure: Config file could not be validated.")