import mysql
import mysql.connector
import logger, logging

class DataHandler():
    def __init__(self, sql_location, sql_database, sql_usr, sql_pw):
        self.database = sql_database
        self.location = sql_location
        self.user = sql_usr
        self.password = sql_pw

        self.sql_cnx = None
        self.sql_cur = None
        
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)

    # Creates all needed tables if they don't already exist and establishes the sql connection and cursor.
    def connect_to_database(self):
        self.sql_cnx = mysql.connector.connect(user=self.user, password=self.password, host=self.location, database=self.database)
        self.sql_cur = self.sql_cnx.cursor()
        # edgeID  name  status  msg   state  type       blacklist        time
        # text    text  text    text  text   input      1 = blacklisted  int
        #                                    output     0 = allowed
        #                                    appliance
        self.sql_cur.execute("CREATE TABLE IF NOT EXISTS edge(edgeID TEXT NOT NULL, name TEXT, status TEXT, msg TEXT, state TEXT, type TEXT, blacklist INT DEFAULT 0, time INT, UNIQUE(edgeID(36)));")
        self.sql_cur.execute("CREATE TABLE IF NOT EXISTS emails(address TEXT);")

        # channel   type            message     date    time
        # text      1 = No audio    text        text    text
        #           0 = No video
        self.sql_cur.execute("CREATE TABLE IF NOT EXISTS cinegy(channel TEXT NOT NULL, type INT, message TEXT, date TEXT, time TEXT)")

    # Closes the sql connection by clearing both the connection and the cursor.
    def close_connection(self):
        if self.sql_cur != None: self.sql_cnx.close()
        if self.sql_cnx != None: self.sql_cnx.close()

    def get_offline(self):
        self.sql_cur.execute("SELECT name, edgeID FROM edge WHERE status=\"missing\" AND blacklist=0;")
        offline_list = self.sql_cur.fetchall()
        
        return offline_list

    def get_fields(self):
        self.sql_cur.execute("SELECT * FROM edge WHERE (type=\"input\" OR type=\"output\") AND blacklist=0;")
        fields_list = self.sql_cur.fetchall()

        return fields_list

    # These can both be combined into the same item, if the logic in PollingAgent is adjusted.
    def get_blacklist_web(self):
        self.sql_cur.execute("SELECT name, edgeID from edge WHERE blacklist=1;")
        blacklist = self.sql_cur.fetchall()

        return blacklist

    def get_blacklist(self):
        self.sql_cur.execute("SELECT * from edge WHERE blacklist=1;")
        templist = self.sql_cur.fetchall()

        list = []

        for item in templist:
            # Done this way in order to clear the tuple so that it's just a list of strings.
            # The cursor returns items from the table as (item,).
            list.append(item[0])

        return list

    def update_blacklist(self, name, edgeID, type):
        self.sql_cur.execute("UPDATE edge SET blacklist=1 WHERE edgeID=%s", (edgeID,))
        
        self.log.info(f"Updated blacklist with item [{name}],[{edgeID}].")
        self.sql_cnx.commit()

    # edgeID is a string of the edge id.
    def remove_from_blacklist(self, edgeID):
        self.sql_cur.execute("UPDATE edge SET blacklist=0 WHERE edgeID=%s", (edgeID,))
        self.log.info(f"Removed [{edgeID}] from blacklist.")
        self.sql_cnx.commit()

    def retrieve_for_alarming(self):
        self.sql_cur.execute("SELECT name, edgeID FROM edge WHERE type=\"appliance\" AND status=\"missing\" AND blacklist=0;")
        offline = (self.sql_cur.fetchall())
        
        self.sql_cur.execute("SELECT name, edgeID FROM edge WHERE status LIKE '%rror%' AND blacklist=0")
        erroring = (self.sql_cur.fetchall())

        return (offline, erroring)
    
    def get_emails(self):
        self.sql_cur.execute("SELECT * FROM emails;")
        templist = self.sql_cur.fetchall()

        emails = []

        for item in templist:
            # Done this way in order to clear the tuple so that it's just a list of strings.
            # Data is returned from the cursor as (email,).
            emails.append(item[0])
        
        return emails
    
    def add_email(self, address):
        self.sql_cur.execute("INSERT INTO emails(address) VALUES (%s)", (address,))
        self.sql_cnx.commit()

        self.log.info(f"Added email address {address}.")

    def remove_email(self, address):
        self.sql_cur.execute("DELETE FROM emails WHERE address = %s;", (address,))
        self.sql_cnx.commit()
        self.log.info(f"Removed email address {address}.")

    def update_table(self, io_list):
        for item in io_list:
            self.sql_cur.execute("INSERT INTO edge(edgeID, name, status, msg, type, time) VALUES(%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=%s, status=%s, msg=%s, time=%s", 
                                 (item["id"], item["name"], item["status"], item["msg"], item["type"], item["time"], item["name"], item["status"], item["msg"], item["time"]))
            
        self.sql_cnx.commit()
    
    def get_edgeIDs(self):
        self.sql_cur.execute("SELECT edgeID from edge")
        ids = self.sql_cur.fetchall()

        return ids
    
    def delete_edgeID(self, edgeID):
        self.sql_cur.execute("DELETE from edge WHERE edgeID=%s", (edgeID,))
        self.sql_cnx.commit()

    def remove_cinegy_alert(self, channel):
        self.sql_cur.execute("DELETE FROM cinegy WHERE channel=%s", (channel,))
        self.sql_cnx.commit()
        self.log.warning(f"CINEGY ALERT ON {channel} CLEARED")

    def add_cinegy_alert(self, channel, mtype, message, date, time):
        self.sql_cur.execute("INSERT INTO cinegy VALUES(%s, %s, %s, %s, %s)", (channel, mtype, message, time, date))
        self.sql_cnx.commit()
        self.log.warning(f"CINEGY ALERT ON CHANNEL {channel}: {message}")