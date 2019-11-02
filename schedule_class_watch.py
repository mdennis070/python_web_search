import sys, os.path, smtplib
from email.mime.text import MIMEText

version = int(sys.version_info.major) + float(sys.version_info.minor)/10
if version < 3:
	import urllib2
else:
	import urllib.request, urllib.parse

class Course:
	def __init__(self, subject, number, list_of_CRNs):
		self.subject = subject
		self.number = number
		self.list_of_CRNs = [s for s in list_of_CRNs]
		self.data_list = []
	def add_row(self, CRN, Type, Cap, Avail, WL_Cap, WL_Avail):
		if CRN in self.list_of_CRNs:
			self.data_list.append([CRN, Type, Cap, Avail, WL_Cap, WL_Avail])
	def print_self(self):
		string2 = self.subject + " " + self.number
		string2 = string2 + ' '*(8-len(string2))
		for row in self.data_list:	
			print(string2 + "  " + row[0] + "  (" + row[1][0:3] + ")\t" + row[3] + "/" + row[2] + "\t  " + row[5] + "/" + row[4])
			string2 = ' '*8
		print()
	def print_msg(self):
		for row in self.data_list:
			sys.stdout.write(self.subject + " " + self.number + " (" + row[0] + ") " + row[3] + " available spots\n")
		sys.stdout.flush()
	def print_email_msg(self):
		msg = ''
		for row in self.data_list:
			msg = msg + self.subject + " " + self.number + " (" + row[0] + ") " + row[3] + " available spots\n"
		return msg
#
def find_cell_data(table, start):
	cell_start_index = table.find('<td>', start)
	cell_end_index = table.find('</td>', cell_start_index)
	return [ ' '.join( table[cell_start_index+4: cell_end_index].split() ), cell_end_index]
#
'''Enter Classes'''
Term = '201801' #yyyytt fall = 01 winter=02 spring=03
schedule = [
			Course('HORT', '301', ['20520']),
			Course('ECE', '375', ['19334', '19337'])
		   ]
'''Enter Classes'''
for course_in_schedule in schedule:
	#get page html
	url = 'http://catalog.oregonstate.edu/CourseDetail.aspx?Columns=foqstv&SubjectCode=' + course_in_schedule.subject + '&CourseNumber=' + course_in_schedule.number + '&Term=' + Term + '&Campus=corvallis'
	if version < 3:
		response = urllib2.urlopen(url)
		page_html = response.read() #retruns a binary literal
	else:
		with urllib.request.urlopen(url) as response:
			page_html = response.read() #retruns a binary literal
	#
	#find the start of the table using a binary literal of the sting (id of the table)
	table_ID_index = page_html.find(b'ctl00_ContentPlaceHolder1_SOCListUC1_gvOfferings')
	table_start_tag_index = page_html.rfind(b'<table', 0, table_ID_index)
	table_end_tag_index = page_html.find(b'</table>', table_ID_index)
	table = page_html[table_start_tag_index:table_end_tag_index+10].decode("UTF-8")
	#remove style elements of the table
	table = table.replace('<font size="2">', "").replace('</font>', "").replace(' scope="col"', "").replace(' align="center"', "").replace('<b>', "").replace('</b>', "").replace(' valign="top"', "")

	#search table rows for values
	num_of_rows = table.count('<tr>')
	start_search_index = 0
	for i in range(0, num_of_rows+1):
		CRN_list = find_cell_data(table, start_search_index)
		CRN = CRN_list[0]
		
		Type_list = find_cell_data(table, CRN_list[1])
		Type = Type_list[0]
		
		Cap_list = find_cell_data(table, Type_list[1])
		Cap = Cap_list[0]
	
		Avail_list = find_cell_data(table, Cap_list[1])
		Avail = Avail_list[0]
	
		WL_Cap_list = find_cell_data(table, Avail_list[1])
		WL_Cap = WL_Cap_list[0]
	
		WL_Avail_list = find_cell_data(table, WL_Cap_list[1])
		WL_Avail = WL_Avail_list[0]
		
		start_search_index = WL_Avail_list[1]
		course_in_schedule.add_row(CRN, Type, Cap, Avail, WL_Cap, WL_Avail)
	#
	#checks for a local file for the amount of available spots in the class last time the program ran
	send_msg = False
	for row in course_in_schedule.data_list:
		msg_text = course_in_schedule.print_email_msg()
		if os.path.isfile('' + str(course_in_schedule.subject) + str(course_in_schedule.number) + str(row[0])):
			f = open(""+str(row[0])+".txt","wr")
			contents = f.read()
			if contents != row[3]:
				send_msg = True
				f.write(row[3])
			#
			f.close()
		else:
			f = open(''+str(row[0])+".txt","w+")
			f.write(row[3])
			f.close()
			send_msg = True
		#
	#
#
if send_msg:
	msg = MIMEText(msg_text)
	msg['Subject'] = 'The contents of %s' % textfile
	msg['From'] = 'dennimit@oregonstate.edu'
	msg['To'] = 'dennimit@oregonstate.edu'
	server = smtplib.SMTP('localhost')
	server.sendmail('dennimit@oregonstate.edu', 'dennimit@oregonstate.edu', msg.as_string())
	server.quit()
#
input("enter to quit")