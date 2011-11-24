ffmpeg -r 60 -i rerun_superopti_%04d.png -i rerun_superopti.wav -vcodec ffv1 -acodec copy encoded.avi
rm *.png