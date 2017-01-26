# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.

#if windoz:
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
#else:
#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEText import MIMEText
#from email.MIMEImage import MIMEImage

#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEText import MIMEText
#from email.MIMEImage import MIMEImage
  
class ComponentMail:

  @staticmethod
  def getInstance():
    self = ComponentMail()
    return self   

  def setHost(self, value):
      self.__host = value

  def setPort(self, value):
      self.__port = value

  def setLogin(self, value):
      self.__login = value

  def setPassword(self, value):
      self.__password = value

  def setMailFrom(self, value):
      self.__mailFrom = value

  def setMailTo(self, value):
      self.__mailTo = value

  def setMailCc(self, value):
      self.__mailCc = value

  def setMailBcc(self, value):
      self.__mailBcc = value

  def setSubject(self, value):
      self.__subject = value

  def setBody(self, value):
      self.__body = value

  def prepare(self):
    # Create the root message and fill in the from, to, and subject headers
    self.__msgRoot = MIMEMultipart('related')
    self.__msgRoot['Subject'] = self.__subject
    self.__msgRoot['From'] = self.__mailFrom
    self.__msgRoot['To'] = self.__mailTo
    self.__msgRoot['cc'] = self.__mailCc + ";" + self.__mailBcc
  
    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgHtml = MIMEText(self.__body, 'html')
    self.__msgRoot.attach(msgHtml)

  def addContentId(self, key, value):
      fp = open(value, 'rb')
      msgImage = MIMEImage(fp.read())
      fp.close()

      # Define the image's ID as referenced above
      msgImage.add_header('Content-ID', '<' + key + '>')
      self.__msgRoot.attach(msgImage)

  def send(self):
    import smtplib
    smtp = smtplib.SMTP()
    smtp.connect(self.__host, self.__port)
    smtp.login(self.__login, self.__password)
    smtp.sendmail(self.__mailFrom, self.__mailTo, self.__msgRoot.as_string())
    smtp.quit()
