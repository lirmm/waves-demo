#!/bin/bash
echo "Working dir: $(pwd)"
dir=$(pwd)
sleep 1
echo "Hello world" > ${dir}/hello_world_output.txt
sleep 1
echo "Follow " $1 >> ${dir}/hello_world_output.txt
sleep 1
echo "Last" $2 >> ${dir}/hello_world_output.txt
