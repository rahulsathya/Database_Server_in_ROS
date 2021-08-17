#!/usr/bin/env python
 
import rospy
import pymongo
import json
import base64
import Image
import time

from datetime import datetime
from bson import ObjectId
from std_msgs.msg import String
from geometry_msgs.msg import Pose,Point, Quaternion
from ros_service.srv import hazard, hazardResponse, hazard_return, hazard_returnResponse, map_pgm, map_pgmResponse, map_yaml, map_yamlResponse, map_pgm_return, map_pgm_returnResponse, map_yaml_return, map_yaml_returnResponse, warden_id, warden_idResponse, action, actionResponse, event, eventResponse, occ_war_list, occ_war_listResponse, loc_state, loc_stateResponse, beacon_id, beacon_idResponse, rob_beacon_info, rob_beacon_infoResponse, beacon_goal, beacon_goalResponse, roles_req, rf_beacon_list, rf_beacon_listResponse

beacon_list =0
##functions
#action
def action_fn(msg):
	robot_id = msg.robot_id
	robot_action = msg.robot_action
	haz_desc = msg.haz_desc
	field = {
		'action': robot_action
		}
	update_data = collection_role.update_many({'robot_id': robot_id },{"$set": field}, upsert=True)
	field = {'status': robot_action}
	#update_action = collection_hazard.update_many({'haz_desc':haz_desc },{"$set": field}, upsert=True)
	
	print 'Received new action: ', robot_action, 'from', robot_id
	return actionResponse('role updated')
	
def warden_id_fn(msg):
	warden_id_list = []
	warden_idle_list = []
	for x in collection_role.find({'role': {'$regex': 'warden', '$options': 'action'}}):
		warden_id_list.append(x['robot_id'])
	n = len(warden_id_list)
	for x in range(n):
		rob_id = warden_id_list[x]
		get_data  = collection_role.find_one({'robot_id': rob_id})
		if get_data['action'] == 'idle':
			warden_idle_list.append(rob_id)			
			
	print 'List of available wardens:',warden_idle_list
	return warden_idResponse(warden_idle_list)

#role



#hazard
def hazard_fn(msg):
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
		'haz_desc': desc
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
		'haz_desc': desc
		}
	if desc.isdigit() is False:
		if desc:
			# find the number of hazards
			haz_arr = []	
	
			if collection_hazard.count() == 0:   #check if collection is empty
				new_hz_id = 1
				data_insert = collection_hazard.update_many({'haz_id': new_hz_id}, {"$set": field_mod}, upsert=True)
				data_insert_2 = collection_hazard_actual.update_many({'haz_id': new_hz_id}, {"$set": field_actual}, upsert=True)
				print 'Received new hazard !!'
			else:
				for x in collection_hazard.find({},{"_id":0, "haz_id":1}):
					haz_arr.append(x['haz_id'])
				recent_hz = max(haz_arr)

				new_hz_id = recent_hz + 1
				data_insert = collection_hazard.update_many({'haz_id': new_hz_id}, {"$set": field_mod}, upsert=True)
				data_insert_1 = collection_hazard_actual.update_many({'haz_id': new_hz_id}, {"$set": field_actual}, upsert=True)
				print 'Received new hazard!!'
	
			#publish notification for new hazard	
			pub = rospy.Publisher ('notification', String , queue_size=10)
			rate = rospy.Rate(1)
			for i in range (1,3):
				rospy.loginfo('New Hazard Available!!')
				pub.publish('new_hazard_available')
				rate.sleep()
	else:
		print 'Invalid hazard detected' 
	return hazardResponse('New Hazard Updated')	

def hazard_rtrn(msg):
	#if msg.haz_request == 'new_hazard_required':	
	haz_id = msg.haz_request
	hazards = []
	'''
	for x in collection_hazard.find({},{"_id":0, "haz_id":1}):
		hazards.append(x['haz_id'])
	new_haz = max(hazards)
	'''
	haz_db = collection_hazard.find_one({'haz_id': haz_id})
	frame_id = haz_db['frame_id']
	time = haz_db['timestamp']
	desc = haz_db['haz_desc']
	
	pose_x = haz_db['pose_x']
	pose_y = haz_db ['pose_y']
	orientation_x = haz_db ['orient_x']
	orientation_y = haz_db ['orient_y']
	orientation_z = haz_db ['orient_z']
	orientation_w = haz_db ['orient_w']
	mod_coordinates = Pose(Point(pose_x,pose_y,0.0),Quaternion(orientation_x,orientation_y,orientation_z,orientation_w))
	time = haz_db['timestamp']
	desc = haz_db['haz_desc']
	
	print 'New hazard sent to warden..'
	return hazard_returnResponse(frame_id,time,mod_coordinates,desc) 
	

#map
def map_pgm_fn(msg):
	map_str = msg.map_pgm_str
	field = {
		'map_pgm': map_str
		}
	data_insert = collection_map.update_many({'map_id': 'map_1'}, {"$set": field}, upsert=True)
	
	##publish notification for new map
	pub = rospy.Publisher ('notification_map', String , queue_size=10)
	rate = rospy.Rate(10)
	for i in range (1,3):
		rospy.loginfo('Notification - New Map Available!!')
		pub.publish('new_map_available')
		rate.sleep()
	return map_pgmResponse('New Map-pgm Updated')

def map_pgm_rtrn(msg):
	map_db = collection_map.find_one({'map_id': 'map_1'})
	map_str = map_db['map_pgm']
	return map_pgm_returnResponse(map_str)
	
	
def map_yaml_fn(msg):
	image = msg.image
	resolution = msg.resolution
	origin = msg.origin
	occupied_thresh = msg.occupied_thresh
	free_thresh = msg.free_thresh
	negate = msg.negate
	timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')
	field = { 
		'image' : image,
		'resolution' :resolution,
		'origin' : origin,
		'occupied_thresh' : occupied_thresh,
		'free_thresh' : free_thresh,
		'negate' :negate
		}
	data_insert = collection_map.update_many({'map_id': 'map_1'}, {"$set": field}, upsert=True)	
	return map_yamlResponse ('New Map-yaml Updated')

def map_yaml_rtrn(msg):
	
	time.sleep(1)
	map_db = collection_map.find_one({'map_id': 'map_1'})
	image = map_db['image']
	resolution = map_db['resolution']
	origin = map_db['origin']
	occupied_thresh = map_db['occupied_thresh']
	free_thresh = map_db['free_thresh']
	negate = map_db['negate']
	return map_yaml_returnResponse (image, resolution, origin, occupied_thresh, free_thresh, negate)

def event_fn(msg):
	
	timestamp = msg.timestamp
	name = msg.name
	robot_id = msg.robot_id
	robot_pose_x = msg.robot_pose.x
	robot_pose_y = msg.robot_pose.y
	robot_pose_z = msg.robot_pose.z
	field = {
		'name' : name,
		'robot_id' : robot_id,
		'time' : timestamp,
		'pose_x':robot_pose_x,
		'pose_y':robot_pose_y,
		'pose_z':robot_pose_z		
		}
	data_insert = collection_event.insert_one(field)
	print 'New event received: ', name
	return eventResponse('Event Recorded')

def occ_war_fn(msg):
	
	warden_id_list = []
	warden_list = []
	for x in collection_role.find({'role': {'$regex': 'warden', '$options': 'action'}}):
		warden_id_list.append(x['robot_id'])
	n = len(warden_id_list)
	for x in range(n):
		rob_id = warden_id_list[x]
		get_data  = collection_role.find_one({'robot_id': rob_id})
		if get_data['action'] == 'occupied':
			warden_list.append(rob_id)			
	
	get_guide = collection_role.find_one({'role': 'guide'})
	warden_list.append(get_guide['robot_id'])
	
	if len(warden_list) >= 3:
		#publish notification for warden+guide list	
			pub = rospy.Publisher ('notification_list', String , queue_size=10)
			rate = rospy.Rate(1)
			for i in range (1,3):
				rospy.loginfo('RF beacon info!!')
				pub.publish('rf_beacon_info')
				rate.sleep()
	

	print 'List of available occupied wardens:',warden_list

	
	return occ_war_listResponse (warden_list)

def state_fn(msg):
	robot_id = msg.robot_id
	loc_state = msg.state
	field = {
		'loc_state' : loc_state
		}
	update_data = collection_role.update_many({'robot_id': robot_id },{"$set": field}, upsert =True)
	print 'state',loc_state,' for robot:', robot_id
	
	return loc_stateResponse('State Received')

#beacon
def beacon_fn(msg):
	get_data = collection_beacon.find_one({'id': 1})
	beacon_id = get_data['beacon_id']
	print 'Beacon ID sent ', beacon_id
	return beacon_idResponse(beacon_id)

def beacon_info(msg):
	global rob_list,beacon_list
	field = {
		'robot_id' : msg.robotID,
		'd' : msg.d,
		'x' : msg.x,
		'y' : msg.y,
		'timestamp' : msg.timestamp
		}
	insert_data = collection_beacon_info.insert(field)
	beacon_list = beacon_list + 1 
	if beacon_list >= 3:
		#publish notification for warden+guide list	
			pub = rospy.Publisher ('notification_list', String , queue_size=10)
			rate = rospy.Rate(1)
			for i in range (1,3):
				rospy.loginfo('RF beacon info!!')
				pub.publish('rf_beacon_info')
				rate.sleep()

	return rob_beacon_infoResponse('beacon info received')

def beacon_goal_fn(msg):
	field = {
		'timestamp': msg.timestamp,
		'goal_x': msg.goalX,
		'goal_y':msg.goalY		
		}
	insert_data = collection_beacon_goal.insert(field)
	return beacon_goalResponse('beacon goal received')

def beacon_list_fn(msg):
	global warden_list, guide_list

	robot_1 = []
	robot_2 = []
	robot_3 = []
	get_rob1 = collection_beacon_info.find_one({'robot_id': warden_list[0]})
	print get_rob1
	get_rob2 = collection_beacon_info.find_one({'robot_id': warden_list[1]})
	get_rob3 = collection_beacon_info.find_one({'robot_id': guide_list[0]})
	
	robot_1.append(get_rob1['x'])
	robot_1.append(get_rob1['y'])
	robot_1.append(get_rob1['d'])
	robot_2.append(get_rob2['x'])
	robot_2.append(get_rob2['y'])
	robot_2.append(get_rob2['d'])
	robot_3.append(get_rob3['x'])
	robot_3.append(get_rob3['y'])
	robot_3.append(get_rob3['d'])	
	
	return 	rf_beacon_listResponse(robot_1,robot_2,robot_3)
	
def roles_fn(msg):
	field = {'role':'x'}


if __name__=='__main__':

	
	rospy.init_node('server_main')
	rospy.loginfo('server_main')
	rospy.set_param('/pub_notif_hazard', False)
	
	db_name ="db_%s_%s_%s"%(datetime.fromtimestamp(time.time()).strftime('%Y'), 
		                  datetime.fromtimestamp(time.time()).strftime('%m'), 
		                  datetime.fromtimestamp(time.time()).strftime('%d'))
	## db ##
	db_connect = pymongo.MongoClient('localhost',27017)
	db = db_connect[db_name]
	print 'Database name: ', db_name

	## db collections ##
	collection_beacon = db['beacon_id']
	collection_beacon_info = db['beacon_info']
	collection_beacon_goal = db['beacon_goal']
	collection_hazard = db['hazards']
	collection_hazard_actual = db['hazards_actual']
	collection_map = db['map']
	collection_role = db['roles']
	collection_event = db['events']

	##Reboot actions
	#roles
	del_role = collection_role.delete_many({})

	exp_list = ['tb3_5']
	warden_list = ['tb3_6','tb3_7']
	guide_list = ['tb3_2']
	warden_field = {
		'action':'idle',
		'role':'warden',
		'loc_state': 'idle'
		}
	exp_field = {
		'action':'idle',
		'role':'explorer',
		'loc_state': 'idle'
		}
	guide_field = {
		'action':'idle',
		'role':'guide',
		'loc_state': 'idle'
		}
	for rob_id in exp_list:
		update_data = collection_role.update_many({'robot_id': rob_id },{"$set": exp_field}, upsert=True)	
	
	for rob_id in warden_list:
		update_data = collection_role.update_many({'robot_id': rob_id },{"$set": warden_field}, upsert=True)

	for rob_id in guide_list:
		update_data = collection_role.update_many({'robot_id': rob_id },{"$set": guide_field}, upsert=True)

	#beacon
	field = {
		'id':1,
		'beacon_id': '001986002211'
		}
	del_beacon = collection_beacon.delete_many({})
	update_data = collection_beacon.insert(field)
	del_beacon_info = collection_beacon_info.delete_many({})
	
	#del_hazards = collection_hazard.delete_many({})
	#del_hazards_actual = collection_hazard_actual.delete_many({})		

	## servers ##

	#beacon
	server_beacon_id = rospy.Service('beacon_id_serv', beacon_id, beacon_fn)
	server_beacon_info = rospy.Service('beacon_info_serv', rob_beacon_info, beacon_info)
	server_beacon_goal = rospy.Service('beacon_goal_serv', beacon_goal, beacon_goal_fn)
	server_beacon_list = rospy.Service('beacon_list_serv', rf_beacon_list, beacon_list_fn)

	#hazard	
	server_hazard_return = rospy.Service('hazard_return_serv', hazard_return, hazard_rtrn)
	#server_hazard = rospy.Service('hazard_serv', hazard, hazard_fn)

	#map
	server_map_pgm = rospy.Service('map_pgm_serv', map_pgm, map_pgm_fn)
	server_map_pgm_return = rospy.Service('map_pgm_return_serv', map_pgm_return, map_pgm_rtrn)
	server_map_yaml = rospy.Service('map_yaml_serv', map_yaml, map_yaml_fn)
	server_map_yaml_return = rospy.Service('map_yaml_return_serv', map_yaml_return, map_yaml_rtrn)

	#action
	server_warden_id = rospy.Service('warden_id_serv', warden_id, warden_id_fn)
	server_action = rospy.Service('action_serv', action, action_fn)
	server_occ_war_list = rospy.Service('occ_war_list_serv', occ_war_list, occ_war_fn)

	#event
	server_event = rospy.Service('event_serv', event, event_fn)

	#localisation state
	server_state = rospy.Service('state_serv', loc_state, state_fn)
	server_state = rospy.Service('loc_state_serv', loc_state, state_fn)
	
	#roles
	server_role = rospy.Service('roles_serv', roles_req, roles_fn)
	
	rospy.spin()
