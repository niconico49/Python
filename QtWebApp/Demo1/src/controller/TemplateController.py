#include "httprequest.h"
#include "httpresponse.h"
#include "httprequesthandler.h"

/**
  This controller generates a website using the template engine.
  It generates a Latin1 (ISO-8859-1) encoded website from a UTF-8 encoded template file.
*/

class TemplateController : public HttpRequestHandler {
    Q_OBJECT
    Q_DISABLE_COPY(TemplateController)
public:

    /** Constructor */
    TemplateController();

    /** Generates the response */
    void service(HttpRequest& request, HttpResponse& response);
};

#include "templatecontroller.h"
#include "templatecache.h"
#include "template.h"

/** Cache for template files */
extern TemplateCache* templateCache;

TemplateController::TemplateController()
{}

void TemplateController::service(HttpRequest& request, HttpResponse& response)
{
    response.setHeader("Content-Type", "text/html; charset=ISO-8859-1");

    Template t=templateCache->getTemplate("demo",request.getHeader("Accept-Language"));
    t.enableWarnings();
    t.setVariable("path",request.getPath());

    QMap<QByteArray,QByteArray> headers=request.getHeaderMap();
    QMapIterator<QByteArray,QByteArray> iterator(headers);
    t.loop("header",headers.size());
    int i=0;
    while (iterator.hasNext())
    {
        iterator.next();
        t.setVariable(QString("header%1.name").arg(i),QString(iterator.key()));
        t.setVariable(QString("header%1.value").arg(i),QString(iterator.value()));
        ++i;
    }

    response.write(t.toLatin1(),true);
}
