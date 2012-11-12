#/bin/bash

simul="../bot/simul"

msg=""

for solver in `find solvers -type f -executable`; do

    echo -e "\e[00;36mTesting $solver:\e[00m"
    msg+="$solver "
    total=0

    for map in `find maps -type f -name "map*"`; do

        echo -e "\e[00;31mMap: $map\e[00m"

        timeout -s INT -k 10 140 "$solver" < "$map" 1> path 2> /dev/null
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
            msg+="FAILED! "
        fi
        echo "Simulating..."
        score=`$simul $map path`

        set -- $score

        echo "$score"
        msg+="$score "
        total=$(($total + $1))
    done

    msg+="$total"
    msg+="\n"

done

echo -e "\n$msg"
