import requests
import json
import time

class EdgeAPIPolling():
    def __init__(self, edge_user, edge_key, edge_url):
        self.edge_user = edge_user
        self.edge_key = edge_key
        self.edge_url = edge_url

        #Formatted for POST request to EdgeAPI for user authentication.
        self.info = {
            'username':self.edge_user,
            'password':self.edge_key
        }

        #io_list is a list of all inputs and outputs currently seen in the Edge API.
        self.io_list = []


        #offline_list is a bit more complicated as Edge does not throw an error when 
        #a device is offline. Given that, the program needs to track what devices are 
        #online, and then alarm when a device that was online is no longer online.
        self.appliance_list = []

        self.blacklist = []

    def set_blacklist(self, blacklist):
        self.blacklist = blacklist

    def pull_info(self):
        
        # Creates two lists that contain information retrieved from the edge API. 
        # The returned lists are a list of appliances pulled from Edge, and a list of 
        # inputs and outputs. Both lists use dicts that contain the name, device id, status, type, and 
        # whatever message is included. 
        with requests.Session() as s:
            r = s.post(url = self.edge_url + "api/login/", json = self.info)

            key = r.content.decode('utf-8')

            key = json.loads(key)

            r = s.get(url = self.edge_url + "api/region/")

            region_info = r.content.decode('utf-8')
            region_info = json.loads(region_info)

            for element in region_info["items"]:
                region_id = element["id"]

                r = s.get(url = self.edge_url + "api/region/" + region_id)
                sub_region = r.content.decode("utf-8")
                sub_region = json.loads(sub_region)

            r = s.get(url = self.edge_url + "api/input/")
            inputs = r.content.decode('utf-8')
            inputs = json.loads(inputs)
            now = time.time()

            for item in inputs['items']:
                temp = {
                    "name":item['name'],
                    "status":item['health']['state'],
                    "msg":item['health']['title'],
                    "id":item['id'],
                    "type":"input",
                    "time":now
                }

                self.io_list.append(temp)

            r = s.get(url = self.edge_url + "api/output/")

            outputs = r.content.decode('utf-8')
            outputs = json.loads(outputs)

            for output in outputs["items"]:

                temp = {
                    "name":output['name'],
                    "status":output['health']['state'],
                    "msg":output['health']['title'],
                    "id":output['id'],
                    "type":"output",
                    "time":now
                }

                self.io_list.append(temp)

            r = s.get (url = self.edge_url + "api/appliance/")
            appliances = r.content.decode('utf-8')
            appliances = json.loads(appliances)
            appliances = appliances["items"]

            self.appliance_list = []

            for item in appliances:
                appliance_info = {
                    "id":item["id"],
                    "name":item["name"],
                    "status":item["health"]["state"],
                    "msg":item["health"]["title"],
                    "type":"appliance",
                    "time":now
                }

                self.appliance_list.append(appliance_info)

            #Log out
            r = s.post(url = self.edge_url + "api/logout/", json = key)

            return (self.appliance_list + self.io_list)