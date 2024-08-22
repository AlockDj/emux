#!bin/bash

array=(nmap apache2 php ruby nodejs pyhton3 git)
for i in "${array[@]} 
do 
   echo "Plese Enter Your Root Passwd"
   echo "Installing ..."
   sudo apt install $i
   sleep 1
   trap "echo Program Exit or Close;exit" SIGINT
 done
   
