import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Location } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
    selector: 'app-student-detail',
    standalone: true,
    imports: [CommonModule, RouterModule],
    templateUrl: './student-detail.html',
    styleUrls: ['./student-detail.css']
})
export class StudentDetail {
    constructor(private location: Location) { }

    goBack() {
        this.location.back();
    }
    student = {
        name: 'Anas Moussaoui',
        email: 'anas.moussaoui@etudiant.fr',
        lastActivity: '2025-12-03',
        riskLevel: 'Critique',
        riskScore: 90,
        performance: 35,
        attendance: 45,
        engagement: 25,
        cluster: 'struggling'
    };

    prediction = {
        message: 'Tendance à la baisse détectée.',
        probability: 90,
        timeframe: '7 prochains jours',
        status: 'critical'
    };

    alerts = [
        { date: '2025-12-08', message: 'Engagement critique - Intervention urgente recommandée', level: 'high' },
        { date: '2025-12-07', message: 'Taux de présence en dessous du seuil acceptable', level: 'high' },
        { date: '2025-12-06', message: 'Risque d\'échec très élevé détecté par PathPredictor', level: 'critical' }
    ];

    recommendations = [
        { title: 'Tutorat individuel', description: 'Organiser des sessions de soutien personnalisées 2x par semaine', type: 'intervention' },
        { title: 'Ressources adaptées', description: 'Proposer des contenus de niveau débutant avec progression graduelle', type: 'resource' },
        { title: 'Entretien de suivi', description: 'Planifier un rendez-vous pour discuter des difficultés rencontrées', type: 'meeting' }
    ];

    // Evolution Chart Data (Mock)
    chartWeeks = ['2025-11-01', '2025-11-08', '2025-11-15', '2025-11-22', '2025-11-29', '2025-12-06'];
    chartSeries = [
        { name: 'Performance', color: '#3b82f6', data: [75, 76, 74, 73, 72, 70] }, // Blue
        { name: 'Engagement', color: '#a855f7', data: [80, 78, 70, 65, 55, 50] }, // Purple
        { name: 'Temps passé (min)', color: '#10b981', data: [120, 110, 105, 95, 90, 85] } // Green
    ];

    viewBoxWidth = 800;
    viewBoxHeight = 300;
    padding = 40;

    getLinePath(data: number[]): string {
        const chartHeight = this.viewBoxHeight - (this.padding * 2);
        const chartWidth = this.viewBoxWidth - (this.padding * 2);
        const xStep = chartWidth / (this.chartWeeks.length - 1);
        const yRatio = chartHeight / 100;

        const points = data.map((val, index) => {
            const x = this.padding + (index * xStep);
            const y = this.viewBoxHeight - this.padding - (val * yRatio);
            return [x, y];
        });

        return this.getSmoothPath(points);
    }

    private getSmoothPath(points: number[][]): string {
        if (points.length < 2) return '';
        let d = `M ${points[0][0]} ${points[0][1]}`;
        for (let i = 0; i < points.length - 1; i++) {
            const cp1x = points[i][0] + (points[i + 1][0] - points[i][0]) / 2;
            const cp1y = points[i][1];
            const cp2x = points[i][0] + (points[i + 1][0] - points[i][0]) / 2;
            const cp2y = points[i + 1][1];
            d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${points[i + 1][0]} ${points[i + 1][1]}`;
        }
        return d;
    }
}
