import re
import json,sys
from datetime import datetime as dt
import subprocess
import argparse
import csv
from email import Encoders
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.mime.text import MIMEText


def mail(report):
          msg = MIMEMultipart()
          msg["From"] = "me@example.com"
          msg["To"] = "sudipta1436@gmail.com"
          msg["Subject"] = "Report Ansible."
          text='<h5 style="color:green;">KINDLY CLICK ON BELOW MENTIONED LINK FOR PATCH UPDATE</h5>\n<a href="http://localhost/api" style="color:red;">http://localhost/api</a>'
          part1 = MIMEText(text, 'html')
          part = MIMEBase('application', "octet-stream")
          part.set_payload(open(report, "rb").read())
          Encoders.encode_base64(part)
          part.add_header('Content-Disposition', 'attachment', filename=report)
          msg.attach(part)
          msg.attach(part1)
          p =subprocess.Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=subprocess.PIPE)
          p.communicate(msg.as_string())
#          print "done"

def gencsv(out):
		sys.stdout.write(out)
		sys.stdout.flush()
		temp = open("patch-update-available.csv","w+")
		writer = csv.writer(temp)
		writer.writerow(["HOSTNAMES", "PACKAGES"])
		ips = []
		out=out.split("\n")
		clean=[]
		modules = []
		for i in out:
			if "TASK [print out] ******************************************************" in i:
				del out[0:out.index(i)+1]
				break
		for i in out:
			if "PLAY RECAP ************************************************************" in i:
				del out[out.index(i)-1:len(out)-1]
				break
		for i in out:
			if "ok: [" in i:
				clean.append(i)
				i=i.replace("ok: [","")
				i=i.replace("] => {","")
				ips.append(i)
			else:
				i=i.replace('        "',"")
				i=i.replace('", ',"")
				clean.append(i)
		for host in ips:
			frag = 'ok: [%s] => {'%host
			for k in clean:
				if k == frag:
					for mod in range(clean.index(k)+1,len(clean)):
						if clean[mod] == '}':
							break
						else:
							modules.append(clean[mod])
			try:
				del modules[0]
				del modules[0]
				del modules[len(modules)-1]
			except:
				pass
			try:
				writer.writerow([host,modules[0]])
                                del modules[0]
			except:
				writer.writerow([host,""])
			for q in modules:
				if '"msg":' in q:
					pass
				else:
					writer.writerow(["",q.replace('"','')])
def execute(fur,sur):
		cmd2 = "ansible-playbook -i %s %s --vault-password-file /home/nik/Desktop/git-repo/python-git/python-ops/rest-api/tower/jobs/patch-mgmt/.vault"%(fur,sur)
		p = subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)  
		out, err = p.communicate()
		return(out)
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-i")
	parser.add_argument("-f")
	args = parser.parse_args()
	if (args.i is not None) and (args.f is not None):
		out = execute(args.i,args.f)
		gencsv(out)
		mail("patch-update-available.csv")
	else:
		print("Missing arguments .")
