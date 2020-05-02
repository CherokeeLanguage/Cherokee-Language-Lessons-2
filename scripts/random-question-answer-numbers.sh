#!/bin/bash

QUESTIONS=10
ANSWERS=4

for r in $(
	for y in $(seq $(($QUESTIONS * 10))); do
		let "q = $RANDOM % $QUESTIONS + 1"
		echo "$q"
	done | awk '!seen[$0]++' 
); do
	echo "Q: $r"
	correct=0
	counter=0
	for y in $(seq $(($QUESTIONS * 10))); do
		let "q = $RANDOM % $ANSWERS + 1"
		if [ $correct = 0 ]; then
			let "s = $RANDOM % 3"
			if [ $counter = 4 ]; then s=0; fi
			if [ $s = 0 ]; then
				correct=1
				q="*"
			fi
		fi
		echo "   $q"
	done | awk '!seen[$0]++' 
	echo
done


