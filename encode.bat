ffmpeg -r 60 -i rerun_superopti_%%04d.png -vcodec ffv1 encoded.avi
del *.png