#!/usr/bin/env python
 
import rospy 
import sys
import time
import yaml

import base64
import Image

from std_msgs.msg import String
from ros_service.srv import mac_add


if __name__ = '__main__':

	rospy.init_node('guide_server')
	rospy.loginfo('guide_server')

	## db ##
	db_connect = pymongo.MongoClient('localhost',27017)
	db = db_connect['centralised_db']
	#print 'Database name: ', db_name

	## db collections ##
	collection_beacon = db['beacon']
	collection_role = db['roles']

	#check for the server
	rospy.wait_for_service('mac_add_serv')


	#local proxy for the service
	srv_beacon = rospy.ServiceProxy('mac_add_serv',mac_add)

	send_req = srv_beacon('001986002211')
	#becon_data = send_req.mac_adr
	print send_req
