from polling.edge_polling import EdgeAPIPolling
from db import DataHandler
import polling.alert_manager as am
import polling.mail_handler as mail_handler
from config import check_config
import json
import time
import logger, logging

class PollingAgent():
    def __init__(self):
        # Create logger for agent and its imports.
        logger.init("agent")
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        # Load configuration information from file.
        # Switched from enum class to json so that the config file could be
        # more easily modified by the program if changes need to be made.
        self.log.info("Reading configuration file.")
        with open("config.json") as f:
            config_file = json.load(f)

            self.edge_usr = config_file["edge_em"]
            self.edge_pw = config_file["edge_key"]
            self.edge_url = config_file["edge_url"]

            self.email_sender = config_file["email_sender"]
            self.email_key = config_file["email_key"]

            self.smtp_url = config_file["smtp_url"]
            self.smtp_port = config_file["smtp_port"]

            sql_ip = config_file["sql_ip"]
            sql_db = config_file["sql_db"]
            sql_user = config_file["sql_user"]
            sql_pw = config_file["sql_pw"]

        self.log.info("Configuration data loaded successfully.")
        self.log.info("Creating DataHandler")
        self.data_handler = DataHandler(sql_ip, sql_db, sql_user, sql_pw)

        self.log.info("Creating EdgeAPIPolling")
        self.edgeAgent = EdgeAPIPolling(self.edge_usr, self.edge_pw, self.edge_url)
        self.blacklist = []

    # TODO Rework alert manager. Currently it's based off a very rough sleep based solution that takes advantage of the fact that
    # the program pases so that it only queries every x seconds at max. A prefered solution would be to have it compare the start 
    # of the alarm time to the present to determine whether or not it will send an alert.
    def alert_manager(self):
        self.data_handler.connect_to_database()
        offline, erroring = self.data_handler.retrieve_for_alarming()
        recipients = self.data_handler.get_emails()
        self.data_handler.close_connection()

        for name, id in offline:
            self.log.warning(f"DEVICE [{name}] with ID: [{id}] is offline.")

        for name, id in erroring:
            self.log.warning(f"DEVICE [{name}] with ID: [{id}] is erroring.")

        # The alert manager is fed the list of offline and erroring clients, compares them against the blacklist, and then returns
        # if there are any edge devices that should presently be alarming.
        alarms = am.check_alarms(offline, erroring, self.blacklist)

        if ((alarms != None) and (len(recipients) != 0)):
            # login, key, smtp, smpt port, recipients, subject, body
            self.log.info("Sending Email Alert.")
            mail_handler.send_email(self.email_sender, self.email_key, self.smtp_url, self.smtp_port, recipients, "Edge Device Alarms:\n", alarms)

    def poll_apis(self):
        self.data_handler.connect_to_database()
        self.blacklist = self.data_handler.get_blacklist()

        # Retrieves list of IDs currently in the database.
        existing_ids = self.data_handler.get_edgeIDs()
        self.edgeAgent.set_blacklist(self.blacklist)
        
        # Retrieves list of devices and paths currently present in Edge.
        full_list = self.edgeAgent.pull_info()
        temp_ids = []

        # Get list of found edgeIDs
        for item in full_list:
            temp_ids.append(item["id"])
        
        # Check for removed edgeIDs. If a device is present in the database but is no longer present in edge, 
        # then it should be removed from the database.
        for id in existing_ids:

            # Unpack tuple. Loads in as (id,...)
            id = id[0]
            if id not in temp_ids:
                self.data_handler.delete_edgeID(id)

        # Push updates to the database then close the connection.
        self.data_handler.update_table(full_list)
        self.data_handler.close_connection()

if __name__ == "__main__":
    if check_config():
        agent = PollingAgent()

        agent.poll_apis()
        agent.alert_manager()
        time.sleep(10)