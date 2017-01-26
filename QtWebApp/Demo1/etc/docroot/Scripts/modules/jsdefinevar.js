exports.jsdefinevar = {
    defineVar : function() {
        if (typeof (window.AbstractNoScriptObject) != "undefined") {
            return window.AbstractNoScriptObject;
        }
        if (typeof (window.external) != "undefined") {
            return window.external;
        }
        if (typeof (PHP) != "undefined"
            &&
            typeof (PHP.AbstractNoScriptObject) != "undefined") {
            return PHP.AbstractNoScriptObject;
        }
        if (typeof (AbstractNoScriptObject) != "undefined") {
            return AbstractNoScriptObject;
        }
    }
};

var JsAbstractNoScriptObject = exports.jsdefinevar.defineVar();
