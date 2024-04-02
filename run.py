from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response
import multiprocessing
from DataHandler import DataHandler
from PollingAgent import PollingAgent, confirm_config
import time
import json
from gevent.pywsgi import WSGIServer

#This should only be executed in a child process.
def start_agent(run_counter):
    agent = PollingAgent()

    while True:
        agent.poll_apis()
        agent.alert_manager()
        run_counter += 1
        time.sleep(10)

#Start the flask server.
def run_flask():
    #Load config info for SQL DB
    with open("config.json") as f:
        config_file = json.load(f)

        sql_ip = config_file["sql_ip"]
        sql_db = config_file["sql_db"]
        sql_user = config_file["sql_user"]
        sql_pw = config_file["sql_pw"]

        flask_port = config_file["flask_port"]
        flask_ip = config_file["flask_ip"]

    #Create datahandler object for SQL queries
    data_handler = DataHandler(sql_ip, sql_db, sql_user, sql_pw)

    #Flask app configuration.
    app = Flask(__name__, template_folder="web", static_folder="static")

    @app.route("/")
    def hello_world():
        return render_template("main.html")

    @app.route("/get_data")
    def get_data():
        #Retrieve Errors, Offline, and Blacklist for the User interface.
        data_handler.connect_to_database()
        offline, errors = data_handler.retrieve_for_alarming()
        blacklist = data_handler.get_blacklist_web()
        emails = data_handler.get_emails()
        data_handler.close_connection()

        #Use append versus using '= ["None,"]' as the later messes up the object.
        templist = [errors, offline, blacklist]
        for item in templist:
            if (len(item) == 0): item.append(["None", "None"])

        if (len(emails) == 0): emails.append("None")

        #Create data object which will be sent to the server.
        data = {
            "errors":errors,
            "offline":offline,
            "blacklist":blacklist,
            "emails":emails
        }
        
        return jsonify(data), 200
    
    #Completely untested lmao
    @app.route("/send_data", methods = ['POST'])
    def send_data():
        if request.method == "POST":
            incoming_data = request.get_json()
            print(incoming_data)

            data_handler.connect_to_database()

            #Remove json formated as string(edgeID)
            if ("remove_from_blacklist" in incoming_data.keys()):
                data_to_use = incoming_data["remove_from_blacklist"]
                if (len(data_to_use) > 1):
                    data_to_use = data_to_use[1]
                data_handler.remove_from_blacklist(data_to_use)

            #Add json formated as list [name, edgeID, type]
            if ("add_to_blacklist" in incoming_data.keys()):
                item = incoming_data["add_to_blacklist"]
                data_handler.update_blacklist(item[0], item[1], item[2])

            #Formatted as string(email)
            if ("add_email" in incoming_data.keys()):
                data_handler.add_email(incoming_data["add_email"])

            #Formatted as string(email)
            if ("delete_email" in incoming_data.keys()):
                data_handler.remove_email(incoming_data["delete_email"])
            
            data_handler.close_connection()

            resp = jsonify(success=True)
            return resp

    #Having debug enabled results in some funny issues such as print statments and emails double sending.
    #app.run(debug=False, host=flask_ip, port=flask_port)
    gevent_server = WSGIServer((flask_ip, flask_port), app)
    gevent_server.serve_forever()

#Required for multiprocessing to start correctly.
if __name__ == "__main__":
    if (confirm_config()):
        run_counter = 0
        multiprocessing.set_start_method("spawn")
        p = multiprocessing.Process(target=start_agent, args=(run_counter,))
        
        p.start()

        flask_p = multiprocessing.Process(target=run_flask)

        flask_p.start()

        #Kinda untested but in theory this should mean that if the
        #monitoring doesn't run in the last minute, it restarts the monitoring process.
        while True:
            time.sleep(60)

            if (run_counter < 1):
                p.terminate()
                p.start()

            run_counter = 0