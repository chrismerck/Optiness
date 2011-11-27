#!/bin/sh
ffmpeg -pass 1 -r 60 -i rerun_superopti_%04d.png -vpre libvpx-360p -b 1700k -an -f webm -threads 0 encoded.webm
ffmpeg -pass 2 -r 60 -i rerun_superopti_%04d.png -vpre libvpx-360p -b 1700k -i rerun_superopti.wav -acodec libvorbis -ab 128k -ar 44100 -threads 0 -y encoded.webm
rm rerun_superopti_*.png
rm ffmpeg2pass-*.log