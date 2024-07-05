# Clear the contents of the logs file
rm ./realm_1.log 
rm ./realm_2.log

# Optional: Print a message indicating that the script has run
echo "Killing servers and clearing logs"

# Find and kill all processes that match the pattern
ps aux | grep server_thread_chat | grep -v grep | awk '{print $2}' | xargs kill -9