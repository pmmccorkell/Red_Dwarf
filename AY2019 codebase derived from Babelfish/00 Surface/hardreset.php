<?php

function runScript() {
	exec("pkill -f auv01min.py");
	exec("pkill -f polar.py");
	exec("python3 /home/pi/hardreset.py");
}

runScript();

?>
