<?php

require_once 'config.php';
function YAutoload($classname)
{
    $filename = dirname(__FILE__) . DIRECTORY_SEPARATOR . 'lib/'. $classname . '.php';
    echo $filename;
    if (is_readable($filename)) {
        require $filename;
    }
}
spl_autoload_register('YAutoload', true, true);
?>
