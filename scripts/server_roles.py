#!/usr/bin/env python
 
import rospy
import pymongo 
import sys
import time
import yaml
import logging
import threading

import base64
import Image

from std_msgs.msg import String
from ros_service.srv import roles, rolesResponse

##functions##

def get_role():
	global tb3_0, tb3_1, tb3_2
	while True:	
		#tb3_0
		get_data = collection.find_one({'robot_id': 'tb3_0'})
		tb3_0 = get_data['role']

		#tb3_1
		get_data = collection.find_one({'robot_id': 'tb3_1'})
		tb3_1 = get_data['role']

		#tb3_2
		get_data = collection.find_one({'robot_id': 'tb3_2'})
		tb3_2 = get_data['role']
		

		

def send_role():
	global tb3_0, tb3_1,tb3_0_status

	rospy.wait_for_service('role_serv')
	srv_role = rospy.ServiceProxy('role_serv',roles) 
	while True:
		rospy.sleep(0.5)
		#tb3_0
		if tb3_0 != tb3_0_status:		
			## send role
			robot_role = tb3_0
			robot_id = 'explorer'
			if robot_role == 'explorer' or robot_role == 'warden':
				send_role = srv_role(robot_id, robot_role)
				print 'Role sent - ',tb3_0
			else:
				print 'Kindly assign the suitable role..'
			tb3_0_status = tb3_0
		
		
		#tb3_1
		get_data = collection.find_one({'robot_id': 'tb3_1'})
		tb3_1_status = get_data['role']
		#print tb3_1_status
		if tb3_1 != tb3_1_status:		
			#print tb3_1_status
			## send role
			send_role = srv_role(tb3_1_status)
			print 'Role sent - ',tb3_1_status
			tb3_1_status = tb3_1
		rospy.sleep(0.5)	
				

	
if __name__=='__main__':
	global tb3_0_status
	rospy.init_node('server_role')
	
	## db 
	db_connect = pymongo.MongoClient('localhost',27017)
	db = db_connect['centralised_db']

	## db collections
	collection = db['roles']

	get_data = collection.find_one({'robot_id': 'tb3_0'})
	tb3_0_status = get_data['role']
	
	threading.Thread(target=get_role).start()	
	threading.Thread(target=send_role).start()
	
	
