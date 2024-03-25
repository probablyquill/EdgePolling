//Retrieve data from server via /get_data GET request.
function getData() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var data = JSON.parse(this.response)
            createTable(data['offline'], data['errors'], data['blacklist'], data['emails']);
        }
    }
    xhttp.open("GET", "get_data", true);
    xhttp.send();
}

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

function deleteBlacklist() {
    var edgeID = document.getElementById("edge-id-input");
    
    if (edgeID.value != "" && edgeID.value != null) {
        removeFromBlacklist(edgeID.value);
        sendUpdateRequest("remove_from_blacklist", edgeID.value);

        edgeID.value = "";
    }
}

function addBlacklist() {
    var edgeID = document.getElementById("edge-id-input");
    var edgeName = document.getElementById("name-input");

    if (edgeID.value != "" && edgeID.value != null) {
        if (edgeName.value != "" && edgeName.value != null) {
            sendUpdateRequest("add_to_blacklist", [edgeName.value, edgeID.value, "blacklist"]);
        
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
    }
}

function deleteEmail() {
    var addressElement = document.getElementById("email-address");

    if (addressElement.value != "" && addressElement.value != null) {
        sendUpdateRequest("delete_email", addressElement.value);
        addressElement.value = "";
    }
}

//This is horrible and I hate it and I'm sorry I wrote it but it works
//This is definitely some kind of crime somewhere.
function createTable(offline, errors, blacklist, emails) {

    var body = document.getElementById("data-table");
    var headerList = ["Offline:", "Errors:", "Blacklist:"];
    var headerCommands = ["add_to_blacklist", "add_to_blacklist", "remove_from_blacklist"];
    var itemList = [offline, errors, blacklist];

    while (body.hasChildNodes()) body.firstChild.remove();

    for (var l = 0; l < headerList.length; l++) {
        var newRow = document.createElement("tr");
        newRow.classList.add('divider');
        var labelOne = document.createElement("th");
        var labelOneText = document.createTextNode(headerList[l]);
        var labelTwo = document.createElement("th");
        var labelTwoText = document.createTextNode("Edge ID:");
        var tableHeader = document.createElement("thead");
        var blankSpace = document.createElement("th") 

        labelOne.appendChild(labelOneText);
        newRow.appendChild(labelOne);

        labelTwo.appendChild(labelTwoText);
        newRow.appendChild(labelTwo);

        newRow.appendChild(blankSpace)

        tableHeader.appendChild(newRow);
        body.appendChild(tableHeader);

        var tableBody = document.createElement("tbody");
        
        //Loops through provided array of arrays and populates the table accordingly.
        for (var i = 0; i < itemList[l].length; i++) {

            //I'd like to thank ChatGPT for explaining IIFE in a way I could understand.
            (function(items, currentI, currentL, headerCommands) {
                var newLine = document.createElement("tr");
                var newCell = document.createElement("td");
                var newCellText = document.createTextNode(items[currentL][currentI][0]);
                var newCell2 = document.createElement("td");
                var newCellText2 = document.createTextNode(items[currentL][currentI][1]);
    
                var newCell3 = document.createElement("td");
                var newCellImage = document.createElement("img");
                
                newCellImage.classList.add('table-image');
                newCellImage.onclick = function(){
                    sendUpdateRequest(headerCommands[currentL], [items[currentL][currentI][0], items[currentL][currentI][1], "button"]);
                };

                newCell.appendChild(newCellText);
                newCell2.appendChild(newCellText2);

                if (currentL != 2 && items[currentL][currentI][0] != "None") {
                    newCellImage.src = "/static/plus.png";
                    newCell3.appendChild(newCellImage);
                    newCell3.classList.add("table-item");
                } else if (items[currentL][currentI][0] != "None") {
                    newCellImage.src = "/static/minus.png";
                    newCell3.appendChild(newCellImage);
                    newCell3.classList.add("table-item");
                }
    
                newLine.appendChild(newCell);
                newLine.appendChild(newCell2);
                newLine.appendChild(newCell3);
                newLine.classList.add('element');
    
                tableBody.appendChild(newLine);
            //ToFix: itemlist doesn't need to be present in every single iteration. It can either be stored 
            //outside of the scope of the function or somewhere else I'll figure it out later.
            })(itemList, i, l, headerCommands);
        }

        body.appendChild(tableBody);
    }

    //One last time for the email list
    var body = document.getElementById("email-table");

    //Yeah I kill children
    while (body.hasChildNodes()) body.firstChild.remove();

    var newRow = document.createElement("tr");
    newRow.classList.add('divider');
    var labelOne = document.createElement("th");
    var labelOneText = document.createTextNode("Emails:");
    var tableHeader = document.createElement("thead");    
    var blankSpace = document.createElement("th");

    labelOne.appendChild(labelOneText);
    newRow.appendChild(labelOne);
    newRow.appendChild(blankSpace);

    tableHeader.appendChild(newRow);
    body.appendChild(tableHeader);

    var tableBody = document.createElement("tbody");

    for (var i = 0; i < emails.length; i++) {
        (function(savedI, savedEmails) {
            console.log(savedEmails[0]);
            var newLine = document.createElement("tr");
            var newCell = document.createElement("td");
            var newCellText = document.createTextNode(savedEmails[savedI]);
            var newCell2 = document.createElement("td");
            newCell2.classList.add("table-item");
            var newCellImage = document.createElement("img");
            newCellImage.classList.add('table-image');
            newCellImage.src = "/static/minus.png";

    
            newCellImage.onclick = function() {
                sendUpdateRequest("delete_email", savedEmails[savedI]);
            };

            newCell.appendChild(newCellText);
            newCell2.appendChild(newCellImage);
            newLine.appendChild(newCell);
            newLine.appendChild(newCell2);
    
            newLine.classList.add('element');
            newLine.classList.add('inner');
    
            tableBody.appendChild(newLine);
        })(i, emails);
    }

    body.appendChild(tableBody);

}