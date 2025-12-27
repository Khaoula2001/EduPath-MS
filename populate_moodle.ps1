Write-Output "Checking for running Moodle container..."

$containerId = docker ps -q --filter "ancestor=moodleapp:1.0"
if (-not $containerId) {
    $containerId = docker ps -q --filter "name=moodleapp"
}

if (-not $containerId) {
    Write-Error "Moodle container is NOT running."
    exit 1
}

$containerName = docker inspect --format '{{.Name}}' $containerId
$containerName = $containerName.Trim("/")
Write-Output "Found Moodle container: $containerName"

Write-Output "Initializing Data Generator..."

docker exec -t $containerName php admin/tool/generator/cli/maketestcourse.php --shortname="TEST101" --size="S"

Write-Output "Setting password for 'student1'..."
docker exec -t $containerName php admin/cli/reset_password.php --username=student1 --password=Moodle@2025 --ignore-password-policy

Write-Output "Data Generation Complete."
