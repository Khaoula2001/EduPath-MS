import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-risk-heatmap',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="heatmap-container">
      <h3 class="section-title">Carte des Risques par Étudiant</h3>
      <div class="heatmap-grid">
        <div *ngFor="let student of students" class="student-card">
          <div class="avatar-ring" [ngClass]="student.riskLevel">
            <div class="avatar-circle">
               {{ getInitials(student.name) }}
            </div>
            <div class="risk-badge" [ngClass]="student.riskLevel">
               {{ student.riskScore }}%
            </div>
          </div>
          <div class="student-name">{{ student.name }}</div>
          <div class="risk-label" [ngClass]="student.riskLevel">
            Risque {{ getRiskLabel(student.riskLevel) }}
          </div>
        </div>
      </div>

      <!-- Legend -->
      <div class="heatmap-legend">
         <div class="legend-item"><span class="dot low"></span> Risque Faible</div>
         <div class="legend-item"><span class="dot medium"></span> Risque Moyen</div>
         <div class="legend-item"><span class="dot high"></span> Risque Élevé</div>
         <div class="legend-item"><span class="dot critical"></span> Risque Critique</div>
      </div>
    </div>
  `,
  styles: [`
    .heatmap-container {
      background: white; /* Restored white background */
      border: 1px solid #E5EAF0; /* Consistent border */
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); /* Consistent shadow */
    }
    .section-title {
      font-size: 16px;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 24px;
    }
    .heatmap-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); /* Increased min-width for wider cards */
      gap: 20px;
    }
    .student-card {
      background: #ffffff;
      border: 1px solid #f1f5f9;
      border-radius: 12px;
      padding: 24px 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      overflow: hidden;
    }
    .student-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .avatar-ring {
      position: relative;
      margin-bottom: 16px;
      padding: 4px;
      border-radius: 50%;
    }

    .avatar-circle {
      width: 56px; /* Slightly larger */
      height: 56px;
      border-radius: 50%;
      background: #f1f5f9;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      color: #475569;
      font-size: 16px;
      border: 3px solid white;
    }

    /* Ring colors */
    .avatar-ring.low { background: #dcfce7; }
    .avatar-ring.medium { background: #fef3c7; }
    .avatar-ring.high { background: #ffedd5; }
    .avatar-ring.critical { background: #fee2e2; }

    .avatar-ring.low .avatar-circle { color: #166534; }
    .avatar-ring.critical .avatar-circle { color: #991b1b; }

    .risk-badge {
      position: absolute;
      bottom: -4px;
      right: -8px;
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 12px;
      color: white;
      font-weight: 700;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .risk-badge.low { background: #22c55e; }
    .risk-badge.medium { background: #eab308; } /* Adjusted yellow/orange */
    .risk-badge.high { background: #f97316; }
    .risk-badge.critical { background: #ef4444; }

    .student-name {
      font-size: 14px;
      font-weight: 600;
      color: #1e293b;
      text-align: center;
      margin-bottom: 6px;
    }

    .risk-label {
      font-size: 12px;
      font-weight: 500;
    }
    .risk-label.low { color: #16a34a; }
    .risk-label.medium { color: #ca8a04; }
    .risk-label.high { color: #ea580c; }
    .risk-label.critical { color: #dc2626; }

    .heatmap-legend {
      display: flex;
      justify-content: center;
      gap: 32px;
      margin-top: 32px;
    }
    .legend-item { font-size: 12px; color: #64748b; display: flex; align-items: center; gap: 8px; font-weight: 500; }
    .dot { width: 10px; height: 10px; border-radius: 50%; }
    .dot.low { background: #22c55e; }
    .dot.medium { background: #eab308; }
    .dot.high { background: #f97316; }
    .dot.critical { background: #ef4444; }
  `]
})
export class RiskHeatmap implements OnInit {
  students: any[] = [];

  constructor(private readonly http: HttpClient) {}

  ngOnInit(): void {
    this.fetchData();
  }

  fetchData(): void {
    this.http.get<any[]>('http://localhost:4000/teacher/risk-heatmap', {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    }).subscribe({
      next: (data: any[]) => {
        this.students = data;
      },
      error: (err: any) => console.error('Erreur lors du chargement de la carte des risques', err)
    });
  }

  getInitials(name: string): string {
    if (!name) return '';
    return name.split(' ').map(n => n[0]).join('').substring(0, 2);
  }

  getRiskLabel(level: string): string {
    const labels: any = { low: 'Faible', medium: 'Moyen', high: 'Élevé', critical: 'Critique' };
    return labels[level] || level;
  }
}
