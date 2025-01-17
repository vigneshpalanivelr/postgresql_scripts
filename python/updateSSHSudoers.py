#!/usr/bin/python2
import re
import os
import sys
import argparse
import fileinput

#import custom modules
# sys.path.append(os.path.dirname('/var/lib/jenkins/workspace/playbook-provisioning-job/all_scripts/python/pySetenv/variables'))
# sys.path.append(os.path.dirname('/var/lib/jenkins/workspace/playbook-provisioning-job/all_scripts/python/pySetenv/packages'))
# sys.path.append(os.path.dirname('/root/all_scripts/python/pySetenv/variables/'))
# sys.path.append(os.path.dirname('/root/all_scripts/python/pySetenv/packages/'))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/pySetenv/variables/' )
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/pySetenv/packages/'  )
# import userdata_template
import userdata_multipart
# print sys.path

def get_all_groups(init_groups=[]):
	for i in init_groups:
		if i == 'ssh_pwauth':
			return data[i]
		if i == 'ssh_groups' or i == 'sudo_groups':
			for j in data[i]:
				data_groups = j.split(',')
			if i == 'ssh_groups':
				return data_groups
			elif i == 'sudo_groups':
				return data_groups

def change_sshd_config_replace(ssh_config_file, ssh_group=[], ssh_pwauth=False, root_login=False):
	group_exp_replaced,passwd_yes_replaced,passwd_no_replaced,root_match_exp_replaced = False,False,False,False
	ssh_group_line 	= ''
	for line in fileinput.input(ssh_config_file, inplace=True):
		if ssh_group:
			ssh_group_line 	= 'AllowGroups ' + ' '.join(ssh_group)
		if ssh_group and group_exp.match(line):
			exsisting_grp	= line.strip().replace('AllowGroups ', '').split(' ')
			ssh_group_line 	= 'AllowGroups ' + ' '.join(sorted(list(set(ssh_group + exsisting_grp))))
			line = re.sub(r'(AllowGroups .*)',ssh_group_line,line)
			group_exp_replaced = True
		if ssh_pwauth is True:
			if passwd_no.match(line):
				line = re.sub(r'(PasswordAuthentication no)','PasswordAuthentication yes',line)
				passwd_yes_replaced = True
			if passwd_yes_comt.match(line):
				line = re.sub(r'(#PasswordAuthentication yes)','#PasswordAuthentication no',line)
				passwd_no_replaced = True
		if ssh_pwauth is False:
			if passwd_yes.match(line):
				line = re.sub(r'(PasswordAuthentication yes)','#PasswordAuthentication yes',line)
				passwd_yes_replaced = True
			if passwd_no_comt.match(line):
				line = re.sub(r'(#PasswordAuthentication no)','PasswordAuthentication no',line)
				passwd_no_replaced = True
		if not root_login:
			if root_login_yes.match(line):
				line = re.sub(r'(#PermitRootLogin yes)','PermitRootLogin no',line)
				root_match_exp_replaced = True
		if root_login is True:
			if root_login_no.match(line):
				line = re.sub(r'(PermitRootLogin no)','#PermitRootLogin yes',line)
				root_match_exp_replaced = True
		print line,
	
	#for x in [ssh_group_line, 'PasswordAuthentication yes','PermitRootLogin no']:
	for x in [ssh_group_line]:
		change_sshd_config_add(ssh_config_file, x)

def change_sshd_config_add(ssh_config_file, add_line):
	''' Below Script to write line if not found in whole file '''
	with open(ssh_config_file, 'a+') as file:
		if not any(add_line == x.strip() for x in file):
			file.write(add_line + '\n')

def add_sudo_file(sudoers_file, sudo_group=[]):
	if sudo_group:
		for item in sudo_group:
			with open(sudoers_file, 'a+') as sudoers:
				if not any("%{item} \tALL=(ALL) \tNOPASSWD: ALL\n".format(item=item) == x for x in sudoers):
					sudoers.write("%{item} \tALL=(ALL) \tNOPASSWD: ALL\n".format(item=item))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Script to Update ssh and sudoers from User-Data')
	
	parser.add_argument('URL'				,action='store_const' 	,const='http://169.254.169.254/latest/user-data',help='URL for User-Data'									)
	parser.add_argument('ssh_config_file'	,action='store_const' 	,const='/etc/ssh/sshd_config'					,help='SSH Configuration file path'							)
	parser.add_argument('sudoers_file'		,action='store_const' 	,const='/etc/sudoers'							,help='Sudoers file for all others'							)
	parser.add_argument('sudoers_file_ops'	,action='store_const' 	,const='/etc/sudoers.d/my-sudoers-config'		,help='Sudoers file for devops team'						)
	parser.add_argument('-add_ssh'			,action='append'		,dest='add_ssh'									,help='Add list of groups in SSH'		,default=[]			)
	parser.add_argument('-add_sudo'			,action='append'		,dest='add_sudo'								,help='Add list of groups in Sudoers'	,default=[]			)
	parser.add_argument('-ssh_pwauth'		,action='store_true'	,dest='ssh_pwauth'								,help='Set to switch to true'			,default=False		)
	parser.add_argument('-root_login'		,action='store_true'	,dest='root_login'								,help='Set to switch to true'			,default=False		)
	
	# arguments	= parser.parse_args(['http://169.254.169.254/latest/user-data','/etc/ssh/sshd_config','-add_ssh','-ssh','root_group','-add_sudo','-sudo','root_group'])
	arguments			= parser.parse_args()
	URL					= arguments.URL
	ssh_config_file		= arguments.ssh_config_file
	sudoers_file_ops	= arguments.sudoers_file_ops
	sudoers_file		= arguments.sudoers_file
	add_ssh				= arguments.add_ssh
	add_sudo			= arguments.add_sudo
	ssh_pwauth			= arguments.ssh_pwauth
	root_login			= arguments.root_login
	
	group_exp		= re.compile(r'(AllowGroups .*)')
	passwd_no		= re.compile(r'(PasswordAuthentication n.*)')
	passwd_yes		= re.compile(r'(PasswordAuthentication y.*)')
	passwd_no_comt	= re.compile(r'(#PasswordAuthentication n.*)')
	passwd_yes_comt	= re.compile(r'(#PasswordAuthentication y.*)')
	root_login_no	= re.compile(r'(PermitRootLogin n.*)')
	root_login_yes	= re.compile(r'(#PermitRootLogin y.*)')
	ssh_group		= []
	sudo_group		= []
	
	##########################################################################################
	############################### Automatic Cloud-Init Entry ###############################
	##########################################################################################
	try:
		data = userdata_multipart.get_cloud_config_data(URL)
		# data = userdata_template.get_cloud_config_data(URL)
		try:
			ssh_group	= get_all_groups(init_groups=['ssh_groups'])
			sudo_group	= get_all_groups(init_groups=['sudo_groups'])
			ssh_pwauth	= get_all_groups(init_groups=['ssh_pwauth'])
			root_login	= get_all_groups(init_groups=['root_login'])
		except Exception as get_groups_error:
			print get_groups_error
	except Exception as data_error:
		print data_error
	
	############################### This will work even Empty CI #############################
	try:
		change_sshd_config_replace(ssh_config_file, ssh_group=ssh_group, ssh_pwauth=ssh_pwauth, root_login=root_login)
	except Exception as change_sshd_config_error:
		print change_sshd_config_error
		exit(300)
	
	try:
		add_sudo_file(sudoers_file_ops, sudo_group=sudo_group)
	except Exception as change_sudoers_error:
		print change_sudoers_error
		exit(400)
	##########################################################################################
	############################### Custom Add SSH & Sudo ####################################
	##########################################################################################
	
	if add_ssh:
		try:
			change_sshd_config_replace(ssh_config_file, ssh_group=add_ssh, ssh_pwauth=ssh_pwauth, root_login=root_login)
		except Exception as get_groups_error:
			print get_groups_error
	
	if add_sudo:
		try:
			add_sudo_file(sudoers_file, sudo_group=add_sudo)
		except Exception as change_sshd_config_error:
			print change_sshd_config_error