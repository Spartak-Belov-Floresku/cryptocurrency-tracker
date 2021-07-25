import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class sendEmailApp:
    """
    Class will send email or text-message notification to the user email or phone number.
    To use this class, you need to set up an account in Gmail
    """

    def __init__(self, email_reciver, subject):
        self.server = smtplib.SMTP("smtp.gmail.com", 587) #protocol to use gmail gateway
        self.password_email_sender = 'password_email' #put your email account password, here
        self.email_sender = 'your_email_id@gmail.com' #put your email id, here
        self.msg = MIMEMultipart()
        self.email_reciver = email_reciver
        self.subject = subject
        

    def formation_request(self, code):
        self.msg["From"] = self.email_sender
        self.msg["To"] = self.email_reciver
        self.msg["Subject"] = self.subject
        self.msg.attach(MIMEText(code, "plain"))

        return self.send_code()

    def send_code(self):
        
        text = self.msg.as_string()

        try:
            self.server.starttls()
            self.server.login(self.email_sender, self.password_email_sender)
            self.server.sendmail(self.email_sender, self.email_reciver, text)
            self.server.quit()
            return True
        except Exception as err:
            return False
