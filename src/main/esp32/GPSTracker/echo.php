<?php
# example reading the values from GPSTracker. you can deploy it e.g. in Apache
function saveValues($mysqli)
{
    $date2 = new DateTimeImmutable();
    $date = $date2->format('Y-m-d H:i:s');
    if (isset($_GET['lat'])) {
        $lat = $_GET['lat'];
    }
    if (isset($_GET['lon'])) {
        $lon = $_GET['lon'];
    }
    if (isset($_GET['alt'])) {
        $alt = $_GET['alt'];
    }
    if (isset($_GET['spd'])) {
        $spd = $_GET['spd'];
    }
    if (isset($_GET['vol'])) {
        $vol = $_GET['vol'];
    }
    if (isset($_GET['tmp'])) {
        $tmp = $_GET['tmp'];
    }
    $line = $date . " lat: " . $lat . " lon : " . $lon . " alt: " . $alt . " spd: " . $speed . " vol: " . $voltage . " temperature: " . $tmp . "\n";
    print $line;
}
?>