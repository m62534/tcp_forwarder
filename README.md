######
# Overview: 
forwarder.py is a python3 program which will parse config.json, and forward traffic to a destination host

## USAGE
1. Edit config.json
2. Chmod 700 forwarder.py
3. ./forwarder.py



#########
## Testing scripts ##
1. view_socket_state.sh - Takes proxy port number as argument. Displays number of ESTABLISHED and TIME_WAIT


2. http_loadtest.inline - Establishes several connections to port 80. Must be run inline


########
## How to run tests ##
### SSH Loadtesting ###
There was more success in load testing the server with multiprocessing compared to multithreading.

1. Setup and run ssh daemon on your computer.
	1. sudo apt update
	2. sudo apt install openssh-server
	3. sudo systemctl status ssh
	4. sudo ufw allow ssh
	5. ensure that there is a username and password that you are willing to enter into script.
		sudo adduser {username}
		sudo passwd {username}
		Default:  Username is test, password is test
		NOTE:  remember to disable after testing.
	6. install net-tools if needed to get ip address of computer

2. ensure python is setup on your computer
	1. sudo apt install python3
	2. python3 -m pip install --user --upgrade pip
	3. python3 -m pip --version
                shouldd be 3.0 or higher
	4. python3 -m pip install --user virtualenv
	5. python3 -m venv <env>
		do this in the directory of the project
	6. exclude virtual environment directory in your .gitignore folder
	7. source <env>/bin/activate
		to deactivate the virtual environment, run $ deactivate
	8. to install packages, run pip install <packagename>
		pip install paramiko
		

3. edit loadtest.json with the ip address, port, username, password, number of connections and wait.

4. ssh into proxy with ssh <USERNAME>@<IPADDRESS> to test

5. TO RUN:  ./ssh_loadtester_process.py 

5. To see socket states, run the following in proxy host:  ./view_socket_state.sh <PROXYPORT#>
