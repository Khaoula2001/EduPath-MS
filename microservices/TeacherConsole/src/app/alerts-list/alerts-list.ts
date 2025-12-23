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

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.fetchAlerts();
  }

  fetchAlerts() {
    this.http.get<any[]>('http://localhost:4000/teacher/alerts', {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    }).subscribe({
      next: (data) => {
        this.alerts = data.map(a => ({
          message: `${a.student_name}: ${a.message}`,
          date: a.date,
          read: false,
          type: a.priority.toLowerCase() === 'urgent' ? 'critical' : 'warning'
        }));
      },
      error: (err) => console.error('Erreur lors du chargement des alertes', err)
    });
  }

  toggleRead(alert: any) {
    alert.read = !alert.read;
  }
}
