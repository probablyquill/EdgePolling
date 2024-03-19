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

        self.sql_cur.execute("CREATE TABLE IF NOT EXISTS fields(edgeID TEXT, name TEXT, status TEXT, msg TEXT, isout INT, time INT);")
        self.sql_cur.execute("CREATE TABLE IF NOT EXISTS errors(edgeID TEXT, name TEXT, status TEXT, msg TEXT, isout INT, alarm INT, time INT);")
        self.sql_cur.execute("CREATE TABLE IF NOT EXISTS offline(edgeID TEXT, name TEXT, status TEXT)")
        self.sql_cur.execute("CREATE TABLE IF NOT EXISTS blacklist(edgeID TEXT, name TEXT, type TEXT);")
        self.sql_cur.execute("CREATE TABLE IF NOT EXISTS emails(address TEXT);")

    #Closes the sql connection by clearing both the connection and the cursor.
    def close_connection(self):
        if self.sql_cur != None: self.sql_cnx.close()
        if self.sql_cnx != None: self.sql_cnx.close()

    def get_offline(self):
        self.sql_cur.execute("SELECT name, edgeID FROM offline;")
        offline_list = self.sql_cur.fetchall()
        
        return offline_list

    def get_fields(self):
        self.sql_cur.execute("SELECT * FROM fields;")
        fields_list = self.sql_cur.fetchall()

        return fields_list

    def get_errors(self):
        self.sql_cur.execute("SELECT name, edgeID FROM errors;")
        error_list = self.sql_cur.fetchall()
        
        return error_list

    #These can both be combined into the same item, if the logic in PollingAgent is adjusted.
    def get_blacklist_web(self):
        self.sql_cur.execute("SELECT name, edgeID from blacklist;")
        blacklist = self.sql_cur.fetchall()

        return blacklist

    def get_blacklist(self):
        self.sql_cur.execute("SELECT * from blacklist;")
        templist = self.sql_cur.fetchall()

        list = []

        for item in templist:
            #Done this way in order to clear the tuple so that it's just a list of strings.
            list.append(item[0])

        return list

    def update_blacklist(self, name, edgeID, type):
        self.sql_cur.execute("INSERT IGNORE INTO blacklist(edgeID, name, type) VALUES (%s, %s, %s)", (str(edgeID), str(name), str(type)))
        self.sql_cnx.commit()

    #Offline is a list of the dicts pulled from the api. 
    def update_offline(self, offline):
        self.sql_cur.execute("TRUNCATE TABLE offline;")

        for item in offline:
            self.sql_cur.execute("INSERT INTO offline(edgeID, name, status) VALUES (%s, %s, %s)", (item["id"], item["name"], item["health"]["state"]))
        
        self.sql_cnx.commit()

    #io_list is a list of the dicts made from the API.
    def update_fields(self, io_list):
        self.sql_cur.execute("TRUNCATE TABLE fields;")

        for item in io_list:
            self.sql_cur.execute("INSERT INTO fields(edgeID, name, status, msg, isout, time) VALUES (%s, %s, %s, %s, %s, %s)", (item['id'], item['name'], item['status'], item['msg'], item['inout'], item['time']))
        
        self.sql_cnx.commit()

    #error_list is a list of the dicts made from the API.
    def update_errors(self, error_list):
        self.sql_cur.execute("TRUNCATE TABLE errors;")

        for item in error_list:
            self.sql_cur.execute("INSERT INTO errors(edgeID, name, status, msg, isout, alarm, time) VALUES (%s, %s, %s, %s, %s, %s, %s)", (item['id'], item['name'], item['status'], item['msg'], item['inout'], str(1), item['time']))
        
        self.sql_cnx.commit()

    #edgeID is a string of the edge id.
    def remove_from_blacklist(self, edgeID):
        self.sql_cur.execute("DELETE FROM blacklist WHERE edgeID = %s;", (edgeID,))
        self.sql_cnx.commit()

    def retrieve_for_alarming(self):
        self.sql_cur.execute("SELECT * FROM offline;")
        offline = (self.sql_cur.fetchall())

        self.sql_cur.execute("SELECT * FROM errors")
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