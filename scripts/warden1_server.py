#!/usr/bin/env python
 
import rospy 
import sys
import time
import yaml
import base64
import Image
from datetime import datetime
from std_msgs.msg import Int16, String
from indoor_hazard_management_msgs.msg import QRinfo, EventInfo
from ros_service.srv import hazard, hazard_return, map_pgm, map_pgmResponse,  map_pgm_return, map_yaml, map_yaml_return, warden_id, action, event, occ_war_list, loc_state

'''
##request
#warden_id
send_data = srv_warden_id('warden_id')
warden_id_ar = send_data.return_request

#update roles
robot_id = 'tb3_1'
robot_action = 'moving to hazard'
send_data = srv_roles(robot_id, robot_action)
print send_data
'''

#function
def notif_cb(msg):
	global my_robot_id
	haz_id = msg.data
	#if sub_data == 'new_hazard_available':
	rospy.set_param('/'+ my_robot_id +'_wardenlist_flag', False)
	
	rospy.wait_for_service('hazard_return_serv')
	srv_hazard_return = rospy.ServiceProxy('hazard_return_serv',hazard_return)		
	send_serv = srv_hazard_return(haz_id)
	print '!!Received new hazard!!'
	print send_serv
	#if send_serv.desc == "Turtlebot3 Burger1":
	###sending to main warden code
	qrinfo = QRinfo()
	qrinfo.hazardID = send_serv.desc
	qrinfo.goalpose = send_serv.mod_coordinates
	qrinfo.status = 2
	qrinfo.job_status = 'warden'
	qrinfo.process = 'sending goal from DB'
	pub_qrinfo.publish(qrinfo)
	print 'Published Hazard Info'
	#else:
		#print 'Irrelevant hazard'

	
	##request
	#warden_id
	send_data = srv_warden_id('warden_id')
	warden_id_ar = send_data.warden_idle_list
	print warden_id_ar
	if my_robot_id in warden_id_ar:
		rospy.set_param('/'+ my_robot_id +'_wardenlist',warden_id_ar)
		rospy.set_param('/'+ my_robot_id +'_wardenlist_flag', True)
		
		print 'Sent warden list to main script', warden_id_ar
	else:
		print my_robot_id, 'not found in the received list'

def notif_map_cb(msg):		
	if msg.data == 'new_map_available':
		#pgm request
		send_req = srv_map_pgm('map_pgm')
		map_str = send_req.map_pgm_str
		map_pgm =  base64.b64decode(map_str)
		with open('map_conv.pgm', 'wb') as imFile:
			imFile.write(map_pgm)
		print 'map file received'
		
		# yaml request
		send_req = srv_map_yaml('new_map_required')
		image = send_req.image
		resolution = send_req.resolution
		origin = send_req.origin
		occupied_thresh = send_req.occupied_thresh
		free_thresh = send_req.free_thresh
		negate = send_req.negate
		
		origin_ar = []		
		for i in range(3):
			origin_ar.append(origin[i])

		print origin_ar
		write_yaml = dict(image = image,resolution = resolution, origin = origin_ar, occupied_thresh = occupied_thresh, free_thresh = free_thresh, negate = negate )
		with open ('map_conv.yaml','w') as outfile:
			yaml.dump(write_yaml, outfile, default_flow_style = False)
		print 'map file saved'
		

def notif_expl_cb(msg):
	sub_data = msg.data
	if sub_data == 'new_hazard_available':
		rospy.wait_for_service('hazard_return_serv')
		srv_hazard_return = rospy.ServiceProxy('hazard_return_serv',hazard_return)
		send_data = srv_hazard_return('new_hazard_required')
		print send_data

def event_info_cb(msg):
	global my_robot_id, state
	if msg.robotID == my_robot_id:
		unix_time = msg.eventtime.secs
		timestamp = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
		name = msg.eventname
		robot_id = msg.robotID
		robot_pose = msg.robot_pose
		send_event = srv_event(timestamp,name,robot_id,robot_pose)
		print 'Event sent'
		if name == 'Navigating to Hazard area' or name == 'Failed to reach the desired pose':
			get_warden_id = rospy.get_param('/' + my_robot_id + '_action')
			#update roles
			robot_id = my_robot_id
			robot_action = get_warden_id[0]
			haz_desc = get_warden_id[1]
			send_data = srv_action(robot_id, robot_action,haz_desc)
			print 'Updated new action :', robot_action
			rospy.sleep(1)
			#Request occupied warden list
			send_req = srv_occ_war_list('OccupiedWardenListRequired')
			print send_req
			warden_list = send_req.warden_list	
			if len(warden_list) >=3:
				rospy.set_param('/'+ my_robot_id +'_occ_wardenlist',warden_list)
				rospy.loginfo('Occupied warden list sent')
			else:
				rospy.loginfo('Not enough occupied warden list')
		if name == 'Finsished localization':
			state = True		
	
if __name__ == '__main__':
	
	rospy.init_node('warden1')
	rospy.loginfo('warden1_server')
	global my_robot_id, state
	my_robot_id = rospy.get_param('~warden', 'tb3_6')

	rospy.set_param('/'+my_robot_id + '_localized_flag',False)
	#check for the server
	rospy.wait_for_service('hazard_serv')
	rospy.wait_for_service('hazard_return_serv')
	rospy.wait_for_service('map_pgm_return_serv')
	rospy.wait_for_service('map_yaml_return_serv')
	rospy.wait_for_service('event_serv')
	rospy.wait_for_service('warden_id_serv')
	rospy.wait_for_service('action_serv')
	rospy.wait_for_service('occ_war_list_serv')
	rospy.wait_for_service('state_serv')

	#local proxy for the service
	srv_hazard = rospy.ServiceProxy('hazard_serv',hazard)
	srv_hazard_return = rospy.ServiceProxy('hazard_return_serv',hazard_return)
	srv_map_pgm = rospy.ServiceProxy('map_pgm_return_serv',map_pgm_return)
	srv_map_yaml = rospy.ServiceProxy('map_yaml_return_serv',map_yaml_return)
	srv_event = rospy.ServiceProxy('event_serv',event)
	srv_warden_id = rospy.ServiceProxy('warden_id_serv',warden_id)
	srv_action = rospy.ServiceProxy('action_serv',action)
	srv_occ_war_list = rospy.ServiceProxy('occ_war_list_serv',occ_war_list)
	srv_loc_state = rospy.ServiceProxy('state_serv', loc_state)

	rospy.set_param('/'+ my_robot_id +'_wardenlist_flag', False)

	pub_qrinfo = rospy.Publisher("/qr_info",QRinfo,queue_size=1)

	state = False
	#Check Localisation state
	while(1):
		
		state = rospy.get_param('/'+my_robot_id + '_localized_flag')
		if state == True:
			state=str(state)
			robot_id = my_robot_id
			send_data = srv_loc_state(robot_id, state)
			print send_data
			break
		else:
			# print 'pass'			
			pass	
			
	#subscribe notification
	rospy.Subscriber("/notification", Int16, notif_cb)
	rospy.Subscriber("notification_map", String, notif_map_cb)
	rospy.Subscriber("notification_explorer", String, notif_expl_cb)
	rospy.Subscriber("/event_info", EventInfo, event_info_cb)	
	#rospy.sleep(1)
	rospy.spin()


