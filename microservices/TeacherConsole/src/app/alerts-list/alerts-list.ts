import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-alerts-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './alerts-list.html',
  styleUrls: ['./alerts-list.css']
})
export class AlertsList implements OnInit {
  alerts: any[] = [];

  constructor(private readonly http: HttpClient) {}

  ngOnInit(): void {
    this.fetchAlerts();
  }

  fetchAlerts(): void {
    this.http.get<any[]>('http://localhost:4000/teacher/alerts', {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    }).subscribe({
      next: (data: any[]) => {
        this.alerts = data.map((a: any) => ({
          message: `${a.student_name}: ${a.message}`,
          date: a.date,
          read: false,
          type: a.priority.toLowerCase() === 'urgent' ? 'critical' : 'warning'
        }));
      },
      error: (err: any) => console.error('Erreur lors du chargement des alertes', err)
    });
  }

  toggleRead(alert: any): void {
    alert.read = !alert.read;
  }
}
