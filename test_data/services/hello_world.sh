#!/bin/bash

rm ./outputs//hello_world_output.txt
echo "Stdout message"

sleep 1
echo "Hello world" > hello_world_output.txt
sleep 1
echo "Follow " $1 >> hello_world_output.txt
sleep 1
echo "Last" $2 >> hello_world_output.txt
