#include "httprequest.h"
#include "httpresponse.h"
#include "httprequesthandler.h"

/**
  This controller demonstrates how to use sessions.
*/

class SessionController : public HttpRequestHandler {
    Q_OBJECT
    Q_DISABLE_COPY(SessionController)
public:

    /** Constructor */
    SessionController();

    /** Generates the response */
    void service(HttpRequest& request, HttpResponse& response);
};

#include <QDateTime>
#include "sessioncontroller.h"
#include "httpsessionstore.h"

/** Storage for session cookies */
extern HttpSessionStore* sessionStore;

SessionController::SessionController()
{}

void SessionController::service(HttpRequest& request, HttpResponse& response)
{
    response.setHeader("Content-Type", "text/html; charset=ISO-8859-1");

    // Get current session, or create a new one
    HttpSession session=sessionStore->getSession(request,response);
    if (!session.contains("startTime"))
    {
        response.write("<html><body>New session started. Reload this page now.</body></html>");
        session.set("startTime",QDateTime::currentDateTime());
    }
    else
    {
        QDateTime startTime=session.get("startTime").toDateTime();
        response.write("<html><body>Your session started ");
        response.write(startTime.toString().toLatin1());
        response.write("</body></html>");
    }

}
