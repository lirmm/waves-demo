#!/bin/bash
echo "Stdout message"

sleep 1
echo "Hello world" > outputs/hello_world_output.txt
sleep 1
echo "Follow " $1 >> outputs/hello_world_output.txt
sleep 1
echo "Last" $2 >> outputs/hello_world_output.txt
