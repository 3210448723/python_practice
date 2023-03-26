import smtplib
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import os


def send_results(filename):
	from_addr = 'xxx@qq.com'
	password = 'uiosslpxxx'  # 使用授权密码
	to_addr = 'xxx@qq.com'
	smtp_server = 'smtp.qq.com'

	# 每个词之间用 ------------ 隔开
	msg = MIMEMultipart()
	msg['From'] = Header('人民日报词频')  # 发送者
	msg['To'] = Header('host')  # 接收者
	subject = '人民日报词频'
	msg['Subject'] = Header(subject, 'utf-8')  # 邮件主题

	with open(filename, 'rb') as f:
		file_content = f.read()
		part = MIMEApplication(file_content)
		part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))
		msg.attach(part)

	try:
		smtpobj = smtplib.SMTP()
		smtpobj.connect(smtp_server, 25)  # 使用对应的端口
		smtpobj.login(from_addr, password)
		smtpobj.sendmail(from_addr, to_addr, msg.as_string())
		print("邮件发送成功")
	except Exception as e:
		print("邮件发送失败：", e)
	smtpobj.quit()


if __name__ == "__main__":
	send_results("./result/2023-03-26.csv")
