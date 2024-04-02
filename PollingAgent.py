from polling.EdgeAPIPolling import EdgeAPIPolling
from DataHandler import DataHandler
from polling.AlertManager import AlertManager
import polling.MailHandler as MailHandler
import json
import time

def confirm_config():
    pass_flag = True
    try:
        with open("config.json") as f:
            config_file = json.load(f)
            edge_em = config_file["edge_em"]
            edge_key = config_file["edge_key"]
            edge_url = config_file["edge_url"]

            email_sender = config_file["email_sender"]
            email_key = config_file["email_key"]

            smtp_url = config_file["smtp_url"]
            smtp_port = config_file["smtp_port"]

            sql_ip = config_file["sql_ip"]
            sql_db = config_file["sql_db"]
            sql_user = config_file["sql_user"]
            sql_pw = config_file["sql_pw"]

            #Check to ensure that required config data is not empty or using the placeholder values.
            if (edge_em == "" or edge_em == "thisis@myedgelogin.com"):
                print("Error: The edge user is missing or unconfigured.")
                pass_flag = False
            if (edge_key == "" or edge_key =="edgePasswordGoesHere"):
                print("Error: The edge password is missing or unconfigured.")
                pass_flag = False
            if (edge_url == "" or edge_url == "https://my-edge-installation.net/"):
                print("Error: The edge url is missing or unconfigured.")
                pass_flag = False
            if (email_sender == "" or email_sender == "smtp-username"):
                print("Error: The smtp user is missing or unconfigured.")
                pass_flag = False
            if (email_key == "" or email_key == "api key goes here"):
                print("Error: The smtp key is missing or unconfigured.")
                pass_flag = False
            if (smtp_url == "" or smtp_url == "smtp.server.com"):
                print("Error: The smtp url is missing or unconfigured.")
                pass_flag = False
            if (smtp_port == ""):
                print("Error: The smtp port is missing.")
                pass_flag = False
            if (sql_ip == ""):
                print("Error: The sql server ip is missing.")
                pass_flag = False

    except FileNotFoundError as e:
        print("Error: The config.json file is missing. Please refer to the README.")
        pass_flag = False

    except Exception as e:
        print(e)
        pass_flag = False

    return pass_flag

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
        self.blacklist = []

    def alert_manager(self):
        self.data_handler.connect_to_database()
        offline, erroring = self.data_handler.retrieve_for_alarming()
        recipients = self.data_handler.get_emails()
        self.data_handler.close_connection()

        alarms = self.alerting.check_alarms(offline, erroring, self.blacklist)

        if ((alarms != None) and (len(recipients) != 0)):
            #login, key, smtp, smpt port, recipients, subject, body
            MailHandler.send_email(self.email_sender, self.email_key, self.smtp_url, self.smtp_port, recipients, "Edge Device Alarms:\n", alarms)

    def poll_apis(self):
        self.data_handler.connect_to_database()
        self.blacklist = self.data_handler.get_blacklist()
        existing_ids = self.data_handler.get_edgeIDs()

        edgeAgent = EdgeAPIPolling(self.edge_usr, self.edge_pw, self.edge_url)
        edgeAgent.set_blacklist(self.blacklist)
        full_list = edgeAgent.pull_info()

        temp_ids = []

        #Get list of found edgeIDs
        for item in full_list:
            temp_ids.append(item["id"])
        
        #Check for removed edgeIDs
        for id in existing_ids:

            #Unpack tuple
            id = id[0]
            if id not in temp_ids:
                self.data_handler.delete_edgeID(id)

        #Manage SQL data using the DataHandler class
        self.data_handler.update_table(full_list)
        self.data_handler.close_connection()

if __name__ == "__main__":
    print("Running")
    assert confirm_config()

    agent = PollingAgent()

    while True:
        agent.poll_apis()
        agent.alert_manager()
        time.sleep(10)