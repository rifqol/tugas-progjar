# Optional: Print a message indicating that the script has run
echo "Starting servers and logs"

nohup python3 server_thread_chat.py 8000 > realm_1.log &
nohup python3 server_thread_chat.py 8001 > realm_2.log &