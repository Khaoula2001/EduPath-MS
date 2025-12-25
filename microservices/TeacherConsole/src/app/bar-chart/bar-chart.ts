import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-bar-chart',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bar-chart-container">
      <div class="chart-header">
        <h3 class="chart-title">Distribution des Notes</h3>
        <p class="chart-subtitle">Répartition par tranches de notes</p>
      </div>

      <div class="chart-body">
        <!-- Y Axis Labels -->
        <div class="y-axis">
          <span>{{ maxVal }}</span>
          <span>{{ maxVal * 0.75 | number:'1.0-0' }}</span>
          <span>{{ maxVal * 0.5 | number:'1.0-0' }}</span>
          <span>{{ maxVal * 0.25 | number:'1.0-0' }}</span>
          <span>0</span>
        </div>

        <!-- Chart Area -->
        <div class="chart-graph">
          <!-- Horizontal Grid Lines -->
          <div class="grid-lines">
             <div class="grid-line"></div>
             <div class="grid-line"></div>
             <div class="grid-line"></div>
             <div class="grid-line"></div>
             <div class="grid-line"></div> <!-- Base line -->
          </div>

          <!-- Bars -->
          <div class="bars-wrapper">
            <div *ngFor="let bar of bars; let i = index" class="bar-group">
               <div class="bar-track">
                  <div class="bar"
                       [style.height.%]="(bar.value / maxVal) * 100"
                       [style.background-color]="getBarColor(i)">
                  </div>
               </div>
               <div class="x-label">{{ bar.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .bar-chart-container {
      background: white;
      border: 1px solid #E5EAF0; /* Requested color */
      border-radius: 12px;
      padding: 24px;
      padding-bottom: 12px; /* Reduced bottom padding to remove "bande parasite" */
      height: 100%;
      min-height: 350px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); /* Soft shadow */
    }

    .chart-header {
      margin-bottom: 24px;
    }

    .chart-title {
      font-size: 16px;
      font-weight: 700;
      color: #1e293b;
      margin: 0 0 4px 0;
    }

    .chart-subtitle {
     font-size: 12px;
     color: #94a3b8;
     margin: 0;
    }

    .chart-body {
      flex: 1;
      display: flex;
      gap: 16px;
    }

    .y-axis {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      color: #94a3b8;
      font-size: 12px;
      padding-bottom: 24px; /* Space for X labels */
      font-weight: 500;
    }

    .chart-graph {
      flex: 1;
      position: relative;
      display: flex;
      flex-direction: column;
    }

    .grid-lines {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 24px; /* X label space */
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      z-index: 0;
    }

    .grid-line {
      width: 100%;
      height: 1px;
      background: #f1f5f9;
      border-top: 1px dashed #e2e8f0;
    }

    /* Make the bottom line solid if preferred, or all uniform dashed as per image */
    .grid-line:last-child {
      border-top: 1px solid #e2e8f0;
    }

    .bars-wrapper {
      flex: 1;
      display: flex;
      justify-content: space-between; /* Balanced spacing */
      align-items: flex-end;
      padding-bottom: 24px; /* X label space to align bars on bottom line */
      z-index: 1;
      position: relative;
      padding-left: 10px;
      padding-right: 10px;
    }

    .bar-group {
      flex: 1;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      align-items: center;
      position: relative;
    }

    .bar-track {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      /* Hover effect container area could go here */
    }

    .bar {
      width: 45px; /* Wider bars */
      border-radius: 4px 4px 0 0;
      transition: height 0.4s ease, opacity 0.2s, background-color 0.2s;
      opacity: 0.85;
    }

    /* Hover effect */
    .bar-group:hover .bar {
      opacity: 0.9;
    }

    /* Background highlight on hover */
    .bar-group::before {
      content: '';
      position: absolute;
      top: -5px;
      bottom: 20px;
      left: -5px;
      right: -5px;
      background: #f8fafc;
      border-radius: 6px;
      opacity: 0;
      transition: opacity 0.2s;
      z-index: -1;
    }

    .bar-group:hover::before {
      opacity: 1;
    }

    .x-label {
      position: absolute;
      bottom: -24px;
      font-size: 11px;
      color: #64748b;
      white-space: nowrap;
      text-align: center;
      width: 100%;
    }
  `]
})
export class BarChart implements OnInit {
  bars: any[] = [];
  maxVal = 5;

  constructor(private readonly http: HttpClient) {}

  ngOnInit(): void {
    this.fetchData();
  }

  fetchData(): void {
    this.http.get<any[]>('http://localhost:4000/teacher/grades-distribution', {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    }).subscribe({
      next: (data: any[]) => {
        this.bars = data;
        this.maxVal = Math.max(...data.map((b: any) => b.value), 1);
        // Ensure maxVal is nice for axis (multiples of 4)
        if (this.maxVal % 4 !== 0) {
          this.maxVal = this.maxVal + (4 - (this.maxVal % 4));
        }
      },
      error: (err: any) => console.error('Erreur lors du chargement de la distribution des notes', err)
    });
  }

  getBarColor(index: number): string {
    const colors = ['#94a3b8', '#64748b', '#3b82f6', '#2563eb', '#1d4ed8', '#1e40af'];
    return colors[index % colors.length];
  }
}
