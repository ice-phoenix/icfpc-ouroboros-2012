#/bin/bash

simul="../bot/simul"

for solver in `find solvers -type f -executable`; do

    echo "Testing $solver:"

    for map in `find maps -type f -name "map*"`; do

	echo "Map: $map"

        timeout -s INT -k 10 140 "$solver" < "$map" &> path
        res=$?
        if [ $res -eq 0 ]; then
    	    echo -n "OK! "
    	    cat path
    	elif [ $res -eq 124 ]; then
    	    echo -n "TIMED OUT! "
    	    cat path
    	elif [ $res -eq 137 ]; then
    	    echo -n "KILLED! "
    	    cat path
    	else
    	    echo "FAILED!"
    	    continue
    	fi
    	echo "Simulating..."
    	$simul $map path
    done
done
