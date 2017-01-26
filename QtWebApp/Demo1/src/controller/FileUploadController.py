#include "httprequest.h"
#include "httpresponse.h"
#include "httprequesthandler.h"

/**
  This controller displays a HTML form for file upload and recieved the file.
*/

class FileUploadController : public HttpRequestHandler {
    Q_OBJECT
    Q_DISABLE_COPY(FileUploadController)
public:

    /** Constructor */
    FileUploadController();

    /** Generates the response */
    void service(HttpRequest& request, HttpResponse& response);
};

#include "fileuploadcontroller.h"

FileUploadController::FileUploadController()
{}

void FileUploadController::service(HttpRequest& request, HttpResponse& response)
{

    if (request.getParameter("action")=="show")
    {
        response.setHeader("Content-Type", "image/jpeg");
        QTemporaryFile* file=request.getUploadedFile("file1");
        if (file)
        {
            while (!file->atEnd() && !file->error())
            {
                QByteArray buffer=file->read(65536);
                response.write(buffer);
            }
        }
        else
        {
            response.write("upload failed");
        }
    }

    else
    {
        response.setHeader("Content-Type", "text/html; charset=ISO-8859-1");
        response.write("<html><body>");
        response.write("Upload a JPEG image file<p>");
        response.write("<form method=\"post\" enctype=\"multipart/form-data\">");
        response.write("  <input type=\"hidden\" name=\"action\" value=\"show\">");
        response.write("  File: <input type=\"file\" name=\"file1\"><br>");
        response.write("  <input type=\"submit\">");
        response.write("</form>");
        response.write("</body></html>",true);
    }
}

