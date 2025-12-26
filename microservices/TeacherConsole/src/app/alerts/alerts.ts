import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { SocketService } from '../services/socket.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'app-alerts',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './alerts.html',
    styleUrls: ['./alerts.css']
})
export class Alerts implements OnInit, OnDestroy {
    selectedSeverity: string = 'Toutes les sévérités';
    selectedType: string = 'Tous les types';

    stats = [
        { label: 'Alertes Urgentes', count: 0, color: 'red', icon: 'warning' },
        { label: 'Alertes Moyennes', count: 0, color: 'orange', icon: 'error' },
        { label: 'Alertes Mineures', count: 0, color: 'yellow', icon: 'info' }
    ];

    urgentAlerts: any[] = [];
    mediumAlerts: any[] = [];
    private socketSub?: Subscription;

    constructor(
        private readonly http: HttpClient,
        private readonly socketService: SocketService
    ) { }

    ngOnInit(): void {
        this.fetchAlerts();
        this.setupSocketListener();
    }

    ngOnDestroy(): void {
        if (this.socketSub) {
            this.socketSub.unsubscribe();
        }
    }

    setupSocketListener(): void {
        this.socketSub = this.socketService.onEvent('profile_alert').subscribe((data: any) => {
            console.log('Real-time alert received via WebSocket:', data);
            const newAlert = this.mapSocketAlert(data);

            if (newAlert.priority === 'Urgent') {
                this.urgentAlerts = [newAlert, ...this.urgentAlerts];
                this.stats[0].count++;
            } else {
                this.mediumAlerts = [newAlert, ...this.mediumAlerts];
                this.stats[1].count++;
            }
        });
    }

    fetchAlerts(): void {
        this.http.get<any[]>('http://localhost:4000/api/coach/teacher/alerts', {
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
        }).subscribe({
            next: (data: any[]) => {
                this.urgentAlerts = data.filter((a: any) => a.priority === 'Urgent').map((a: any) => this.mapAlert(a));
                this.mediumAlerts = data.filter((a: any) => a.priority !== 'Urgent').map((a: any) => this.mapAlert(a));

                this.stats[0].count = this.urgentAlerts.length;
                this.stats[1].count = this.mediumAlerts.length;
            },
            error: (err: any) => console.error('Erreur lors du chargement des alertes', err)
        });
    }

    mapAlert(a: any): any {
        return {
            initials: a.student_name ? a.student_name.split(' ').map((n: string) => n[0]).join('') : 'ST',
            name: a.student_name || `Étudiant #${a.student_id}`,
            type: a.type || 'Performance',
            typeColor: this.getColorByType(a.type || 'Performance'),
            message: a.message,
            date: a.date || new Date().toLocaleString(),
            note: a.note || 'N/A',
            presence: a.presence || 'N/A',
            priority: a.priority
        };
    }

    mapSocketAlert(data: any): any {
        return {
            initials: 'ST',
            name: `Étudiant #${data.studentId}`,
            type: 'Performance',
            typeColor: 'blue',
            message: `Mise à jour profil : ${data.profileType} (Risque: ${data.riskLevel})`,
            date: new Date().toLocaleString(),
            note: 'Real-time',
            presence: 'N/A',
            priority: data.riskLevel === 'High' ? 'Urgent' : 'Moyen'
        };
    }

    getColorByType(type: string): string {
        if (type === 'Performance') return 'blue';
        if (type === 'Absence') return 'purple';
        if (type === 'Engagement') return 'green';
        return 'gray';
    }

    get filteredUrgentAlerts(): any[] {
        return this.urgentAlerts.filter(alert => {
            const matchesSeverity = this.selectedSeverity === 'Toutes les sévérités' || this.selectedSeverity === 'Urgentes';
            const matchesType = this.selectedType === 'Tous les types' || alert.type === this.selectedType;
            return matchesSeverity && matchesType;
        });
    }

    get filteredMediumAlerts(): any[] {
        return this.mediumAlerts.filter(alert => {
            const matchesSeverity = this.selectedSeverity === 'Toutes les sévérités' || this.selectedSeverity === 'Moyennes';
            const matchesType = this.selectedType === 'Tous les types' || alert.type === this.selectedType;
            return matchesSeverity && matchesType;
        });
    }

    getTypeClass(color: string): string {
        switch (color) {
            case 'blue': return 'tag-blue';
            case 'purple': return 'tag-purple';
            case 'green': return 'tag-green';
            default: return 'tag-gray';
        }
    }
}
