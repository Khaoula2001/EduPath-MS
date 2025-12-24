import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-stats-cards',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './stats-cards.html',
  styleUrls: ['./stats-cards.css']
})
export class StatsCards implements OnInit {
  stats: any[] = [];

  constructor(private readonly http: HttpClient) {}

  ngOnInit(): void {
    this.fetchStats();
  }

  fetchStats(): void {
    // Appel via l'API Gateway (port 4000)
    this.http.get<any>('http://localhost:4000/teacher/stats', {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    }).subscribe({
      next: (data: any) => {
        this.stats = [
          { title: 'Total Étudiants', value: data.total_students, icon: '👤', type: 'info' },
          { title: 'Moyenne Classe', value: data.average_engagement, icon: '📈', type: 'success' },
          { title: 'Étudiants à Risque', value: data.at_risk_students, icon: '⚠️', type: 'critical' },
          { title: 'Alertes Actives', value: data.active_courses, icon: '🔔', type: 'warning' }
        ];
      },
      error: (err: any) => console.error('Erreur lors du chargement des stats', err)
    });
  }
}
