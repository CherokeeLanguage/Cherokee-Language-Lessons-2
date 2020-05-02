#!/bin/bash

QUESTIONS=10
ANSWERS=4

echo "Q: question # to use"
echo "*: the correct answer location"
echo "N: the incorrect answer to get from question# N"

for r in $(
	for y in $(seq $(($QUESTIONS * 10))); do
		let "q = $RANDOM % $QUESTIONS + 1"
		echo "$q"
	done | awk '!seen[$0]++' 
); do
	echo "Q: $r"
	correct=0
	counter=0
	for y in $(seq $(($ANSWERS * 10))); do
		let "q = $RANDOM % $QUESTIONS + 1"
		if [ $correct = 0 ]; then
			let "s = $RANDOM % 3"
			if [ $counter = 4 ]; then s=0; fi
			if [ $s = 0 ]; then
				correct=1
				q="*"
			fi
		fi
		echo "   $q"
	done | awk '!seen[$0]++' | grep -v "$r" | head -n 4
	echo
done


