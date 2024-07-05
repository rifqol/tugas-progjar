#!/bin/bash

# Clear the contents of the lb_async.log file
rm ./lb_async.log

# Optional: Print a message indicating that the script has run
echo "Killing async processes and cleared lb_async.log"

# Find and kill all processes that match the pattern "async"
ps aux | grep async | grep -v grep | awk '{print $2}' | xargs kill -9


