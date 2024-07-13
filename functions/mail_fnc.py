import ssl
import smtplib
from smtplib import SMTP_SSL

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 共通ファンクションの読込(Reading common functions)
from functions import mysqlaio_fnc
from functions import log_fnc

# 共通ユーティリティの読込(Reading common utilities)
from util import util_cmn

async def execSendEmail(objDbPool, strSubject: str, strMessage: str, strSendMail: str=""):
    """
    メール送信処理(mail service)

    strSendMailを指定することで指定のアドレスにメール送信することが可能(Email can be sent to a specified address by specifying strSendMail)

    Args:

        strSubject (int): メールタイトル(Mail Title)

        strMessage (int): メールメッセージ(email message)

        strSendMail (int): メール宛先(Mailing address)

    Returns:

        bool:成功:メール送信 失敗:Fals](Success:send mail Failure:False)
    """

    objLogger = await log_fnc.setOutputLog()
    aryLogExtra = await util_cmn.getIpAddress()

    # メール情報取得(Obtaining email information)
    strMailDealerSendMail = getenv("mail_system_send_mail")
    strMailDealerInfoMail =  getenv("mail_system_info_mail")
    strMailHost = getenv("mail_host")
    strMailPort = getenv("mail_port")
    strMailUsername = getenv("mail_username")
    strMailPassword = getenv("mail_password")
    intMailTimeout = getenv("mail_timeout")
    strMailLocalDomain = getenv("mail_local_domain")
    strMailEncryption = getenv("mail_encryption")

    # 宛先の指定があれば書き換える(Rewrite the destination designation, if any)
    if strSendMail != "":
        strMailDealerSendMail = strSendMail

    # 設定がない場合はメール送信無(No email sent if no settings)
    if strMailHost == None or strMailPort == None or strMailDealerSendMail == None or strMailDealerInfoMail ==None:
        objLogger.info(f"メール送信無(mail send notthing)", extra=aryLogExtra)
        return False

    try:
        # MIMETextを作成(Create MIMEText)
        objMIMEMultipart = MIMEMultipart()
        objMIMEMultipart['Subject'] = strSubject
        objMIMEMultipart['From'] = strMailDealerInfoMail
        objMIMEMultipart['To'] = strMailDealerSendMail
        objMIMEMultipart.attach(MIMEText(strMessage, 'plain', 'utf-8'))

        # サーバを指定(Specify server)
        if strMailEncryption == "tls":
            objContext = ssl.create_default_context()
            server = SMTP_SSL(strMailHost, strMailPort, context=objContext)
            if intMailTimeout != None:
                server.timeout = int(intMailTimeout)
        elif strMailHost == "mailhog":
            if intMailTimeout != None:
                server = smtplib.SMTP(strMailHost, strMailPort, timeout=int(intMailTimeout))
            else:
                server = smtplib.SMTP(strMailHost, strMailPort)
        else:
            if intMailTimeout != None:
                server = smtplib.SMTP(strMailHost, strMailPort, timeout=int(intMailTimeout))
            else:
                server = smtplib.SMTP(strMailHost, strMailPort)
            server.starttls()

        # ログイン処理(login process)
        if strMailUsername != None and strMailPassword != None:
            server.login(strMailUsername, strMailPassword)

        # メールを送信(Send email to)
        server.send_message(objMIMEMultipart)
        
        # 閉じる(close)
        server.quit()

    except Exception as e:
        objLogger.critical(f"メール送信失敗(Exception Error mail send) Exception:{e}", extra=aryLogExtra)
        return False
    
async def execSendEmailHtml(objDbPool, strSubject: str, strMessage: str, strSendMail: str=""):
    """
    HTMLメール送信処理(html mail service)

    strSendMailを指定することで指定のアドレスにメール送信することが可能(Email can be sent to a specified address by specifying strSendMail)

    Args:

        strSubject (int): メールタイトル(Mail Title)

        strMessage (int): メールメッセージ(email message)

        strSendMail (int): メール宛先(Mailing address)

    Returns:

        bool:成功:メール送信 失敗:Fals](Success:send mail Failure:False)
    """

    objLogger = await log_fnc.setOutputLog()
    aryLogExtra = await util_cmn.getIpAddress()

    # メール情報取得(Obtaining email information)
    strMailDealerSendMail = getenv("mail_system_send_mail")
    strMailDealerInfoMail =  getenv("mail_system_info_mail")
    strMailHost = getenv("mail_host")
    strMailPort = getenv("mail_port")
    strMailUsername = getenv("mail_username")
    strMailPassword = getenv("mail_password")
    intMailTimeout = getenv("mail_timeout")
    strMailLocalDomain = getenv("mail_local_domain")
    strMailEncryption = getenv("mail_encryption")
    strMailSendType = getenv("mail_send_type")

    # 宛先の指定があれば書き換える(Rewrite the destination designation, if any)
    if strSendMail != "":
        strMailDealerSendMail = strSendMail

    # 設定がない場合はメール送信無(No email sent if no settings)
    if strMailHost == None or strMailPort == None or strMailDealerSendMail == None or strMailDealerInfoMail ==None:
        objLogger.info(f"メール送信無(mail send notthing)", extra=aryLogExtra)
        return False

    try:
        # MIMETextを作成(Create MIMEText)
        objMIMEMultipart = MIMEMultipart('alternative')
        objMIMEMultipart['Subject'] = strSubject
        objMIMEMultipart['From'] = strMailDealerInfoMail
        objMIMEMultipart['To'] = strMailDealerSendMail
        objMIMEMultipart.attach(MIMEText(strMessage, 'html', 'utf-8'))

        # サーバを指定(Specify server)
        if strMailEncryption == "tls":
            objContext = ssl.create_default_context()
            server = SMTP_SSL(strMailHost, strMailPort, context=objContext)
            if intMailTimeout != None:
                server.timeout = int(intMailTimeout)
        elif strMailHost == "mailhog":
            if intMailTimeout != None:
                server = smtplib.SMTP(strMailHost, strMailPort, timeout=int(intMailTimeout))
            else:
                server = smtplib.SMTP(strMailHost, strMailPort)
        else:
            if intMailTimeout != None:
                server = smtplib.SMTP(strMailHost, strMailPort, timeout=int(intMailTimeout))
            else:
                server = smtplib.SMTP(strMailHost, strMailPort)
            server.starttls()

        # ログイン処理(login process)
        if strMailUsername != None and strMailPassword != None:
            server.login(strMailUsername, strMailPassword)

        # メールを送信(Send email to)
        server.send_message(objMIMEMultipart)
        
        # 閉じる(close)
        server.quit()

    except Exception as e:
        objLogger.critical(f"メール送信失敗(Exception Error mail send) Exception:{e}", extra=aryLogExtra)
        return False