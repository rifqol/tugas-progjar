#!/bin/bash

# Clear the contents of the lb_async.log file
rm ./lb_process.log

# Optional: Print a message indicating that the script has run
echo "Killing thread processes and cleared lb_process.log"

# Find and kill all processes that match the pattern "process"
ps aux | grep process | grep -v grep | awk '{print $2}' | xargs kill -9


