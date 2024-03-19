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

//I will need to look later, but addToBlacklist, addToEmail, and removeEmail can probably all be
//consolidated into one function.
function addToBlacklist(name, edgeId) {
    var xhttp = new XMLHttpRequest();

    var dataToSend = JSON.stringify({"add_to_blacklist":[name, edgeId, "blacklisted"]})

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            getData();
        }
    }

    xhttp.open("POST", "send_data", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(dataToSend);
}

function addToEmail(address) {
    var xhttp = new XMLHttpRequest();

    var dataToSend = JSON.stringify({"add_email":address})

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            getData();
        }
    }

    xhttp.open("POST", "send_data", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(dataToSend);
}

function delete_email(address) {
    var xhttp = new XMLHttpRequest();

    var dataToSend = JSON.stringify({"delete_email":address})

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            getData();
        }
    }

    xhttp.open("POST", "send_data", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(dataToSend);
}

function removeFromBlacklist(edgeId) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            getData();
        }
    }

    var dataToSend = JSON.stringify({"remove_from_blacklist":edgeId})

    xhttp.open("POST", "send_data", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(dataToSend);
}

//This is horrible and I hate it and I'm sorry I wrote it but it works
function createTable(offline, errors, blacklist, emails) {

    var body = document.getElementById("data-table");
    var headerList = ["Offline:", "Errors:", "Blacklist"];
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

        labelOne.appendChild(labelOneText);
        newRow.appendChild(labelOne);

        labelTwo.appendChild(labelTwoText);
        newRow.appendChild(labelTwo);

        tableHeader.appendChild(newRow);
        body.appendChild(tableHeader);

        var tableBody = document.createElement("tbody");
        
        //Loops through provides array of arrays and populates the table accordingly.
        for (var i = 0; i < itemList[l].length; i++) {
            var newLine = document.createElement("tr");
            var newCell = document.createElement("td");
            var newCellText = document.createTextNode(itemList[l][i][0]);
            var newCell2 = document.createElement("td");
            var newCellText2 = document.createTextNode(itemList[l][i][1]);

            newCell.appendChild(newCellText);
            newCell2.appendChild(newCellText2);

            newLine.appendChild(newCell);
            newLine.appendChild(newCell2);
            newLine.classList.add('element');
            
            //Some logic thrown in to make it look nice. Dashed line in between
            //elements will only be put in on the non-last element unless it's 
            //the last set of elements.
            if (i != itemList[l].length - 1 || l == itemList.length - 1) {
                newLine.classList.add('inner');
            }

            tableBody.appendChild(newLine);
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

    labelOne.appendChild(labelOneText);
    newRow.appendChild(labelOne);

    tableHeader.appendChild(newRow);
    body.appendChild(tableHeader);

    var tableBody = document.createElement("tbody");

    for (var i = 0; i < emails.length; i++) {
        var newLine = document.createElement("tr");
        var newCell = document.createElement("td");
        var newCellText = document.createTextNode(emails[i]);

        newCell.appendChild(newCellText);
        newLine.appendChild(newCell);

        newLine.classList.add('element');
        newLine.classList.add('inner');

        tableBody.appendChild(newLine);
    }

    body.appendChild(tableBody);

}

function deleteBlacklist() {
    var edgeID = document.getElementById("edge-id-input");
    
    if (edgeID.value != "" && edgeID.value != null) {
        removeFromBlacklist(edgeID.value);

        edgeID.value = "";
    }
}

function addBlacklist() {
    var edgeID = document.getElementById("edge-id-input");
    var edgeName = document.getElementById("name-input");

    if (edgeID.value != "" && edgeID.value != null) {
        if (edgeName.value != "" && edgeName.value != null) {
            addToBlacklist(edgeName.value, edgeID.value);
        
            edgeID.value = "";
            edgeName.value = "";
        }
    }
}

function addEmail() {
    var addressElement = document.getElementById("email-address");

    if (addressElement.value != "" && addressElement.value != null) {
        addToEmail(addressElement.value)
        addressElement.value = "";
    }
}

function deleteEmail() {
    var addressElement = document.getElementById("email-address");

    if (addressElement.value != "" && addressElement.value != null) {
        delete_email(addressElement.value)
        addressElement.value = "";
    }
}