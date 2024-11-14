from flask import Flask, render_template, request, jsonify
from DataHandler import DataHandler
from waitress import serve

import json
import xml.etree.ElementTree as ET

# Start the flask server.
def run_flask():
    # Load config info for SQL DB
    with open("config.json") as f:
        config_file = json.load(f)

        sql_ip = config_file["sql_ip"]
        sql_db = config_file["sql_db"]
        sql_user = config_file["sql_user"]
        sql_pw = config_file["sql_pw"]

        flask_port = config_file["flask_port"]
        flask_ip = config_file["flask_ip"]

    # Create datahandler object for SQL queries
    data_handler = DataHandler(sql_ip, sql_db, sql_user, sql_pw)

    # Flask app configuration.
    app = Flask(__name__, template_folder="web", static_folder="static")

    @app.route("/", methods=['GET', 'POST'])
    def hello_world():
        if (request.method == 'GET'): return render_template("main.html") 
        if (request.method != 'POST'): return "Unsupported", 501

        root = ET.fromstring(request.data.decode('utf-8'))
        
        for child in root:
            if (child.tag != "event"): continue
            print(child.attrib)

            channel, message, date, time = "", "", "", ""
            mtype = 9999 # 0 is missing Audio, 1 is Missing Video. Sends a larger number when clearing the alert.

            # Parse alert
            if "channel" in child.attrib: channel = child.attrib["channel"]
            if "type" in child.attrib: mtype = int(child.attrib["type"])
            if "message" in child.attrib: message = child.attrib["messsage"]
            if "date" in child.attrib: date = child.attrib["date"]
            if "time" in child.attrib: time = child.attrib["time"]

            data_handler.connect_to_database()
            # Clear alert from database. Clear messages will have a type greater than 1.
            if mtype > 1: data_handler.remove_cinegy_alert(channel) 
            # Add alert to database  
            else: data_handler.add_cinegy_alert(channel, mtype, message, date, time)
            
            data_handler.close_connection()
        
        return "Success", 200

    @app.route("/get_data")
    def get_data():
        # Retrieve Errors, Offline, and Blacklist for the User interface.
        data_handler.connect_to_database()
        offline, errors = data_handler.retrieve_for_alarming()
        blacklist = data_handler.get_blacklist_web()
        emails = data_handler.get_emails()
        data_handler.close_connection()

        # Use append versus using '= ["None,"]' as the later messes up the object.
        templist = [errors, offline, blacklist]
        for item in templist:
            if (len(item) == 0): item.append(["None", "None"])

        if (len(emails) == 0): emails.append("None")

        # Create data object which will be sent to the server.
        data = {
            "errors":errors,
            "offline":offline,
            "blacklist":blacklist,
            "emails":emails
        }
        
        return jsonify(data), 200
    
    # Honestly this should probably return a pre-rendered flask template instead of
    # having it be generated client side with JS but whatever.
    @app.route("/send_data", methods = ['POST'])
    def send_data():
        if request.method == "POST":
            incoming_data = request.get_json()

            data_handler.connect_to_database()

            # Remove json formated as string(edgeID)
            if ("remove_from_blacklist" in incoming_data.keys()):
                data_to_use = incoming_data["remove_from_blacklist"]
                if (len(data_to_use) > 1):
                    data_to_use = data_to_use[1]
                data_handler.remove_from_blacklist(data_to_use)

            # Add json formated as list [name, edgeID, type]
            if ("add_to_blacklist" in incoming_data.keys()):
                item = incoming_data["add_to_blacklist"]
                data_handler.update_blacklist(item[0], item[1], item[2])

            # Formatted as string(email)
            if ("add_email" in incoming_data.keys()):
                data_handler.add_email(incoming_data["add_email"])

            # Formatted as string(email)
            if ("delete_email" in incoming_data.keys()):
                data_handler.remove_email(incoming_data["delete_email"])
            
            data_handler.close_connection()

            resp = jsonify(success=True)
            return resp

    # Having debug enabled results in some funny issues such as print statments and emails double sending.
    # app.run(debug=False, host=flask_ip, port=flask_port)
    serve(app, host=flask_ip, port=flask_port)