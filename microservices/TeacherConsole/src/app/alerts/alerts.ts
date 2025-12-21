import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
    selector: 'app-alerts',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './alerts.html',
    styleUrls: ['./alerts.css']
})
export class Alerts {
    selectedSeverity: string = 'Toutes les sévérités';
    selectedType: string = 'Tous les types';

    stats = [
        { label: 'Alertes Urgentes', count: 2, color: 'red', icon: 'warning' },
        { label: 'Alertes Moyennes', count: 3, color: 'orange', icon: 'error' },
        { label: 'Alertes Mineures', count: 0, color: 'yellow', icon: 'info' }
    ];

    urgentAlerts = [
        {
            initials: 'MC',
            name: 'Mohamed Chakir',
            type: 'Performance',
            typeColor: 'blue',
            message: 'Note inférieure à 60% - Intervention recommandée',
            date: '2025-12-19',
            note: '58%',
            presence: '65%',
            priority: 'Urgent'
        },
        {
            initials: 'HB',
            name: 'Hamza Benjelloun',
            type: 'Absence',
            typeColor: 'purple',
            message: 'Taux de présence faible (60%) - Contact nécessaire',
            date: '2025-12-18',
            note: '55%',
            presence: '60%',
            priority: 'Urgent'
        }
    ];

    mediumAlerts = [
        {
            initials: 'AF',
            name: 'Amine Fassi',
            type: 'Engagement',
            typeColor: 'green',
            message: 'Engagement en baisse - Suivi recommandé',
            date: '2025-12-17',
            note: '62%',
            presence: '70%',
            priority: 'Moyen'
        },
        {
            initials: 'KI',
            name: 'Khawla Idrissi',
            type: 'Performance',
            typeColor: 'blue',
            message: 'Performance en baisse légère',
            date: '2025-12-16',
            note: '72%',
            presence: '85%',
            priority: 'Moyen'
        },
        {
            initials: 'YA',
            name: 'Youssef Alaoui',
            type: 'Absence',
            typeColor: 'purple',
            message: 'Absences récentes détectées',
            date: '2025-12-15',
            note: '75%',
            presence: '80%',
            priority: 'Moyen'
        }
    ];

    get filteredUrgentAlerts() {
        return this.urgentAlerts.filter(alert => {
            const matchesSeverity = this.selectedSeverity === 'Toutes les sévérités' || this.selectedSeverity === 'Urgentes';
            const matchesType = this.selectedType === 'Tous les types' || alert.type === this.selectedType;
            return matchesSeverity && matchesType;
        });
    }

    get filteredMediumAlerts() {
        return this.mediumAlerts.filter(alert => {
            const matchesSeverity = this.selectedSeverity === 'Toutes les sévérités' || this.selectedSeverity === 'Moyennes';
            const matchesType = this.selectedType === 'Tous les types' || alert.type === this.selectedType;
            return matchesSeverity && matchesType;
        });
    }

    getTypeClass(color: string) {
        switch (color) {
            case 'blue': return 'tag-blue';
            case 'purple': return 'tag-purple';
            case 'green': return 'tag-green';
            default: return 'tag-gray';
        }
    }
}
