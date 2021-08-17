#!/usr/bin/env python
 
import rospy 
import sys
import time
import yaml
import base64
import Image
import threading

from std_msgs.msg import String
from nav_msgs.msg import Odometry
from indoor_hazard_management_msgs.msg import EventInfo, QRinfo 
from tinydb import TinyDB, Query
from datetime import datetime
from ros_service.srv import hazard, hazard_return, hazard_returnResponse, map_pgm, map_yaml,event


#functions

def hazard_rtrn(msg):
	haz_request = msg.haz_request
	#retrieve from personal_db and send to warden	
	check_haz_exists = db.get (Get.haz_id.exists())
	haz_count = db.count (Get.haz_id)
	if haz_count != 0:
		for n in range(haz_count):
			get_data = db.get(Get.haz_id == haz_count)
			print get_data
	print 'Hazard information sent to warden robot'
			
	return hazard_returnResponse(frame_id,time,pose_x,pose_y,desc)

def hazard_process():	
	global frame_id,pose_x,pose_y,time,desc
	#server
	server_hazard_return = rospy.Service('hazard_return_serv', hazard_return, hazard_rtrn)

	#hazard
	pose_x = 2.3546
	pose_y = 6.6548
	desc = 'fire'
	frame_id = 'map_frame'
	time =str(time.ctime())
	print 'Hazard found...'

	try:	
		rospy.wait_for_service('hazard_return_serv')  
		srv_hazard = rospy.ServiceProxy('hazard_serv',hazard)  		
		send_haz = srv_hazard(frame_id,time,pose_x,pose_y,desc)
		print 'Connected to server'
	except Exception, e: 
	
		print ('Cannot connect to server..')
		db = TinyDB('/home/rahul/catkin_ws/src/ros_service/personal_db/personal_db.json')
		Get = Query()
		check_haz_exists = db.get (Get.haz_id.exists())
		haz_count = db.count (Get.haz_id)
		haz_count = haz_count + 1
		db.insert ({'haz_id': haz_count, 'frame_id': frame_id, 'pose_x': pose_x, 'pose_y':pose_y, 'haz_desc':desc })

		for i in range(5):
			try:
				rospy.wait_for_service('hazard_return_serv')  
				srv_hazard = rospy.ServiceProxy('hazard_serv',hazard)  		
				send_haz = srv_hazard(frame_id,time,pose_x,pose_y,desc)
				print 'Server responded..'
				print 'Hazard info sent to server...'
				break
			except Exception, e:
			    	print 'Server is unable to reach...'
				rospy.sleep(1)

	print ('Publishing notification !!')
	# notification 
	pub = rospy.Publisher ('notification_explorer', String, queue_size=10)
	rate = rospy.Rate(10)
	for i in range (1,3):
		rospy.loginfo('New Hazard Available!!')
		pub.publish('new_hazard_available')
		rate.sleep()

def hazard_no_pDB():
	global time
	#hazard
	try:	
		status = qr_info_msg.status
		job_status = qr_info_msg.job_status

		if status is 1 and job_status is 'explorer_sending':
			#hazard
			coordinates = qr_info_msg.goalpose
			desc = qr_info_msg.hazardID
			frame_id = 'map_frame'
			send_haz = srv_hazard(frame_id,time,coordinates, desc)		
			print 'Hazard sent to the server'
	except Exception, e:
		print 'Did not receive any information'

def map_process():
	while True:
		print 'Creating map...'
		time.sleep(15)
		#map
		###check file availability(not done)
		map_location = "xxgive location herexx"
		with open(map_location, "rb") as imageFile:
			map_str = base64.b64encode(imageFile.read())
		send_map_pgm = srv_map_pgm(map_str)
		map_location_yaml = 'r','call me when you do this'
		with open(r'map.yaml') as file:
		    yaml_read = yaml.safe_load(file)

		image = yaml_read['image']
		resolution = yaml_read['resolution']
		origin = yaml_read['origin']
		occupied_thresh = yaml_read['occupied_thresh']
		free_thresh = yaml_read['free_thresh']
		negate = yaml_read['negate']

		send_map_yaml = srv_map_yaml(image, resolution, origin, occupied_thresh, free_thresh, negate)
		print 'New map updated'


def qr_info_cb(msg):
	#global	qr_info_msg
	#qr_info_msg = msg
	#try:	
	status = msg.status
	job_status = msg.job_status
	if status is 1:
		#hazard
		mod_coordinates = msg.goalpose
		actual_coordinates = msg.hazardpose
		desc = msg.hazardID
		frame_id = 'map_frame'
		
		now = datetime.now()
		unix_time = msg.hazard_time.secs
		timestamp = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
		send_haz = srv_hazard(frame_id,timestamp,mod_coordinates,actual_coordinates, desc)
		print send_haz.confirm_update	
		print 'Hazard sent to the server'

def event_info_cb(msg):
	if msg.robotID == 'tb3_5':
		
		unix_time = msg.eventtime.secs
		timestamp = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
		name = msg.eventname
		robot_id = msg.robotID
		robot_pose = msg.robot_pose
		send_event = srv_event(timestamp,name,robot_id,robot_pose)
		print 'Event sent'
	 
def goal_event():
	
	rospy.Subscriber("/qr_info", QRinfo, qr_info_cb)
	#rospy.sleep(1)
	rospy.Subscriber("/event_info", EventInfo, event_info_cb)	
	#rospy.sleep(1)

if __name__=='__main__':

	rospy.init_node('explorer_main')
	rospy.loginfo('explorer_server')
	qr_info_msg = None
	#check for the server
	rospy.wait_for_service('hazard_serv')
	rospy.wait_for_service('map_pgm_serv')
	rospy.wait_for_service('map_yaml_serv')
	rospy.wait_for_service('event_serv')

	#local proxy for the service
	srv_hazard = rospy.ServiceProxy('hazard_serv',hazard)
	srv_map_pgm = rospy.ServiceProxy('map_pgm_serv',map_pgm)
	srv_map_yaml = rospy.ServiceProxy('map_yaml_serv',map_yaml)
	srv_event = rospy.ServiceProxy('event_serv',event)

	
	rospy.Subscriber("/qr_info", QRinfo, qr_info_cb)
	rospy.Subscriber("/event_info", EventInfo, event_info_cb)
	
	#map_process = threading.Thread(target = map_process)
	#goal_event = threading.Thread(target = goal_event)
	#map_process.start(); 
	#goal_event.start()
	
	rospy.spin()

