import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-profiles',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './profiles.html',
  styleUrls: ['./profiles.css'],
})
export class Profiles {
  profileCards = [
    {
      name: 'Assidu',
      desc: 'Étudiants réguliers et performants avec un haut niveau d\'engagement',
      count: 5,
      avg: '90%',
      icon: 'check', // Green icon
      color: 'green',
      students: [
        { name: 'Omar Benali', score: '92%', initials: 'OB' },
        { name: 'Nisrine El Amrani', score: '88%', initials: 'NEA' },
        { name: 'Fatima Zahra Tazi', score: '95%', initials: 'FZT' }
      ],
      extra: 2
    },
    {
      name: 'Moyen',
      desc: 'Étudiants avec des performances stables et un engagement modéré',
      count: 4,
      avg: '74%',
      icon: 'user', // Blue icon
      color: 'blue',
      students: [
        { name: 'Khawla Idrissi', score: '72%', initials: 'KI' },
        { name: 'Youssef Alaoui', score: '75%', initials: 'YA' },
        { name: 'Imane Lahlou', score: '78%', initials: 'IL' }
      ],
      extra: 1
    },
    {
      name: 'Procrastinateur',
      desc: 'Étudiants qui reportent le travail et ont besoin de suivi',
      count: 2,
      avg: '57%',
      icon: 'clock', // Red icon
      color: 'red',
      students: [
        { name: 'Mohamed Chakir', score: '58%', initials: 'MC' },
        { name: 'Hamza Benjelloun', score: '55%', initials: 'HB' }
      ],
      extra: 0
    },
    {
      name: 'Irrégulier',
      desc: 'Étudiants avec des performances fluctuantes nécessitant attention',
      count: 1,
      avg: '62%',
      icon: 'shuffle', // Purple icon
      color: 'purple',
      students: [
        { name: 'Amine Fassi', score: '62%', initials: 'AF' }
      ],
      extra: 0
    }
  ];

  characteristics = [
    {
      title: 'Assidu',
      color: 'green', // Green border/bg
      points: [
        'Présence régulière (>90%)',
        'Devoirs toujours complétés',
        'Engagement élevé en classe',
        'Notes supérieures à 85%'
      ]
    },
    {
      title: 'Moyen',
      color: 'blue',
      points: [
        'Présence correcte (80-90%)',
        'Devoirs généralement faits',
        'Participation modérée',
        'Notes entre 70-85%'
      ]
    },
    {
      title: 'Procrastinateur',
      color: 'red',
      points: [
        'Rendus souvent en retard',
        'Présence variable (<70%)',
        'Travail de dernière minute',
        'Notes inférieures à 65%'
      ]
    },
    {
      title: 'Irrégulier',
      color: 'purple',
      points: [
        'Performance fluctuante',
        'Engagement imprévisible',
        'Absences sporadiques',
        'Notes variables'
      ]
    }
  ];

  getIconClass(color: string) {
    switch (color) {
      case 'green': return 'bg-green-100 text-green-600';
      case 'blue': return 'bg-blue-100 text-blue-600';
      case 'red': return 'bg-red-100 text-red-600';
      case 'purple': return 'bg-purple-100 text-purple-600';
      default: return 'bg-gray-100';
    }
  }
}
