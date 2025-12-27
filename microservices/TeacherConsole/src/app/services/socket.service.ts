import { Injectable } from '@angular/core';
import { io, Socket } from 'socket.io-client';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class SocketService {
    private socket: Socket;

    constructor() {
        // Gateway URL
        this.socket = io('http://localhost:4000');

        this.socket.on('connect', () => {
            console.log('Connected to WebSocket Gateway');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from WebSocket Gateway');
        });
    }

    onEvent(event: string): Observable<any> {
        return new Observable(observer => {
            this.socket.on(event, (data: any) => observer.next(data));

            // Cleanup on unsubscribe
            return () => {
                this.socket.off(event);
            };
        });
    }
}
