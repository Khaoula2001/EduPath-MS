# Script to populate Moodle Docker Container with Test Data
# Robust version to handle container naming and retries

Write-Output "🔍 Checking for running Moodle container..."

# Try to find container by image name or partial name
$containerId = docker ps -q --filter "ancestor=moodleapp:1.0"
if (-not $containerId) {
    $containerId = docker ps -q --filter "name=moodleapp"
}

if (-not $containerId) {
    Write-Error "❌ Moodle container is NOT running." 
    Write-Output "Please check 'docker ps -a' to see if it crashed."
    Write-Output "You might need to rebuild: docker-compose up -d --build moodleapp"
    exit 1
}

$containerName = docker inspect --format '{{.Name}}' $containerId
$containerName = $containerName.Trim("/")
Write-Output "✅ Found Moodle container: $containerName"

Write-Output "🚀 Initializing Data Generator in $containerName..."

# 1. Create a Test Course
# We use 'try' because sometimes Moodle is still initializing
try {
    Write-Output "   Creating Test Course (Shortname: TEST101)..."
    docker exec -t $containerName php admin/tool/generator/cli/maketestcourse.php --shortname="TEST101" --size="S"
    if ($LASTEXITCODE -eq 0) {
        Write-Output "   ✅ Course created successfully."
    } else {
        Write-Warning "   ⚠️  Data generation exited with code $LASTEXITCODE. (Course might already exist)"
    }
} catch {
    Write-Error "   ❌ Failed to execute command in container. Is Moodle fully started?"
}

Write-Output "`n-------------------------------------------"
Write-Output "🎉 Data Generation Attempt Complete."
Write-Output "If effective, you can now trigger the Sync via Postman:"
Write-Output "POST http://localhost:3001/api/sync/full"
Write-Output "-------------------------------------------"
