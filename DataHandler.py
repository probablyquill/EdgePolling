import mysql
import mysql.connector

class DataHandler():
    def __init__(self, sql_location, sql_database, sql_usr, sql_pw):
        self.database = sql_database
        self.location = sql_location
        self.user = sql_usr
        self.password = sql_pw

        self.sql_cnx = None
        self.sql_cur = None

    #Creates all needed table if they don't already exist and establishes the sql connection and cursor.
    def connect_to_database(self):
        self.sql_cnx = mysql.connector.connect(user=self.user, password=self.password, host=self.location, database=self.database)
        self.sql_cur = self.sql_cnx.cursor()

        self.sql_cur.execute("CREATE TABLE IF NOT EXISTS edge(edgeID TEXT NOT NULL, name TEXT, status TEXT, msg TEXT, state TEXT, type TEXT, blacklist INT DEFAULT 0, time INT, KEY(edgeID(36)));")
        self.sql_cur.execute("CREATE TABLE IF NOT EXISTS emails(address TEXT);")

    #Closes the sql connection by clearing both the connection and the cursor.
    def close_connection(self):
        if self.sql_cur != None: self.sql_cnx.close()
        if self.sql_cnx != None: self.sql_cnx.close()

    def get_offline(self):
        self.sql_cur.execute("SELECT name, edgeID FROM edge WHERE status=\"missing\";")
        offline_list = self.sql_cur.fetchall()
        
        return offline_list

    def get_fields(self):
        self.sql_cur.execute("SELECT * FROM edge WHERE type=\"input\" OR type=\"output\";")
        fields_list = self.sql_cur.fetchall()

        return fields_list

    def get_errors(self):
        self.sql_cur.execute("SELECT name, edgeID FROM errors;")
        error_list = self.sql_cur.fetchall()
        
        return error_list

    #These can both be combined into the same item, if the logic in PollingAgent is adjusted.
    def get_blacklist_web(self):
        self.sql_cur.execute("SELECT name, edgeID from edge WHERE blacklist=1;")
        blacklist = self.sql_cur.fetchall()

        return blacklist

    def get_blacklist(self):
        self.sql_cur.execute("SELECT * from edge WHERE blacklist=1;")
        templist = self.sql_cur.fetchall()

        list = []

        for item in templist:
            #Done this way in order to clear the tuple so that it's just a list of strings.
            list.append(item[0])

        return list

    def update_blacklist(self, name, edgeID, type):
        self.sql_cur.execute("UPDATE SET blacklist=1 WHERE edgeID=%s", (edgeID,))
        
        self.sql_cnx.commit()

    #Offline is a list of the dicts pulled from the api. 
    """def update_offline(self, offline):
        self.sql_cur.execute("TRUNCATE TABLE offline;")

        for item in offline:
            self.sql_cur.execute("INSERT INTO offline(edgeID, name, status) VALUES (%s, %s, %s)", (item["id"], item["name"], item["health"]["state"]))
        
        self.sql_cnx.commit()

    #io_list is a list of the dicts made from the API.
    def update_fields(self, io_list):
        self.sql_cur.execute("TRUNCATE TABLE fields;")

        for item in io_list:
            self.sql_cur.execute("INSERT INTO fields(edgeID, name, status, msg, isout, time) VALUES (%s, %s, %s, %s, %s, %s)", (item['id'], item['name'], item['status'], item['msg'], item['type'], item['time']))
        
        self.sql_cnx.commit()

    #error_list is a list of the dicts made from the API.
    def update_errors(self, error_list):
        self.sql_cur.execute("TRUNCATE TABLE errors;")

        for item in error_list:
            self.sql_cur.execute("INSERT INTO errors(edgeID, name, status, msg, isout, alarm, time) VALUES (%s, %s, %s, %s, %s, %s, %s)", (item['id'], item['name'], item['status'], item['msg'], item['type'], str(1), item['time']))
        
        self.sql_cnx.commit()"""

    #edgeID is a string of the edge id.
    def remove_from_blacklist(self, edgeID):
        self.sql_cur.execute("UPDATE SET blacklist=0 WHERE edgeID=%s", (edgeID))
        self.sql_cnx.commit()

    def retrieve_for_alarming(self):
        self.sql_cur.execute("SELECT * FROM edge WHERE type=\"appliance\" AND status=\"missing\";")
        offline = (self.sql_cur.fetchall())
        
        self.sql_cur.execute("SELECT * FROM edge WHERE 'status' LIKE %{$error}%")
        erroring = (self.sql_cur.fetchall())

        return (offline, erroring)
    
    def get_emails(self):
        self.sql_cur.execute("SELECT * FROM emails;")
        templist = self.sql_cur.fetchall()

        emails = []

        for item in templist:
            #Done this way in order to clear the tuple so that it's just a list of strings.
            #Data is returned from the cursor as (email,).
            emails.append(item[0])
        
        return emails
    
    def add_email(self, address):
        self.sql_cur.execute("INSERT INTO emails(address) VALUES (%s)", (address,))
        self.sql_cnx.commit()

    def remove_email(self, address):
        self.sql_cur.execute("DELETE FROM emails WHERE address = %s;", (address,))
        self.sql_cnx.commit()

    #edgeID TEXT NOT NULL, name TEXT, status TEXT, msg TEXT, state TEXT, type TEXT, blacklist INT, time INT,
    #INSERT INTO table () VALUES () ON DUPLICATE KEY UPDATE parameter="example", p2=0
    def update_appliances(self, appliances):
        for appliance in appliances:
            self.sql_cur.execute("INSERT INTO edge(edgeID, name, status, msg, type, time) VALUES(%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=%s, status=%s, msg=%s, time=%s", 
                                 (appliance["id"], appliance["name"], appliance["status"], appliance["msg"], appliance["type"], appliance["time"], appliance["name"], appliance["status"], appliance["msg"], appliance["time"]))
            
        self.sql_cnx.commit()

    def update_io(self, io_list):
        for item in io_list:
            self.sql_cur.execute("INSERT INTO edge(edgeID, name, status, msg, type, time) VALUES(%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=%s, status=%s, msg=%s, time=%s", 
                                 (item["id"], item["name"], item["status"], item["msg"], item["type"], item["time"], item["name"], item["status"], item["msg"], item["time"]))
            
        self.sql_cnx.commit()