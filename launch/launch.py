#!/usr/bin/env python
import os
import rospy

rospy.loginfo('Opening Servers....')
rospy.init_node('launch')


db_name = raw_input('Kindly give the Database name (Press enter for default name): ') or 'centralised_db'
rospy.set_param('/db_name',db_name)

command_exp_serv = "python /home/rahul/catkin_ws/src/ros_service/scripts/explorer_server.py"
os.system("gnome-terminal -e 'bash -c \""+command_exp_serv+";bash\"'")

command_serv = "python /home/rahul/catkin_ws/src/ros_service/scripts/server.py"
os.system("gnome-terminal -e 'bash -c \""+command_serv+";bash\"'")

command_serv_haz = "python /home/rahul/catkin_ws/src/ros_service/scripts/server_hazard.py"
os.system("gnome-terminal -e 'bash -c \""+command_serv_haz+";bash\"'")


command_war_serv = "python /home/rahul/catkin_ws/src/ros_service/scripts/warden1_server.py"
os.system("gnome-terminal -e 'bash -c \""+command_war_serv+";bash\"'")


command_war2_serv = "python /home/rahul/catkin_ws/src/ros_service/scripts/warden2_server.py"
os.system("gnome-terminal -e 'bash -c \""+command_war2_serv+";bash\"'")



