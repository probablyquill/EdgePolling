from polling.edge_polling import EdgeAPIPolling
from db import DataHandler
from polling.alert_manager import AlertManager
import polling.mail_handler as mail_handler
from config import check_config
import json
import time

class PollingAgent():
    def __init__(self):

        # Load configuration information from file.
        # Switched from enum class to json so that the config file could be
        # more easily modified by the program if changes need to be made.
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

        self.data_handler = DataHandler(sql_ip, sql_db, sql_user, sql_pw)
        self.alerting = AlertManager()
        self.blacklist = []

    def alert_manager(self):
        self.data_handler.connect_to_database()
        offline, erroring = self.data_handler.retrieve_for_alarming()
        recipients = self.data_handler.get_emails()
        self.data_handler.close_connection()

        alarms = self.alerting.check_alarms(offline, erroring, self.blacklist)

        if ((alarms != None) and (len(recipients) != 0)):
            # login, key, smtp, smpt port, recipients, subject, body
            mail_handler.send_email(self.email_sender, self.email_key, self.smtp_url, self.smtp_port, recipients, "Edge Device Alarms:\n", alarms)

    def poll_apis(self):
        self.data_handler.connect_to_database()
        self.blacklist = self.data_handler.get_blacklist()
        existing_ids = self.data_handler.get_edgeIDs()

        edgeAgent = EdgeAPIPolling(self.edge_usr, self.edge_pw, self.edge_url)
        edgeAgent.set_blacklist(self.blacklist)
        full_list = edgeAgent.pull_info()

        temp_ids = []

        # Get list of found edgeIDs
        for item in full_list:
            temp_ids.append(item["id"])
        
        # Check for removed edgeIDs
        for id in existing_ids:

            # Unpack tuple
            id = id[0]
            if id not in temp_ids:
                self.data_handler.delete_edgeID(id)

        # Manage SQL data using the DataHandler class
        self.data_handler.update_table(full_list)
        self.data_handler.close_connection()

if __name__ == "__main__":
    if check_config():
        agent = PollingAgent()

        while True:
            agent.poll_apis()
            agent.alert_manager()
            time.sleep(10)