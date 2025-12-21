import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

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
          <span>4</span>
          <span>3</span>
          <span>2</span>
          <span>1</span>
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
                       [style.height.%]="(bar.value / 4) * 100"
                       [class.highlight]="i === 3"> <!-- 70-80 is highlighted in example? Or hover logic -->
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
      background-color: #3b82f6; /* Uniform Blue */
      border-radius: 4px 4px 0 0;
      transition: height 0.4s ease, opacity 0.2s;
      opacity: 1;
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
export class BarChart {
  bars = [
    { label: '0-50', value: 0 },
    { label: '50-60', value: 2 },
    { label: '60-70', value: 1 },
    { label: '70-80', value: 4 },
    { label: '80-90', value: 2 },
    { label: '90-100', value: 3 }
  ];
}
