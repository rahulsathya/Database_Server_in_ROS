#!/usr/bin/env python
 
import rospy
import pymongo
import json
import base64
import Image
import time
import threading

from datetime import datetime
from bson import ObjectId
from std_msgs.msg import Int16
from geometry_msgs.msg import Pose,Point, Quaternion
from ros_service.srv import hazard, hazardResponse


def hazard_fn(msg):
	global hazard_list
	frame_id = msg.frame_id
	timestamp = msg.timestamp
	pose_x = msg.mod_coordinates.position.x
	pose_y = msg.mod_coordinates.position.y
	orientation_x = msg.mod_coordinates.orientation.x
	orientation_y = msg.mod_coordinates.orientation.y
	orientation_z = msg.mod_coordinates.orientation.z
	orientation_w = msg.mod_coordinates.orientation.w
	desc = msg.desc
	field_mod = {
		'frame_id':frame_id,
		'timestamp':timestamp,
		'pose_x': pose_x ,
		'pose_y' : pose_y,
		'orient_x' : orientation_x,
		'orient_y' : orientation_y,
		'orient_z' : orientation_z,
		'orient_w' : orientation_w,
		'haz_desc': desc,
		'status': 'idle'
		}
	field_actual = {
		'frame_id':frame_id,
		'timestamp':timestamp,
		'pose_x': msg.actual_coordinates.position.x ,
		'pose_y' : msg.actual_coordinates.position.y,
		'orient_x' : msg.actual_coordinates.orientation.x,
		'orient_y' : msg.actual_coordinates.orientation.y,
		'orient_z' : msg.actual_coordinates.orientation.z,
		'orient_w' : msg.actual_coordinates.orientation.w,
		'haz_desc': desc,
		'status':'idle'
		}

	if desc.isdigit() is False:
		if desc:
			# find the number of hazards
			haz_arr = []	
	
			if collection_hazard.count() == 0:   #check if collection is empty
				new_hz_id = 1
				data_insert = collection_hazard.update_many({'haz_id': new_hz_id}, {"$set": field_mod}, upsert=True)
				data_insert_2 = collection_hazard_actual.update_many({'haz_id': new_hz_id}, {"$set": field_actual}, upsert=True)
				hazard_list.append(new_hz_id)
				print 'Received new hazard !!'
				print 'haz list:', hazard_list
			else:
				for x in collection_hazard.find({},{"_id":0, "haz_id":1}):
					haz_arr.append(x['haz_id'])
				recent_hz = max(haz_arr)

				new_hz_id = recent_hz + 1
				data_insert = collection_hazard.update_many({'haz_id': new_hz_id}, {"$set": field_mod}, upsert=True)
				data_insert_1 = collection_hazard_actual.update_many({'haz_id': new_hz_id}, {"$set": field_actual}, upsert=True)
				hazard_list.append(new_hz_id)
				print 'Received new hazard!!'
				print 'haz list:', hazard_list
		else:
			print 'Invalid hazard'
	else:
		print 'Invalid hazard'
		

	return hazardResponse('New Hazard Updated')	

def hazard_pub():
	
	warden_id_list = [] #available warden list
	warden_list = [] #occupied warden list
	global state, hazard_list
	for x in collection_role.find({'role': {'$regex': 'warden', '$options': 'action'}}):
		warden_id_list.append(x['robot_id'])
	n = len(warden_id_list)
	end = False
	while not rospy.is_shutdown():		
		
		#check loc state & check hazard list
		if state == True and len(hazard_list) >0:
			haz_id = min(hazard_list)
			#publish notification for new hazard	
			pub = rospy.Publisher ('/notification', Int16 , queue_size=10)
			rate = rospy.Rate(1)
			for i in range (1,3):
				print('New Hazard Available!!, ID:',haz_id)
				pub.publish(haz_id)
				rate.sleep()
			hazard_list.remove(haz_id)
			#ensuring robot occupied the hazard
			while not rospy.is_shutdown() and not end:
				
				for x in range(n):
					rob_id = warden_id_list[x]
					get_data  = collection_role.find_one({'robot_id': rob_id})
					if get_data['action'] == 'occupied' or get_data['action'] == 'unnavigable':
						warden_list.append(rob_id)			
				if len(warden_list) == haz_id:
					end = True

			
def loc_check():
	global state
	# check localisation state
	while not rospy.is_shutdown():
			
		warden_id_list = []
		warden_state_list = []
		for x in collection_role.find({'role': {'$regex': 'warden', '$options': 'loc_state'}}):
			warden_id_list.append(x['robot_id'])
		n = len(warden_id_list)
		for x in range(n):
			rob_id = warden_id_list[x]
			get_data  = collection_role.find_one({'robot_id': rob_id})
			if get_data['loc_state'] == 'True':
				warden_state_list.append(rob_id)
		if len(warden_state_list) == n:
			state = True
			print 'All robots localised'
			break
		else:
			state = False
		

if __name__=='__main__':
	rospy.init_node('server_hazard')
	rospy.loginfo('server_hazard')
	
	db_name ="db_%s_%s_%s"%(datetime.fromtimestamp(time.time()).strftime('%Y'), 
		                  datetime.fromtimestamp(time.time()).strftime('%m'), 
		                  datetime.fromtimestamp(time.time()).strftime('%d'))

	## db ##
	db_connect = pymongo.MongoClient('localhost',27017)
	db = db_connect[db_name]
	print 'Database name: ', db_name

	## db collections ##
	collection_beacon = db['beacons']
	collection_hazard = db['hazards']
	collection_hazard_actual = db['hazards_actual']
	collection_map = db['map']
	collection_role = db['roles']
	collection_event = db['events']
	rospy.sleep(3)
	#initial setup
	global hazard_list, state
	hazard_list=[]
	state=False

	#del_hazards = collection_hazard.delete_many({})
	#del_hazards_actual = collection_hazard_actual.delete_many({})
	
	## servers ##
	#hazard
	server_hazard = rospy.Service('hazard_serv', hazard, hazard_fn)
	
	#multiprocess
	process1 = threading.Thread(target = hazard_pub)
	process2 = threading.Thread(target = loc_check)
	process1.start(); process2.start()
	

	rospy.spin()
