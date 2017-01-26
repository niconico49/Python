exports.jswebconnection = {
    config : {
        FN_RESTFUL: "RESTful",
        FN_NET: ".Net",
        FN_JAVA: "Java",
        FN_PHP: "PHP",
        FN_PYTHON: "Python",
        FN_PERL: "Perl"
    },
    
    formatDataRequest : function (language, jsonData, serverListener) {
        var result = "";

        switch (language) {
            case this.config.FN_NET:
                if (serverListener == this.config.FN_RESTFUL) {
                    //.net 4.0???
                    //result = { '': JSON.stringify(jsonData) };
                    //.net 4.5???
                    result = JSON.stringify(jsonData);
                }
                else {
                    result = "{\"jsonData\": '" + JSON.stringify(jsonData) + "'}";
                }
                break;
            case this.config.FN_JAVA:
                result = JSON.stringify(jsonData);
                break;
            case this.config.FN_PHP:
                result = {
                    jsonData: JSON.stringify(jsonData)
                };
                break;
            case this.config.FN_PYTHON:
            case this.config.FN_PERL:
                result = {
                    jsonData: JSON.stringify(jsonData)
                };
                result = JSON.stringify(result);
                break;
        }
        return result;
    },

    formatHeaders : function (language, serverListener) {
        var result = {};

        var contentType = "text/plain; charset=utf-8";

        switch (language) {
            case this.config.FN_NET:
                if (serverListener != this.config.FN_RESTFUL) {
                    contentType = "application/json; charset=utf-8";
                }
                result = {
                    Accept: contentType,
                    "Content-Type": contentType
                };
                break;
            case this.config.FN_JAVA:
                result = {
                    Accept: contentType,
                    "Content-Type": contentType
                };
                break;
            case this.config.FN_PYTHON:
            case this.config.FN_PERL:
                contentType = "application/json; charset=utf-8";
                result = {
                    Accept: contentType,
                    "Content-Type": contentType
                };
                break;
        }
/*
        var contentType = "text/plain; charset=utf-8";

        if (language == this.config.FN_NET
            &&
            serverListener != this.config.FN_RESTFUL
            ) {
            contentType = "application/json; charset=utf-8";
        }
        result = {
            Accept: contentType,
            "Content-Type": contentType
        };
*/
        return result;
    },

    formatDataResponse : function (language, data, serverListener) {
        var result = "";
        switch (language) {
            case this.config.FN_NET:
                if (serverListener == this.config.FN_RESTFUL) {
                    result = JSON.parse(JSON.parse(data));
                }
                else {
                    result = JSON.parse(data.d);
                }
                break;
            case this.config.FN_JAVA:
            case this.config.FN_PHP:
            case this.config.FN_PYTHON:
            case this.config.FN_PERL:
                //result = JSON.parse(Iuppiter.decompress(data.split(",")));
                //data = Iuppiter.decompress(Iuppiter.Base64.decode(Iuppiter.toByteArray(data), true));
                //data = Iuppiter.decompress(data.split(","));
                result = JSON.parse(data);
                //result = eval(data);
                break;
        }
        return result;
    },

    ajaxCallWithUrl : function (url, jsonData, successFunction) {
        var self = this;
        // var languageType = Session["LANGUAGE_PROGRAMMING"];
        // var serverListenerType = Session["WEB_SERVICE_TYPE"];
        var languageType = "Java";
        var serverListenerType = "Classic";

        //jsonData.LOCATION = Session.LOCATION;
        jsonData.LOCATION = {
            PROTOCOL: "http",
            HOST: "127.0.0.1",
            PORT: "7777",
            PATHNAME: "EasyWakeOnLan"
        };
        //$.support.cors = true;
        //alert(url + " " + JSON.stringify(jsonData));
        $.ajax({
            type: "POST",
            url: url,
            data: this.formatDataRequest(languageType, jsonData, serverListenerType),
            headers: this.formatHeaders(languageType, serverListenerType),
            dataType: "text",
            /*
                    headers: { 'Access-Control-Allow-Origin': '*' }
                    //contentType: self.formatContentType(languageType, serverListenerType),
                    dataType: "json",
                    dataType: "text",
                    dataFilter: function (data) {
                        var response = typeof (JSON) !== "undefined" && typeof (JSON.parse) === "function" ? JSON.parse(data) : val("(" + data + ")");
                        return response.hasOwnProperty("d") ? response.d : response;
                    },
            */
            success: function (data) {
                //data = data.hasOwnProperty("d") ? JSON.parse(data.d) : eval(data);
                //alert(JSON.stringify(data));
                successFunction(data);
/*                
                var dataResponse = self.formatDataResponse(languageType, data, serverListenerType);
                
                switch(true) {
                    case dataResponse.hasOwnProperty("redirectPage") && dataResponse.redirectPage.length > 0:
                        Master.reload(dataResponse.redirectPage);
                        break;

                    case dataResponse.hasOwnProperty("redirectPageExternal") && dataResponse.redirectPageExternal.length > 0:
                        document.location.href = dataResponse.redirectPageExternal;
                        break;

                    default :
                        successFunction(dataResponse);
                }
*/                
    /*            
                if (dataResponse.hasOwnProperty("redirectPage") && dataResponse.redirectPage.length > 0) {
                    Master.reload(dataResponse.redirectPage);
                    //document.location.href = dataResponse.redirectPage;
                }
                else {
                    if (dataResponse.hasOwnProperty("redirectPageExternal") && dataResponse.redirectPageExternal.length > 0) {
                        //Master.reload(dataResponse.redirectPage);
                        document.location.href = dataResponse.redirectPageExternal;
                    }
                    else {
                        successFunction(dataResponse);
                    }
                }
    */
            },
            error: function (e) {
                alert("error ==> by url " + url + " " + JSON.stringify(jsonData) + "\n" + JSON.stringify(e));
                //alert("error ==> " +  JSON.stringify(e));
                //$("#divResult").html("WebSerivce unreachable");
            }
        });
    },

    ajaxCall : function (jsonData, successFunction) {
        //var urlWebServicePath = Session["URL_WEB_SERVICE_PATH"];
        //var urlWebServicePath = "http://127.0.0.1:7777/EasyWakeOnLan/webresources/api/execute";
        var urlWebServicePath = "http://127.0.0.1:8080/webresources/api/execute";
        this.ajaxCallWithUrl(urlWebServicePath, jsonData, successFunction);
    },

    arrayReplacement : function (data, prefix, array2Find) {
        for (var key in data) {
            for (var i = 0; i < array2Find.length; i++) {
                data[key] = data[key].replace(array2Find[i], prefix + array2Find[i]);
            }
        }
    },

    getQueryString : function (value) {
        return value.substring(value.search("\\?") + 1);
    },

    parseParams : function (queryString) {
        var params = {},
            e,
            a = /\+/g,  // Regex for replacing addition symbol with a space
            r = /([^&=]+)=?([^&]*)/g,
            d = function (s) {
                return decodeURIComponent(s.replace(a, " "));
            };

        while (e = r.exec(queryString)) {
            params[d(e[1])] = d(e[2]);
        }

        return params;
    }
};
