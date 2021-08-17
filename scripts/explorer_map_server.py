#!/usr/bin/env python
 
import rospy 
import sys
import time
import yaml
import base64
import Image
import os
import rospkg

from std_msgs.msg import String
from nav_msgs.msg import Odometry
from indoor_hazard_management_msgs.msg import EventInfo, QRinfo 

from tinydb import TinyDB, Query
from datetime import datetime
from ros_service.srv import map_pgm, map_yaml



if __name__ == '__main__':
	
	rospy.init_node('explorer_map_server')
	#check for server
	rospy.wait_for_service('map_pgm_serv')
	rospy.wait_for_service('map_yaml_serv')

	#local proxy for the service
	srv_map_pgm = rospy.ServiceProxy('map_pgm_serv',map_pgm)
	srv_map_yaml = rospy.ServiceProxy('map_yaml_serv',map_yaml)

	map_location = rospkg.RosPack().get_path('indoor_hazard_management')
	print map_location
	while True:
		print 'Creating map...'
		time.sleep(8)
		#map
		###check file availability(not done)
		
		with open(map_location + '/mapping/map/explore_map.pgm', "rb") as imageFile:
			map_str = base64.b64encode(imageFile.read())
		send_map_pgm = srv_map_pgm(map_str)
		
		with open(map_location + '/mapping/map/explore_map.yaml', "r") as file:
		    yaml_read = yaml.safe_load(file)

		image = yaml_read['image']
		resolution = yaml_read['resolution']
		origin = yaml_read['origin']
		occupied_thresh = yaml_read['occupied_thresh']
		free_thresh = yaml_read['free_thresh']
		negate = yaml_read['negate']

		send_map_yaml = srv_map_yaml(image, resolution, origin, occupied_thresh, free_thresh, negate)
		print 'New map updated'
