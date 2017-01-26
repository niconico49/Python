exports.jsmain = {
    // WAKE ON LAN - MAGIC PACKET SENDER
    // MAC ADDRESS LIST
    // Description,MAC Address
    // Example:
    // My PC,A1:B2:C3:D4:E5:F6
    jsGuide : [
        {
            PC_NAME : "DEVELOPMENT-PC",
            MAC_ADDRESS : "00:21:97:83:DE:B6"
        },    
        {
            PC_NAME : "DEVELOPMENT-01 (NICO)",
            MAC_ADDRESS : "98:90:96:C4:60:C5"
        },    
        {
            PC_NAME : "WORKSTATION-1 (FABIO)",
            MAC_ADDRESS : "C8:9C:DC:2B:87:40"
        },    
        {
            PC_NAME : "WORKSTATION-4 (ALVARO)",
            MAC_ADDRESS : "90:1B:0E:28:C2:A8"
        },    
        {
            PC_NAME : "WORKSTATION-3 (STEFANIA)",
            MAC_ADDRESS : "00:21:97:9D:AD:F2"
        },
        {
            PC_NAME : "WORKSTATION-5 (MARZIA)",
            MAC_ADDRESS : "64:00:6A:33:47:A6"
        },
        {
            PC_NAME : "WORKSTATION-6 (RECEPTION)",
            MAC_ADDRESS : "00:25:11:69:8A:A8"
        },
        {
            PC_NAME : "COMMERCIALE-2",
            MAC_ADDRESS : "3C:D9:2B:61:D0:A1"
        },
        {
            PC_NAME : "COMMERCIALE-3",
            MAC_ADDRESS : "3C:D9:2B:62:8C:5D"
        },
        {
            PC_NAME : "COMMERCIALE-4 (ALESSIO-PIERFRANCESCO)",
            MAC_ADDRESS : "3C:D9:2B:62:8A:E3"
        },
        {
            PC_NAME : "COMMERCIALE-5",
            MAC_ADDRESS : "2C:41:38:8C:7E:AD"
        },
        {
            PC_NAME : "CONFERENCE-PC (PORTATILE DELL)",
            MAC_ADDRESS : "5C:26:0A:40:24:80"
        },
        {
            PC_NAME : "UBUNTU64-01 (OLD VIDEO-SORVEGLIANZA)",
            MAC_ADDRESS : "C8:9C:DC:28:D9:C7"
        },
        {
            PC_NAME : "UBUNTU64-02 (OLD WORKSTATION-6 (RECEPTION))",
            MAC_ADDRESS : "00:25:11:69:8A:A8"
        },
        {
            PC_NAME : "UBUNTU64-03 (OLD WORKSTATION-2 (MARZIA))",
            MAC_ADDRESS : "00:21:97:9D:AB:10"
        }
    ],

    //ups-server.blt-enterprise.local (192.168.1.89)
    //bcksrv.blt-enterprise.local (192.168.1.92)
    //bltserver-01.blt-enterprise.local (192.168.1.98)
    //bltserver-02.blt-enterprise.local (192.168.1.99)

    populate : function(id) {
        var element = document.getElementById(id);
        element.innerHTML = "";
        for (var i = 0; i < this.jsGuide.length; i++) {
            var item = this.jsGuide[i];
            var pcName = item.PC_NAME;
            var macAddress = item.MAC_ADDRESS;
            var checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.name = "chkList";
            //checkbox.name = "nick";
            checkbox.value = macAddress;
            element.appendChild(checkbox);
            var label = document.createElement('label')
            label.htmlFor = pcName;
            label.appendChild(document.createTextNode(pcName));

            element.appendChild(label);
            element.appendChild(document.createElement("br"));    
        }
/*    
        //var JsAbstractNoScriptObject = defineVar();
        setInterval(
            function() {
                JsAbstractNoScriptObject.getComponentDevelopment().displayValue("ok");
            },
            3000
        );
*/    
        //var jswebconnection = exports.jswebconnection;
        //alert(JSON.stringify(jswebconnection.parseParams(jswebconnection.getQueryString(window.location.href))));
    },

    toggle : function(source) {
        $("input[name='chkList']").each(function() {
            this.checked = source.checked;
        });    
    },

    listChecked : function() {
        var elements = [];
        $("input[name='chkList']").each(function() {
            if (this.checked) {
                elements.push(this.value);
            }
        });    
        return elements;
    }, 

    wakeOnLan : function() {
        var macAddressList = this.listChecked();
        if (macAddressList.length == 0) {
            alert("select a pc");
            return;
        }
        //alert(macAddressList);
        var jswebconnection = exports.jswebconnection;
        var jsonData = {
            ID_METHOD: "WakeOnLan.wakeOnLan",
            PARAMS: {
                MAC_ADDRESSES: macAddressList
            }
        };
        //alert(macAddressList);
/*
        var JsAbstractNoScriptObject = defineVar();
        
        //var JsAbstractNoScriptObject = window.AbstractNoScriptObject;
        //alert(JsAbstractNoScriptObject.getComponentDevelopment());
        
        JsAbstractNoScriptObject.getComponentDevelopment().displayValue(macAddressList);
        var jsComponentRequestResponse = JsAbstractNoScriptObject.getComponentRequestResponse();
        var request = jsComponentRequestResponse.getRequest();
        var response = request + " RESPONSE";
        //alert(response);
        jsComponentRequestResponse.setResponse(response);
*/    
        jswebconnection.ajaxCall(jsonData, function (data) {
            alert(JSON.stringify(data));
            var id = "resultMsg";
            var element = document.getElementById(id);
            element.innerHTML += data + "<br/>\n";
            //alert(data);
        });
    }
};

var jsmain = exports.jsmain;