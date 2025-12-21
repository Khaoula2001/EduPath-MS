import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-alerts-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './alerts-list.html',
  styleUrls: ['./alerts-list.css']
})
export class AlertsList {
  alerts = [
    {
      message: 'Anas Moussaoui n\'a pas été actif depuis 5 jours',
      date: '2025-12-08',
      read: false,
      type: 'critical'
    },
    {
      message: 'Fatima Zahra a raté 3 devoirs consécutifs',
      date: '2025-12-07',
      read: false,
      type: 'critical'
    },
    {
      message: 'Mohamed Amine montre des signes de désengagement',
      date: '2025-12-07',
      read: false,
      type: 'warning'
    },
    {
      message: 'Yassine Tahiri a un taux de complétion des exercices de 40%',
      date: '2025-12-06',
      read: false,
      type: 'warning'
    },
    {
      message: '8 étudiants n\'ont pas consulté le dernier cours',
      date: '2025-12-06',
      read: false,
      type: 'info'
    }
  ];

  toggleRead(alert: any) {
    alert.read = !alert.read;
  }
}
