ffmpeg -r 60 -i rerun_superopti_%%04d.png -i out1.wav -vcodec ffv1 -acodec copy encoded.avi
del *.png