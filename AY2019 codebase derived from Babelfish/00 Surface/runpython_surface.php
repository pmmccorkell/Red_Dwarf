<?php

function runScript() {
	exec("pkill -f auv01min");
	exec("pkill -f polar.py");
	exec("python3 /home/pi/auv01min_surface.py");
}

runScript();

?>
