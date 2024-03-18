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

        #error_list is a list of all Edge outputs that are reporting back an error.
        self.error_list = []

        #offline_list is a bit more complicated as Edge does not throw an error when 
        #a device is offline. Given that, the program needs to track what devices are 
        #online, and then alarm when a device that was online is no longer online.
        self.offline_list = []

        self.blacklist = []

    def set_blacklist(self, blacklist):
        self.blacklist = blacklist

    def pull_info(self):
        with requests.Session() as s:
            r = s.post(url = self.edge_url + "api/login/", json = self.info)

            key = r.content.decode('utf-8')

            key = json.loads(key)
            #print("SESSION INFO: ")
            #print(json.dumps(key, indent=2))

            r = s.get(url = self.edge_url + "api/region/")

            region_info = r.content.decode('utf-8')
            region_info = json.loads(region_info)

            #print("\nREGION INFO: ")
            for element in region_info["items"]:
                region_id = element["id"]

                r = s.get(url = self.edge_url + "api/region/" + region_id)
                sub_region = r.content.decode("utf-8")
                sub_region = json.loads(sub_region)
                #print(json.dumps(sub_region, indent = 2))

            r = s.get(url = self.edge_url + "api/input/")
            inputs = r.content.decode('utf-8')
            inputs = json.loads(inputs)
            now = time.time()

            #print("\nINPUTS: ")
            for item in inputs['items']:
                temp = {
                    "name":item['name'],
                    "status":item['health']['state'],
                    "msg":item['health']['title'],
                    "id":item['id'],
                    "inout": 0,
                    "time":now
                }
                #print(item['name'] + " | " + item['health']['state'] + " | " + item['health']['title'])
                self.io_list.append(temp)

            r = s.get(url = self.edge_url + "api/output/")

            outputs = r.content.decode('utf-8')
            outputs = json.loads(outputs)

            #print("\nOUTPUTS: ")
            for output in outputs["items"]:

                temp = {
                    "name":output['name'],
                    "status":output['health']['state'],
                    "msg":output['health']['title'],
                    "id":output['id'],
                    "inout":1,
                    "time":now
                }
                #print(output['name'] + " | " + output['health']['state'] + " | " + output['health']['title'])
                self.io_list.append(temp)

            r = s.get (url = self.edge_url + "api/appliance/")
            appliances = r.content.decode('utf-8')
            appliances = json.loads(appliances)
            appliances = appliances["items"]

            self.offline_list = []

            for item in appliances:
                status = item["health"]["state"]

                if (status != "connected" and item['id'] not in self.blacklist):
                    self.offline_list.append(item)
                #Have to compare by value, not by reference. Cannot use "and item not in blacklist".

            #Log out
            r = s.post(url = self.edge_url + "api/logout/", json = key)

            #parse for errors
            for item in self.io_list:
                #allOk is the default "good" status response. Anything else has some form of alarm or error.
                if ("alarm" in str(item['status']).lower() and item['id'] not in self.blacklist):
                    self.error_list.append(item)

            return (self.offline_list, self.io_list, self.error_list)