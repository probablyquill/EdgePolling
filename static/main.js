//Sends a POST request formated as "request_type": data.
function sendUpdateRequest(request_type, data) {
    var xhttp = new XMLHttpRequest();
    
    //You cannot directly feed stringify a string object to use as the key, so you have 
    //to create an object with a key-value pair and then give it to jsonify.
    var containerObj = {}
    containerObj[request_type] = data;
    dataToSend = JSON.stringify(containerObj);

    //"delete_from_blacklist": "edgeID"
    //"add_to_blacklist": ["name", "edgeID", "any string"]
    //"add_email":"email"
    //"delete_email":"email"

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            //Runs getData to update tables after the post request has been processed.
            getData();
        }
    }

    xhttp.open("POST", "send_data", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(dataToSend);
}

function deleteBlacklist(value) {
    var edgeID = value
    if (edgeID != "" && edgeID != null) {
        sendUpdateRequest("remove_from_blacklist", edgeID);
    }
}

function addBlacklist(name, value) {
    var edgeID = value
    var edgeName = name

    if (edgeID != "" && edgeID != null) {
        if (edgeName != "" && edgeName != null) {
            sendUpdateRequest("add_to_blacklist", [edgeName, edgeID, "blacklist"]);
        
            edgeID.value = "";
            edgeName.value = "";
        }
    }
}
function addEmail() {
    var addressElement = document.getElementById("email-address");
    if (addressElement.value != "" && addressElement.value != null) {
        sendUpdateRequest("add_email", addressElement.value);
        addressElement.value = "";
        if (addressElement != "" && addressElement != null) {
            sendUpdateRequest("add_email", addressElement);
        }
    }
}

function deleteEmail(address) {
    var addressElement = address;

    if (addressElement != "" && addressElement != null) {
        sendUpdateRequest("delete_email", addressElement);
    }
}

function getData() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var data = this.response;
            var table = document.getElementById("data-table");

            table.innerHTML = data;
        }
    }
    xhttp.open("GET", "get_data", true);
    xhttp.send();
}