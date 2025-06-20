<?php
$db_path = __DIR__ . '/iptv.db';
$valid_hours = 120;

$username = $_GET['username'] ?? '';
$password = $_GET['password'] ?? '';
$type = $_GET['type'] ?? 'm3u_plus';

if (!$username || !$password) {
    http_response_code(400);
    echo "Missing username or password";
    exit;
}

try {
    $pdo = new PDO('sqlite:' . $db_path);
    $stmt = $pdo->prepare("SELECT created_at FROM users WHERE username=? AND password=?");
    $stmt->execute([$username, $password]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$row) {
        http_response_code(403);
        echo "Invalid credentials";
        exit;
    }

    $created_at = strtotime($row['created_at']);
    $expires_at = $created_at + ($valid_hours * 3600);

    if (time() > $expires_at) {
        http_response_code(410);
        echo "Token expired";
        exit;
    }

    header("Content-Type: application/octet-stream");
    echo file_get_contents("https://lkmobrqtdsac.us-west-1.clawcloudrun.com/?type=m3u");

} catch (Exception $e) {
    http_response_code(500);
    echo "Server error: " . $e->getMessage();
}
?>
