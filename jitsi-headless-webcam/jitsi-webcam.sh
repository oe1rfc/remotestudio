#!/bin/sh

DISPLAY=:0

# mute chromium a few seconds after startup.
( sleep 5; pacmd set-sink-input-mute $(pacmd list-sink-inputs | awk '$1 == "index:" {idx = $2}; $1 == "application.name" && $3 == "\"Chromium\"" {print idx; exit}' ) 1) &
xvfb-run --auto-servernum --server-num=1 chromium --disable-infobars --use-fake-ui-for-media-stream --kiosk --temp-profile jitsi-webcam.html
