#!/usr/bin/env python
 
import rospy 
import sys
import time
import yaml

import base64
import Image

from std_msgs.msg import String
from ros_service.srv import hazard, hazard_return, map_pgm, map_pgmResponse,  map_pgm_return, map_yaml, map_yaml_return, warden_id, roles

rospy.init_node('warden')
'''
#check for the server
rospy.wait_for_service('hazard_serv')
rospy.wait_for_service('hazard_return_serv')
rospy.wait_for_service('map_pgm_return_serv')
rospy.wait_for_service('map_yaml_return_serv')
rospy.wait_for_service('warden_id_serv')
rospy.wait_for_service('roles_serv')


#local proxy for the service
srv_hazard = rospy.ServiceProxy('hazard_serv',hazard)
srv_hazard_return = rospy.ServiceProxy('hazard_return_serv',hazard_return)
srv_map_pgm = rospy.ServiceProxy('map_pgm_return_serv',map_pgm_return)
srv_map_yaml = rospy.ServiceProxy('map_yaml_return_serv',map_yaml_return)
srv_warden_id = rospy.ServiceProxy('warden_id_serv',warden_id)
srv_roles = rospy.ServiceProxy('roles_serv',roles)


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
	sub_data = msg.data
	
	if sub_data == 'new_hazard_available':
		rospy.wait_for_service('hazard_return_serv')
		srv_hazard_return = rospy.ServiceProxy('hazard_return_serv',hazard_return)		
		send_serv = srv_hazard_return('new_hazard_required')		
		pose_x = send_serv.pose_x
		pose_y = send_serv.pose_y
		print '!!Received new hazard!!'
		
		print 'frame_id:', send_serv.frame_id
		print 'pose_x:', pose_x
		print 'pose_y:', pose_y
		print 'time:', send_serv.time
		print 'hazard desc:', send_serv.desc
		
		
	elif sub_data == 'new_map_available':
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
	
	

#subscribe notification
rospy.Subscriber("notification", String, notif_cb)
rospy.Subscriber("notification_explorer", String, notif_expl_cb)
rospy.spin()


