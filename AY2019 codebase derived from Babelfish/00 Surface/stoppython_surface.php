<?php
function stopScript() {
	exec("pkill -f auv01min");
}

stopScript();

?>
	
