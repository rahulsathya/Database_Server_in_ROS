#!/usr/bin/env python
import os
import rospy

rospy.loginfo('Opening Servers....')
rospy.init_node('launch')
my_dir = os.getcwd()

rospack = rospkg.RosPack()
rospack.list()
pkg_path =rospack.get_path('ros_service')

command_exp_serv = "roslaunch ros_service explorer_server.launch"
os.system("gnome-terminal -e 'bash -c \""+command_exp_serv+";bash\"'")


command_war_serv = "python %s/scripts/warden1_server.py"%pkg_path
os.system("gnome-terminal -e 'bash -c \""+command_war_serv+";bash\"'")


command_war2_serv = "python %s/scripts/warden2_server.py"%pkg_path
os.system("gnome-terminal -e 'bash -c \""+command_war2_serv+";bash\"'")



