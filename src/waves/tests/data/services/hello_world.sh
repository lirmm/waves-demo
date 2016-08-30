#!/bin/bash
echo "Working dir: $(pwd)"
dir=$(pwd)
sleep 1
echo "Hello world" > ${dir}/outputs/hello_world_output.txt
sleep 1
echo "Follow " $1 >> ${dir}/outputs/hello_world_output.txt
sleep 1
echo "Last" $2 >> ${dir}/outputs/hello_world_output.txt
