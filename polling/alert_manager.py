import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

alarm_ids = []
current_alarming = {}

# Alert manager is by far the worst part of this program and needs to be reworked. 
# For the moment it has been changed to no longer be an object as there were no benefits to it being a Class.
def parse_for_alarms(alarm_list, blacklist):
    body_text = ""
    for item in alarm_list:
        # Unpacking the tupple into usable variables
        # This program operates under the assumption that the edgeID is the first
        # value stored in the database.
        name, edgeid = item

        if (edgeid in blacklist): continue

        if (edgeid not in alarm_ids): alarm_ids.append(edgeid)

        if (edgeid in current_alarming):
            current_alarming[edgeid] = current_alarming[edgeid] + 1
            ticks = current_alarming[edgeid]
            
            # This is a hacky solution to introcude a delay between alarms being sent. As the api is polled
            # approximately every ten seconds, having the alarm check execute every 12 and 24 polling cycles 
            # means that an alarm will be sent two minutes after the alarm is detected, and four minutes after
            # the alarm is detected.
            if ticks == 12 or ticks == 24:
                if (body_text == ""): body_text = "Offline Device(s):"
                body_text = body_text + "\n" + str(name)
                log.info(f"[{name}] FLAGGED FOR ALARM")
        
        else:
            current_alarming[edgeid] = 0
        
    return body_text

def check_alarms(offline, erroring, blacklist):
    body_text = ""

    if (len(offline) != 0): body_text = body_text + parse_for_alarms(offline, blacklist)
    if (len(erroring) != 0): body_text = body_text + parse_for_alarms(erroring, blacklist)

    poplist = []

    for item in current_alarming:
        if (item not in alarm_ids):
            poplist.append(item)

    for item in poplist:
        current_alarming.pop(item)
        log.info(f"CLEARED ALERT ON {item}")
        
    if (body_text != ""):
        return body_text
    else:
        return None