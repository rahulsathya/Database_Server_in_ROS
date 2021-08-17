#!/usr/bin/env python
import os
import rospy
import rospkg

rospy.loginfo('Opening Servers....')
rospy.init_node('launch')

rospack = rospkg.RosPack()
rospack.list()
pkg_path =rospack.get_path('ros_service')

db_name = raw_input('Kindly give the Database name (Press enter for default name): ') or 'centralised_db'
rospy.set_param('/db_name',db_name)

command_exp_serv = "rosrun ros_service explorer_server.py"
os.system("gnome-terminal -e 'bash -c \""+command_exp_serv+";bash\"'")

command_serv = "rosrun ros_service server.py"
os.system("gnome-terminal -e 'bash -c \""+command_serv+";bash\"'")

command_serv_haz = "rosrun ros_service server_hazard.py"
os.system("gnome-terminal -e 'bash -c \""+command_serv_haz+";bash\"'")


command_war_serv = "rosrun ros_service warden1_server.py"
os.system("gnome-terminal -e 'bash -c \""+command_war_serv+";bash\"'")


command_war2_serv = "rosrun ros_service warden2_server.py"
os.system("gnome-terminal -e 'bash -c \""+command_war2_serv+";bash\"'")



