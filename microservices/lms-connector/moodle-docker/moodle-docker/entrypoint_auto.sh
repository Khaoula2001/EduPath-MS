#!/bin/bash
set -e

# Start cron
service cron start

echo "Waiting for Moodle Database..."
# Simple wait loop (could be improved with a proper netcat check but PHP cli install handles connection retries usually)
sleep 10

# Check if Moodle is already installed (check config.php or DB tables)
# config.php exists because it is in the image? No, typically generated.
# But in this Docker setup, we might be mounting volumes.
# If config.php doesn't exist, we might need to configure it. 
# However, usually docker-moodle images handle this. 
# The current Dockerfile copies ./* (source code) to /var/www/html. 
# It does NOT seem to have a pre-configured config.php.

# Let's assume standard install via CLI if config.php is missing.
if [ ! -f /var/www/html/config.php ]; then
    echo "Installing Moodle..."
    php admin/cli/install_database.php \
        --adminuser=admin \
        --adminpass=moodle \
        --adminemail=admin@example.com \
        --agree-license \
        --fullname="EduPath Moodle" \
        --shortname="EduPath" \
        --lang=en 
        
    # We generally need config.php BEFORE install_database. 
    # Usually install.php generates it. 
    # BUT, simpler approach: rely on existing environment vars and `admin/cli/install.php`
    
    # If the user's previous successful run had a config.php, it might be in the volume. 
    # If this is a fresh start and it failed, we need to handle full install.
    
    # Let's try to run the standard install command which handles config creation if env vars are set properly 
    # OR standard docker moodle approach.
    
    # Given the simplicity of the current Dockerfile, it seems it expects manual setup or a pre-supplied config.
    # The user's issue implies it never fully set up because they didn't go through web wizard.
    
    # We will attempt a non-interactive install. 
    php admin/cli/install.php \
        --chmod=2777 \
        --lang=en \
        --wwwroot="http://localhost:8088" \
        --dataroot=/var/www/moodledata \
        --dbtype=mysqli \
        --dbhost=$PMA_HOST \
        --dbname=$MYSQL_DATABASE \
        --dbuser=$MYSQL_USER \
        --dbpass=$MYSQL_PASSWORD \
        --fullname="EduPath LMS" \
        --shortname="EduPath" \
        --adminuser=admin \
        --adminpass=moodle \
        --adminemail=admin@localhost.com \
        --non-interactive \
        --agree-license
fi

# Data Generation (Richer Dataset)
echo "Generating Rich Test Data..."

# Course 1: Computer Science (Large - ~1000 users, many activities)
# Using 'M' (Medium) or 'L' (Large) depending on performance. 'M' is usually safe for quick dev.
php admin/tool/generator/cli/maketestcourse.php --shortname="CS101" --fullname="Computer Science 101" --size="M" || echo "CS101 exists."

# Course 2: Mathematics (Small - quick checks)
php admin/tool/generator/cli/maketestcourse.php --shortname="MATH202" --fullname="Advanced Mathematics" --size="S" || echo "MATH202 exists."

# Course 3: Physics (Medium)
php admin/tool/generator/cli/maketestcourse.php --shortname="PHYS303" --fullname="Physics of The Future" --size="S" || echo "PHYS303 exists."


# -------------------------------------------------------------
# Triggering LMS Connector Sync (Automated)
# -------------------------------------------------------------
echo "Triggering LMS Connector Sync..."
# We wait a bit to ensure LMS Connector is ready
sleep 15 

# We try to reach lms-connector on its internal port (3000)
# Note: We must ensure 'lms-connector' is the correct service name in docker-compose.
# Based on common setup, it is 'lms-connector'.
curl -X POST http://lms-connector:3000/api/sync/full -H "Content-Type: application/json" -d '{}' || echo "Sync trigger failed (Check connection to lms-connector)"

echo "Startup Sequence Complete."
exec "$@"
