import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-stats-cards',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './stats-cards.html',
  styleUrls: ['./stats-cards.css']
})
export class StatsCards {
  stats = [
    {
      title: 'Total Étudiants',
      value: '12',
      icon: '👤',
      type: 'info'
    },
    {
      title: 'Moyenne Classe',
      value: '77%',
      icon: '📈',
      type: 'success'
    },
    {
      title: 'Étudiants à Risque',
      value: '3',
      icon: '⚠️',
      type: 'warning'
    },
    {
      title: 'Alertes Actives',
      value: '2',
      icon: '🔔',
      type: 'critical'
    }
  ];
}
