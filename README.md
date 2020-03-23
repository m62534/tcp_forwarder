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
