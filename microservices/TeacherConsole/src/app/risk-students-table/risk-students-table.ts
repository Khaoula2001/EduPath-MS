import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { StudentService, Student } from '../services/student.service';

@Component({
  selector: 'app-risk-students-table',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './risk-students-table.html',
  styleUrls: ['./risk-students-table.css']
})
export class RiskStudentsTable implements OnInit {
  riskStudents: any[] = [];
  isLoading = true;
  error: string | null = null;

  // États des filtres et tri
  currentSort = 'riskScore';
  sortDirection: 'asc' | 'desc' = 'desc'; // Par défaut: décroissant pour le risque
  currentFilter = 'all';
  searchTerm = '';

  constructor(private router: Router, private studentService: StudentService) { }

  ngOnInit() {
    this.loadStudents();
  }

  loadStudents() {
    this.isLoading = true;
    this.studentService.getStudents().subscribe({
      next: (data: Student[]) => {
        // Add UI state properties
        this.riskStudents = data.map(s => ({
          ...s,
          expanded: false
        }));
        this.isLoading = false;
      },
      error: (err: any) => {
        console.error('Failed to load risk students', err);
        this.error = 'Erreur lors du chargement des données.';
        this.isLoading = false;
      }
    });
  }

  viewStudentDetails(student: any) {
    this.router.navigate(['/student', student.id]);
  }

  // Options de tri
  sortOptions = [
    { value: 'riskScore', label: 'Score de risque' },
    { value: 'name', label: 'Nom' },
    { value: 'performance', label: 'Performance' },
    { value: 'lastActivity', label: 'Dernière activité' }
  ];

  // Filtres disponibles
  riskLevelFilters = [
    { value: 'all', label: 'Tous les niveaux' },
    { value: 'critique', label: 'Critique' },
    { value: 'élevé', label: 'Élevé' },
    { value: 'moyen', label: 'Moyen' },
    { value: 'faible', label: 'Faible' }
  ];

  hasExpandedStudents(): boolean {
    return this.riskStudents.some(student => student.expanded);
  }

  // Méthode pour obtenir l'étudiant expansé
  getExpandedStudent(): any {
    return this.riskStudents.find(student => student.expanded);
  }

  // Dans la classe RiskStudentsTable
  getDaysAgo(dateString: string): number {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  }

  // Données filtrées et triées
  get filteredStudents() {
    let students = [...this.riskStudents];

    // Appliquer la recherche
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      students = students.filter(student =>
        student.name.toLowerCase().includes(term) ||
        student.email.toLowerCase().includes(term)
      );
    }

    // Appliquer le filtre par niveau de risque
    if (this.currentFilter !== 'all') {
      students = students.filter(student =>
        student.riskLevel.toLowerCase() === this.currentFilter
      );
    }

    // Appliquer le tri
    students.sort((a, b) => {
      let aValue: any, bValue: any;

      switch (this.currentSort) {
        case 'name':
          aValue = a.name;
          bValue = b.name;
          break;
        case 'performance':
          aValue = a.performance;
          bValue = b.performance;
          break;
        case 'lastActivity':
          aValue = new Date(a.lastActivity);
          bValue = new Date(b.lastActivity);
          break;
        case 'riskScore':
        default:
          aValue = a.riskScore;
          bValue = b.riskScore;
          break;
      }

      if (this.sortDirection === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return students;
  }

  // Obtenir la classe CSS pour le niveau de risque
  getRiskLevelClass(level: string): string {
    const levelLower = level.toLowerCase();
    switch (levelLower) {
      case 'critique': return 'critical';
      case 'élevé': return 'high';
      case 'moyen': return 'medium';
      case 'faible': return 'low';
      default: return 'low';
    }
  }

  // Obtenir la couleur du score de risque
  getRiskScoreColor(score: number): string {
    if (score >= 80) return 'critical';
    if (score >= 60) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
  }

  // Trier les étudiants
  sortBy(field: string) {
    if (this.currentSort === field) {
      // Inverser la direction si on clique sur la même colonne
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      // Nouvelle colonne, direction par défaut
      this.currentSort = field;
      this.sortDirection = field === 'name' ? 'asc' : 'desc';
    }
  }

  // Appliquer un filtre
  applyFilter(filterValue: string) {
    this.currentFilter = filterValue;
  }

  // Toggle l'expansion d'une ligne
  toggleExpand(student: any) {
    student.expanded = !student.expanded;
  }

  // Actions disponibles pour chaque étudiant
  actions = [
    { id: 'message', label: 'Envoyer un message', icon: '✉️' },
    { id: 'meeting', label: 'Planifier un rendez-vous', icon: '📅' },
    { id: 'resources', label: 'Assigner des ressources', icon: '📚' },
    { id: 'monitor', label: 'Surveiller de près', icon: '👁️' },
    { id: 'contact', label: 'Contacter les parents', icon: '👨‍👩‍👧‍👦' }
  ];

  // Exécuter une action
  executeAction(actionId: string, student: any) {
    console.log(`Action ${actionId} exécutée pour ${student.name}`);

    // Ici vous pourriez implémenter la logique réelle
    switch (actionId) {
      case 'message':
        this.sendMessage(student);
        break;
      case 'meeting':
        this.scheduleMeeting(student);
        break;
      case 'resources':
        this.assignResources(student);
        break;
      case 'monitor':
        this.startMonitoring(student);
        break;
      case 'contact':
        this.contactParents(student);
        break;
    }
  }

  // Méthodes d'actions (à implémenter)
  private sendMessage(student: any) {
    alert(`Message envoyé à ${student.name} (${student.email})`);
  }

  private scheduleMeeting(student: any) {
    alert(`Rendez-vous planifié avec ${student.name}`);
  }

  private assignResources(student: any) {
    alert(`Ressources assignées à ${student.name}`);
  }

  private startMonitoring(student: any) {
    alert(`Surveillance activée pour ${student.name}`);
  }

  private contactParents(student: any) {
    alert(`Parents de ${student.name} contactés`);
  }

  // Statistiques
  get totalStudents() {
    return this.riskStudents.length;
  }

  get criticalCount() {
    return this.riskStudents.filter(s => s.riskLevel === 'Critique').length;
  }

  get highCount() {
    return this.riskStudents.filter(s => s.riskLevel === 'Élevé').length;
  }

  get mediumCount() {
    return this.riskStudents.filter(s => s.riskLevel === 'Moyen').length;
  }

  // Exporter les données
  exportData() {
    const data = this.filteredStudents.map(student => ({
      'Nom': student.name,
      'Email': student.email,
      'Score de risque': `${student.riskScore}%`,
      'Niveau de risque': student.riskLevel,
      'Performance': `${student.performance}%`,
      'Dernière activité': student.lastActivity
    }));

    const csv = this.convertToCSV(data);
    this.downloadCSV(csv, 'etudiants-a-risque.csv');
  }

  private convertToCSV(data: any[]): string {
    const headers = Object.keys(data[0]).join(',');
    const rows = data.map(row => Object.values(row).join(','));
    return [headers, ...rows].join('\n');
  }

  private downloadCSV(csv: string, filename: string) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  }
}
