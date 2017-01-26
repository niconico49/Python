"""
 Enhanced version of QString for template processing. Templates
 are usually loaded from files, but may also be loaded from
 prepared Strings.
 Example template file:
 <p><code><pre>
 Hello {username}, how are you?

 {if locked}
     Your account is locked.
 {else locked}
     Welcome on our system.
 {end locked}

 The following users are on-line:
     Username       Time
 {loop user}
     {user.name}    {user.time}
 {end user}
 </pre></code></p>
 <p>
 Example code to fill this template:
 <p><code><pre>
 Template t(QFile("test.tpl"),QTextCode::codecForName("UTF-8"));
 t.setVariable("username", "Stefan");
 t.setCondition("locked",false);
 t.loop("user",2);
 t.setVariable("user0.name,"Markus");
 t.setVariable("user0.time,"8:30");
 t.setVariable("user1.name,"Roland");
 t.setVariable("user1.time,"8:45");
 </pre></code></p>
 <p>
 The code example above shows how variable within loops are numbered.
 Counting starts with 0. Loops can be nested, for example:
 <p><code><pre>
 &lt;table&gt;
 {loop row}
     &lt;tr&gt;
     {loop row.column}
         &lt;td&gt;{row.column.value}&lt;/td&gt;
     {end row.column}
     &lt;/tr&gt;
 {end row}
 &lt;/table&gt;
 </pre></code></p>
 <p>
 Example code to fill this nested loop with 3 rows and 4 columns:
 <p><code><pre>
 t.loop("row",3);

 t.loop("row0.column",4);
 t.setVariable("row0.column0.value","a");
 t.setVariable("row0.column1.value","b");
 t.setVariable("row0.column2.value","c");
 t.setVariable("row0.column3.value","d");

 t.loop("row1.column",4);
 t.setVariable("row1.column0.value","e");
 t.setVariable("row1.column1.value","f");
 t.setVariable("row1.column2.value","g");
 t.setVariable("row1.column3.value","h");

 t.loop("row2.column",4);
 t.setVariable("row2.column0.value","i");
 t.setVariable("row2.column1.value","j");
 t.setVariable("row2.column2.value","k");
 t.setVariable("row2.column3.value","l");
 </pre></code></p>
 @see TemplateLoader
 @see TemplateCache
"""

from PyQt5.QtCore import (QRegExp, QFile, QFileInfo, QIODevice, QTextCodec) 

"""
Constructor that reads the template from a string.
@param source The template source text
@param sourceName Name of the source file, used for logging
Template::Template(QString source, QString sourceName)
    : QString(source)
{
    this.sourceName = sourceName
    this.warnings = false
}

Constructor that reads the template from a file. Note that this class does not
cache template files by itself, so using this constructor is only recommended
to be used on local filesystem.
@param file File that provides the source text
@param textCodec Encoding of the source
@see TemplateLoader
@see TemplateCache
Template::Template(QFile& file, QTextCodec* textCodec)
    this.warnings = false
    sourceName = QFileInfo(file.fileName()).baseName()
    if (!file.isOpen()):
        file.open(QFile.ReadOnly | QFile.Text)

    QByteArray data = file.readAll()
    file.close()
    if (data.size() == 0 || file.error()):
        qCritical("Template: cannot read from %s, %s" % (sourceName, file.errorString()))
    else:
        append(textCodec.toUnicode(data))
"""
class Template():

    #def __init__(self, source, sourceName, file, textCodec): 
    #def __init__(self, file, textCodec): 
    def __init__(self, source, sourceName): 
        self.sourceName = sourceName 
        self.warnings = false
        """
        self.warnings = false
        sourceName = QFileInfo(file.fileName()).baseName()
        if (!file.isOpen()):
            file.open(QFile.ReadOnly | QFile.Text)

        QByteArray data = file.readAll()
        file.close()
        if (data.size() == 0 || file.error()):
            qCritical("Template: cannot read from %s, %s" % (sourceName, file.errorString()))
        else:
            append(textCodec.toUnicode(data))
        """

    """
      Replace a variable by the given value.
      Affects tags with the syntax

      - {name}

      After settings the
      value of a variable, the variable does not exist anymore,
      it it cannot be changed multiple times.
      @param name name of the variable
      @param value new value
      @return The count of variables that have been processed
    """
    def setVariable(self, name, value):
        count = 0
        variable = "{" + name + "}"
        start = indexOf(variable)
        while (start >= 0):
            replace(start, variable.length(), value)
            count++
            start = indexOf(variable, start + value.length())

        if (count == 0 && warnings):
            qWarning("Template: missing variable %s in %s" % (variable, sourceName))
        return count

    """
      Set a condition. This affects tags with the syntax

      - {if name}...{end name}
      - {if name}...{else name}...{end name}
      - {ifnot name}...{end name}
      - {ifnot name}...{else name}...{end name}

     @param name Name of the condition
     @param value Value of the condition
     @return The count of conditions that have been processed
    """
    def setCondition(self, name, value):
        count = 0
        startTag = "{if %1}" % (name)
        elseTag = "{else %1}" % (name)
        endTag = "{end %1}" % (name)
        #search for if-else-end
        start = indexOf(startTag)
        while (start >= 0):
            end = indexOf(endTag, start + startTag.length())
            if (end >= 0):
                count++
                ellse = indexOf(elseTag, start + startTag.length())
                if (ellse > start && ellse < end):
                    #there is an else part
                    if (value == true):
                        truePart = mid(start + startTag.length(), ellse - start - startTag.length())
                        replace(start, end - start+endTag.length(), truePart)
                    else:
                        #value==false
                        falsePart = mid(ellse + elseTag.length(), end - ellse - elseTag.length())
                        replace(start, end - start + endTag.length(), falsePart)
                else if (value == true):
                    #and no else part
                    truePart = mid(start + startTag.length(), end - start - startTag.length())
                    replace(start, end - start + endTag.length(), truePart)
                else:
                    #value==false and no else part
                    replace(start, end - start + endTag.length(), "")
                start = indexOf(startTag, start)
            else:
                qWarning("Template: missing condition end %s in %s" % (endTag, sourceName))

        #search for ifnot-else-end
        startTag2 = "{ifnot " + name + "}"
        start = indexOf(startTag2)
        while (start >= 0):
            end = indexOf(endTag, start + startTag2.length())
            if (end >= 0):
                count++
                ellse = indexOf(elseTag, start + startTag2.length())
                if (ellse > start && ellse < end):
                    #there is an else part
                    if (value == false):
                        falsePart = mid(start + startTag2.length(), ellse - start - startTag2.length())
                        replace(start, end - start + endTag.length(), falsePart)
                    else:
                        #value==true
                        truePart = mid(ellse + elseTag.length(), end - ellse - elseTag.length())
                        replace(start, end - start + endTag.length(), truePart)
                else if (value == false):
                    #and no else part
                    falsePart = mid(start + startTag2.length(), end - start - startTag2.length())
                    replace(start, end - start + endTag.length(), falsePart)
                else:
                    #value==true and no else part
                    replace(start, end - start + endTag.length(), "")
                start=indexOf(startTag2, start)
            else:
                qWarning("Template: missing condition end %s in %s" % (endTag, sourceName))
        if (count == 0 && warnings):
            qWarning("Template: missing condition %s or %s in %s" % (startTag, startTag2, sourceName))
        return count

    """
     Set number of repetitions of a loop.
     This affects tags with the syntax

     - {loop name}...{end name}
     - {loop name}...{else name}...{end name}

     @param name Name of the loop
     @param repetitions The number of repetitions
     @return The number of loops that have been processed
    """
    def loop(self, name, repetitions):
        Q_ASSERT(repetitions >= 0)
        count = 0
        startTag = "{loop " + name + "}"
        elseTag = "{else " + name + "}"
        endTag = "{end " + name + "}"
        #search for loop-else-end
        start = indexOf(startTag)
        while (start >= 0):
            end = indexOf(endTag, start + startTag.length())
            if (end >= 0):
                count++
                ellse = indexOf(elseTag, start + startTag.length())
                if (ellse > start && ellse < end):
                    #there is an else part
                    if (repetitions > 0):
                        loopPart = mid(start + startTag.length(), ellse - start - startTag.length())
                        insertMe
                        for (int i = 0; i < repetitions; ++i):
                            #number variables, conditions and sub-loop within the loop
                            nameNum = name + QString::number(i)
                            s = loopPart
                            s.replace("{%1." % (name), "{%1." % (nameNum))
                            s.replace("{if %1." % (name), "{if %1." % (nameNum))
                            s.replace("{ifnot %1." % (name), "{ifnot %1." % (nameNum))
                            s.replace("{else %1." % (name), "{else %1." % (nameNum))
                            s.replace("{end %1." % (name), "{end %1." % (nameNum))
                            s.replace("{loop %1." % (name), "{loop %1."% (nameNum))
                            insertMe.append(s);
                        replace(start, end - start + endTag.length(), insertMe)
                    else:
                        #repetitions==0
                        elsePart = mid(ellse + elseTag.length(), end - ellse - elseTag.length())
                        replace(start, end - start + endTag.length(), elsePart)
                else if (repetitions > 0):
                    #and no else part
                    loopPart = mid(start + startTag.length(), end - start - startTag.length())
                    insertMe
                    for (int i=0; i<repetitions; ++i):
                        #number variables, conditions and sub-loop within the loop
                        nameNum = name + QString::number(i)
                        s = loopPart
                        s.replace("{%1.") % (name), "{%1." % (nameNum))
                        s.replace("{if %1." % (name), "{if %1." % (nameNum))
                        s.replace("{ifnot %1." % (name), "{ifnot %1." % (nameNum))
                        s.replace("{else %1." % (name), "{else %1." % (nameNum))
                        s.replace("{end %1." % (name), "{end %1." % (nameNum))
                        s.replace("{loop %1." % (name), "{loop %1." % (nameNum))
                        insertMe.append(s);
                    }
                    replace(start, end - start + endTag.length(), insertMe)
                else:
                    #repetitions==0 and no else part
                    replace(start, end - start + endTag.length(), "")
                start = indexOf(startTag, start)
            else:
                qWarning("Template: missing loop end %s in %s" % (endTag, sourceName))
        if (count == 0 && warnings):
            qWarning("Template: missing loop %s in %s" % (startTag, sourceName))
        return count

    """
     Enable warnings for missing tags
     @param enable Warnings are enabled, if true
    """
    def enableWarnings(self, enable = true):
        warnings = enable
