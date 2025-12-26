const amqp = require('amqplib');

class MessengerService {
    constructor() {
        this.url = process.env.RABBITMQ_URL || 'amqp://edupath:edupath@rabbitmq:5672';
        this.queue = 'student_features_updated';
        this.connection = null;
        this.channel = null;
    }

    async init() {
        try {
            if (!this.connection) {
                this.connection = await amqp.connect(this.url);
                this.channel = await this.connection.createChannel();
                await this.channel.assertQueue(this.queue, { durable: true });
                console.log(`[RabbitMQ] Connected to ${this.url} and queue ${this.queue} asserted.`);
            }
        } catch (error) {
            console.error('[RabbitMQ] Connection error:', error.message);
        }
    }

    async publishUpdate(data) {
        try {
            await this.init();
            if (this.channel) {
                const msg = JSON.stringify(data);
                this.channel.sendToQueue(this.queue, Buffer.from(msg), { persistent: true });
                console.log(`[RabbitMQ] Published update for student ${data.studentId}`);
            }
        } catch (error) {
            console.error('[RabbitMQ] Publishing error:', error.message);
        }
    }
}

module.exports = new MessengerService();
