class AlertManager():
    def __init__(self):
        self.alarm_ids = []
        self.current_alarming = {}

    def parse_for_alarms(self, alarm_list):
        body_text = ""
        for item in alarm_list:
            #Unpacking the tupple into usable variables
            #This program operates under the assumption that the edgeID is the first
            #value stored in the database.
            edgeid, *temp = item
            if (edgeid not in self.alarm_ids): self.alarm_ids.append(edgeid)

            if (edgeid in self.current_alarming):
                self.current_alarming[edgeid] = self.current_alarming[edgeid] + 1
                ticks = self.current_alarming[edgeid]
                
                #This is a hacky solution to introcude a delay between alarms being sent. As the api is polled
                #approximately every ten seconds, having the alarm check execute every 12 and 24 polling cycles 
                #means that an alarm will be sent two minutes after the alarm is detected, and four minutes after
                #the alarm is detected.
                if ticks == 12 or ticks == 24:
                    if (body_text == ""): body_text = "Offline Device(s):"
                    body_text = body_text + "\n" + str(item[1])
            
            else:
                self.current_alarming[edgeid] = 0
            
        return body_text

    def check_alarms(self, offline, erroring):
        body_text = ""

        if (len(offline) != 0): body_text = body_text + self.parse_for_alarms(offline)
        if (len(erroring) != 0): body_text = body_text + self.parse_for_alarms(erroring)

        poplist = []

        for item in self.current_alarming:
            if (item not in self.alarm_ids):
                poplist.append(item)

        for item in poplist:
            #body_text = body_text + f"\nCleared: {item}"
            self.current_alarming.pop(item)

        #print("\nCurrent alarming: " + str(self.current_alarming))
        #print("\nAlarm IDs: " + str(self.alarm_ids))

        if (body_text != ""):
            return body_text
        else:
            return None