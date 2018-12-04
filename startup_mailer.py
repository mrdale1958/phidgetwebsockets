import subprocess
import smtplib
import socket
from email.mime.text import MIMEText
from time import sleep
import datetime
ipaddr = ""
# Change to your own account information
def send_ip_addr(ip_addr):
    to = 'dale.macdonald@utdallas.edu'
    gmail_user = 'dale.wayne.macdonald@gmail.com'
    gmail_password = 'igqoangrelhdudpu'
    smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_password)
    today = datetime.date.today()
    my_ip = 'Your ip is %s' %  ip_addr
    msg = MIMEText(my_ip)
    msg['Subject'] = 'IP For RaspberryPi on %s' % today.strftime('%b %d %Y')
    msg['From'] = gmail_user
    msg['To'] = to
    smtpserver.sendmail(gmail_user, [to], msg.as_string())
    smtpserver.quit()

# Very Linux Specific
while(1):
    arg='ip route list'
    p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
    data = p.communicate()
    split_data = data[0].split()
    try:
        current_ipaddr = split_data[split_data.index(b'src')+1]
    except ValueError:
        print("error:", ValueError, split_data)
        current_ipaddr = ""
        ipaddr = ""
        
            
    print("ipaddr info",current_ipaddr,ipaddr)
    if (current_ipaddr != ipaddr):
        ipaddr = current_ipaddr
        send_ip_addr(ipaddr)
    sleep(30)
