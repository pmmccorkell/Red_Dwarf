<?php
function stopScript() {
	exec("pkill -f polar.py");
}

stopScript();

?>
	
