const http = require('http');

async function triggerSync(courseId) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({ courseId });
        const options = {
            hostname: 'localhost',
            port: 3005,
            path: '/api/sync/full',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': data.length
            }
        };

        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (d) => body += d);
            res.on('end', () => {
                console.log(`Course ${courseId} Sync Status: ${res.statusCode}`);
                console.log(`Response: ${body}`);
                resolve();
            });
        });

        req.on('error', (e) => {
            console.error(`Problem with request for course ${courseId}: ${e.message}`);
            reject(e);
        });

        req.write(data);
        req.end();
    });
}

async function run() {
    const courses = [9, 10, 11, 12, 13];
    for (const id of courses) {
        await triggerSync(id);
    }
}

run();
