from polling.EdgeAPIPolling import EdgeAPIPolling
from DataHandler import DataHandler
from polling.AlertManager import AlertManager
import polling.MailHandler as MailHandler
import json

class PollingAgent():
    def __init__(self):

        #Load configuration information from file.
        #Switched from enum class to json so that the config file could be
        #more easily modified by the program if changes need to be made.
        with open("config.json") as f:
            config_file = json.load(f)

            self.edge_usr = config_file["edge_em"]
            self.edge_pw = config_file["edge_key"]
            self.edge_url = config_file["edge_url"]

            self.email_sender = config_file["email_sender"]
            self.email_key = config_file["email_key"]

            self.smtp_url = config_file["smtp_url"]
            self.smtp_port = config_file["smtp_port"]
            #I'm not 100% sure how I want to structure it at the moment, however 
            #I think I'm going to change the email list to be in the sql db for easier modification.

            sql_ip = config_file["sql_ip"]
            sql_db = config_file["sql_db"]
            sql_user = config_file["sql_user"]
            sql_pw = config_file["sql_pw"]

        self.data_handler = DataHandler(sql_ip, sql_db, sql_user, sql_pw)
        self.alerting = AlertManager()

    def alert_manager(self):
        self.data_handler.connect_to_database()
        offline, erroring = self.data_handler.retrieve_for_alarming()
        recipients = self.data_handler.get_emails()
        self.data_handler.close_connection()

        alarms = self.alerting.check_alarms(offline, erroring)

        if (alarms != None):
            #login, key, smtp, smpt port, recipients, subject, body
            MailHandler.send_email(self.email_sender, self.email_key, self.smtp_url, self.smtp_port, recipients, "Edge Device Alarms:\n", alarms)

    def poll_apis(self):
        self.data_handler.connect_to_database()
        blacklist = self.data_handler.get_blacklist()

        edgeAgent = EdgeAPIPolling(self.edge_usr, self.edge_pw, self.edge_url)
        edgeAgent.set_blacklist(blacklist)
        offline, io_list, errors = edgeAgent.pull_info()

        #Manage SQL data using the DataHandler class
        self.data_handler.update_offline(offline)
        self.data_handler.update_fields(io_list)
        self.data_handler.update_errors(errors)
        self.data_handler.close_connection()

if __name__ == "__main__":
    print("Running")
    agent = PollingAgent()
    agent.poll_apis()
    agent.alert_manager()