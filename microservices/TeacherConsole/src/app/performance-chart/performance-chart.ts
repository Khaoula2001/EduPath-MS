import { Component, ElementRef, ViewChild, AfterViewInit, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-performance-chart',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="chart-container">
      <h3 class="chart-title">Évolution des Performances</h3>

      <div class="chart-wrapper">
        <!-- SVG Layout -->
        <svg class="chart-svg" viewBox="0 0 600 300" preserveAspectRatio="none">
           <!-- Grid Lines (Horizontal) -->
           <g class="grid-y">
             <line *ngFor="let tick of yTicks" x1="40" [attr.y1]="getY(tick)" x2="580" [attr.y2]="getY(tick)" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4"/>
           </g>

            <!-- Grid Lines (Vertical) -->
           <g class="grid-x">
             <line *ngFor="let week of xLabels; let i = index"
                   [attr.x1]="getX(i)" y1="20"
                   [attr.x2]="getX(i)" y2="250"
                   stroke="#f1f5f9" stroke-width="1" stroke-dasharray="2"/>
           </g>

           <!-- Paths -->
           <path [attr.d]="getPath(dataPresence)" fill="none" stroke="#a855f7" stroke-width="2" />
           <path [attr.d]="getPath(dataEngagement)" fill="none" stroke="#10b981" stroke-width="2" />
           <path [attr.d]="getPath(dataMoyenne)" fill="none" stroke="#3b82f6" stroke-width="2" />

           <!-- Dots -->
           <!-- Moyenne (Blue) -->
           <circle *ngFor="let val of dataMoyenne; let i = index"
                   [attr.cx]="getX(i)" [attr.cy]="getY(val)" r="4" fill="white" stroke="#3b82f6" stroke-width="2"
                   class="dot" (mouseenter)="showTooltip($event, i, 'Moyenne', val)"/>

           <!-- Engagement (Green) -->
           <circle *ngFor="let val of dataEngagement; let i = index"
                   [attr.cx]="getX(i)" [attr.cy]="getY(val)" r="4" fill="white" stroke="#10b981" stroke-width="2"
                   class="dot" (mouseenter)="showTooltip($event, i, 'Engagement', val)"/>

           <!-- Presence (Purple) -->
           <circle *ngFor="let val of dataPresence; let i = index"
                   [attr.cx]="getX(i)" [attr.cy]="getY(val)" r="4" fill="white" stroke="#a855f7" stroke-width="2"
                   class="dot" (mouseenter)="showTooltip($event, i, 'Présence', val)"/>

           <!-- Axis Labels -->
           <g class="labels-x">
             <text *ngFor="let week of xLabels; let i = index" [attr.x]="getX(i)" y="270" text-anchor="middle" font-size="11" fill="#64748b">{{ week }}</text>
           </g>

           <g class="labels-y">
             <text *ngFor="let tick of yTicks" x="35" [attr.y]="getY(tick) + 4" text-anchor="end" font-size="11" fill="#64748b">{{ tick }}</text>
           </g>
        </svg>

        <!-- Legend -->
        <div class="legend">
           <div class="legend-item"><span class="indicator blue"></span>Moyenne</div>
           <div class="legend-item"><span class="indicator green"></span>Engagement</div>
           <div class="legend-item"><span class="indicator purple"></span>Présence</div>
        </div>

        <!-- Tooltip -->
        <div class="tooltip" *ngIf="tooltipVisible" [style.left.px]="tooltipX" [style.top.px]="tooltipY">
           <div class="tooltip-header">{{ currentTooltipWeek }}</div>
           <div class="tooltip-row">
             <span class="dot-sm blue"></span> Moyenne: <span class="val">{{ currentValues.moyenne }}</span>
           </div>
           <div class="tooltip-row">
             <span class="dot-sm green"></span> Engagement: <span class="val">{{ currentValues.engagement }}</span>
           </div>
           <div class="tooltip-row">
             <span class="dot-sm purple"></span> Présence: <span class="val">{{ currentValues.presence }}</span>
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
      font-size: 16px;
      font-weight: 600;
      color: #1e293b;
      margin-bottom: 16px;
    }
    .chart-wrapper {
      position: relative;
      flex: 1;
    }
    .chart-svg {
      width: 100%;
      height: 100%;
      overflow: visible;
    }
    .dot {
      cursor: pointer;
      transition: r 0.2s;
    }
    .dot:hover {
      r: 6;
      stroke-width: 3;
    }
    .legend {
      display: flex;
      justify-content: center;
      gap: 24px;
      margin-top: 8px;
    }
    .legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #64748b; font-weight: 500;}
    .indicator { width: 8px; height: 8px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 0 1px currentColor; }
    .indicator.blue { color: #3b82f6; background: #3b82f6; }
    .indicator.green { color: #10b981; background: #10b981; }
    .indicator.purple { color: #a855f7; background: #a855f7; }

    .tooltip {
      position: absolute;
      background: white;
      border: 1px solid #e2e8f0;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
      padding: 12px;
      border-radius: 8px;
      pointer-events: none;
      z-index: 20;
      font-size: 12px;
      min-width: 120px;
    }
    .tooltip-header {
      font-weight: 600;
      margin-bottom: 8px;
      color: #1e293b;
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 4px;
    }
    .tooltip-row {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
      color: #64748b;
    }
    .val {
      margin-left: auto;
      font-weight: 600;
      color: #334155;
    }
    .dot-sm { width: 6px; height: 6px; border-radius: 50%; }
    .dot-sm.blue { background: #3b82f6; }
    .dot-sm.green { background: #10b981; }
    .dot-sm.purple { background: #a855f7; }
  `]
})
export class PerformanceChart implements OnInit {
  yTicks = [0, 25, 50, 75, 100];
  xLabels: string[] = [];

  // Data matching the visual curves
  dataMoyenne: number[] = [];
  dataEngagement: number[] = [];
  dataPresence: number[] = [];

  tooltipVisible = false;
  tooltipX = 0;
  tooltipY = 0;
  currentTooltipWeek = '';
  currentValues = { moyenne: 0, engagement: 0, presence: 0 };

  constructor(private readonly http: HttpClient) {}

  ngOnInit(): void {
    this.fetchData();
  }

  fetchData(): void {
    this.http.get<any>('http://localhost:4000/teacher/performance-data', {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    }).subscribe({
      next: (data: any) => {
        this.xLabels = data.labels;
        this.dataMoyenne = data.moyenne;
        this.dataEngagement = data.engagement;
        this.dataPresence = data.presence;
      },
      error: (err: any) => console.error('Erreur lors du chargement des données de performance', err)
    });
  }

  getX(index: number): number {
    // 8 points spread across roughly 540 width (40 to 580)
    const step = 540 / (this.xLabels.length - 1);
    return 40 + (index * step);
  }

  getY(value: number): number {
    // Map 0-100 to 250-20
    // range starts at 250 (which is 0)
    // height is 230
    return 250 - (value / 100 * 230);
  }

  getPath(data: number[]): string {
    return data.map((val: number, i: number) => {
      const type = i === 0 ? 'M' : 'L';
      return `${type} ${this.getX(i)} ${this.getY(val)}`;
    }).join(' ');
  }

  showTooltip(event: MouseEvent, index: number, series: string, value: number): void {
    this.tooltipVisible = true;
    // Position tooltip near the point relative to container
    // This is rough estimation, angular binding handles updates
    // In real app, we might check bounds
    const target = event.target as SVGElement;
    const rect = target.getBoundingClientRect();
    // Assuming wrapper is parent offset
    // Just hardcode to the point coordinates for now as offset
    this.tooltipX = this.getX(index) + 10;
    this.tooltipY = this.getY(value) - 10;

    this.currentTooltipWeek = this.xLabels[index];
    this.currentValues = {
      moyenne: this.dataMoyenne[index],
      engagement: this.dataEngagement[index],
      presence: this.dataPresence[index]
    };
  }
}
