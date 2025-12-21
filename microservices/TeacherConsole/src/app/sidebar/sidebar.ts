import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.html',
  styleUrls: ['./sidebar.css']
})
export class Sidebar {  // Garder "Sidebar" comme nom de classe
  menuItems = [
    { label: 'Tableau de bord', route: '/dashboard', icon: 'grid_view' }, // Using Material Icon text or similar
    { label: 'Étudiants', route: '/students', icon: 'people' },
    { label: 'Alertes', route: '/alerts', icon: 'warning' },
    { label: 'Profils', route: '/profiles', icon: 'bar_chart' },
    { label: 'Ressources', route: '/resources', icon: 'menu_book' }
  ];
}
