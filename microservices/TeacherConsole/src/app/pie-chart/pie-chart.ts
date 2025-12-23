import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-pie-chart',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="chart-container">
      <h3 class="chart-title">Distribution des Profils</h3>

      <div class="chart-wrapper">
        <svg viewBox="0 0 100 100" class="pie-svg">
           <g transform="rotate(-60 50 50)">
              <circle *ngFor="let seg of segments"
                      cx="50" cy="50" r="15.9155" fill="transparent"
                      [attr.stroke]="seg.color" stroke-width="32"
                      [attr.stroke-dasharray]="seg.dashArray"
                      [attr.stroke-dashoffset]="seg.dashOffset"
                      class="segment">
              </circle>
           </g>
        </svg>

        <div class="legend">
           <div *ngFor="let seg of segments" class="legend-item">
             <span class="indicator" [ngClass]="seg.type"></span>
             <span class="legend-label">{{ seg.label }}</span>
             <span class="legend-value">{{ seg.value }}%</span>
           </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .chart-container {
      background: white;
      border-radius: 12px;
      padding: 24px;
      border: 1px solid #E5EAF0;
      height: 100%;
      min-height: 350px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .chart-title {
      font-size: 16px; /* Matched PerformanceChart */
      font-weight: 600;
      color: #1e293b;
      margin-bottom: 24px; /* More space for the pie */
    }

    .chart-wrapper {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }

    .pie-svg {
      width: 280px; /* Further increased size */
      height: 280px;
      overflow: visible;
      margin-bottom: 20px;
    }

    .segment {
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      cursor: pointer;
    }
    .segment:hover {
      stroke-width: 34; /* Slightly larger on hover */
      opacity: 0.9;
    }

    /* Legend Styles (Copied from PerformanceChart) */
    .legend {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 16px;
      margin-top: auto;
      width: 100%;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: #64748b;
      font-weight: 500;
      min-width: 120px;
    }

    .legend-label {
      flex: 1;
    }

    .legend-value {
      font-weight: 600;
      color: #334155;
    }

    .indicator {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }

    .indicator.assidu { background: #10b981; }
    .indicator.irregulier { background: #8b5cf6; }
    .indicator.moyen { background: #f59e0b; }
    .indicator.procrastinateur { background: #ef4444; }
  `]
})
export class PieChart implements OnInit {
  segments: any[] = [];

  constructor(private readonly http: HttpClient) {}

  ngOnInit(): void {
    this.fetchData();
  }

  fetchData(): void {
    this.http.get<any[]>('http://localhost:4000/teacher/profiles-distribution', {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    }).subscribe({
      next: (data: any[]) => {
        let currentOffset = 0;
        this.segments = data.map((item: any) => {
          const dashArray = `${item.value} ${100 - item.value}`;
          const dashOffset = -currentOffset;
          currentOffset += item.value;
          return {
            ...item,
            dashArray,
            dashOffset
          };
        });
      },
      error: (err: any) => console.error('Erreur lors du chargement de la distribution des profils', err)
    });
  }
}
