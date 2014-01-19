# to launch the sentry app, add this to the .bashrc
#sh ~/enjigo_door/croverlord.sh
#or
#bash ~/enjigo_door/croverlord.sh

#get us in the corret directory
cd ~/enjigo_door/door_interface/



function run_sentry {

	if sudo python enjigo_sentry.py; then
	    echo "Exit code of 0, success"
	else
    	echo "Exit code of $?"
    	pause_then_relaunch
	fi


}

function pause_then_relaunch {
	
	echo "Launching Sentry in 8 secs"
	echo "press q to cancel"

	COUNT=8
	while [ $COUNT -gt 0 ];
	do
	    # TASK 1
	    #date
	    read -t 1 -n 1 key

	    if [[ $key = q ]]
	    then
	        break
	    fi

	    let COUNT=COUNT-1
	    echo $COUNT

	    if [[ $COUNT -eq 0 ]]
	  	then
	  		#relaunch app
	  		echo 'relaunching'
	  		run_sentry
	  	fi
	done

}

pause_then_relaunch

