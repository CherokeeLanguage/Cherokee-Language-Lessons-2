#!/bin/sh

cd "$(dirname "$0")" || exit 1

if [ ! -d src.cln ]; then mkdir src.cln; fi
rm src.cln/*

i=0
for page in src/*.JPG src/*.jpg; do
	if [ ! -f "$page" ]; then continue; fi
	i=$(($i+1))
	p="$(printf "%03d" $i)"
	echo "Processing ${page}"
	dest="src.cln/$p".png
	gm convert "$page" -filter Sinc -despeckle -resize '200%' -set histogram-threshold 3 -normalize -colorspace CMYK "$dest".tiff
	cyan=src.cln/"$p"-c.tiff
	magenta=src.cln/"$p"-m.tiff
	yellow=src.cln/"$p"-y.tiff
	black=src.cln/"$p"-k.tiff
	tmp=src.cln/"$p"-cmyk.tiff
	gm convert "$dest".tiff -channel black $black
	gm convert "$dest".tiff -channel cyan $cyan
	gm convert "$dest".tiff -channel magenta $magenta
	gm convert "$dest".tiff -channel yellow $yellow
	rm "$dest".tiff
	echo " - ${black}"
	gm mogrify -median 2 -black-threshold 150 -gamma 2 "$black"
	#gm mogrify -set histogram-threshold 3 -normalize "$black"
	for c in "$cyan" "$magenta" "$yellow"; do
		echo " - ${c}"
		gm mogrify -median 2 -blur 0x3 -gamma 0.65 "$c"
		#gm mogrify -set histogram-threshold 3 -normalize "$c"
		#gm mogrify -contrast "$c"
	done
	
	echo " - composite and convert"
	gm composite -compose CopyYellow "$yellow" "$magenta" "$tmp"
	gm composite -compose CopyBlack "$black" "$tmp" "$tmp"
	gm composite -compose CopyCyan "$cyan" "$tmp" "$tmp"
	gm convert "$tmp" -normalize "$dest"
	#gm convert "$tmp" "$dest"
	rm "$yellow"
	rm "$magenta"
	rm "$black"
	rm "$cyan"
	rm "$tmp"	
done

gm convert src.cln/*.png -filter sinc -compress JPEG -quality 30 src-cln.pdf
pdfbook --suffix 'duplex-long' src-cln.pdf

