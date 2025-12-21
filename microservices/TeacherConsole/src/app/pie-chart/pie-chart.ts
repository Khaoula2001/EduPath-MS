import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

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
              <!-- Assidu (Green) 42% -->
              <circle cx="50" cy="50" r="15.9155" fill="transparent" stroke="#10b981" stroke-width="32"
                      stroke-dasharray="42 58" stroke-dashoffset="0" class="segment"></circle>
              
              <!-- Irrégulier (Purple) 8% -->
              <circle cx="50" cy="50" r="15.9155" fill="transparent" stroke="#8b5cf6" stroke-width="32"
                      stroke-dasharray="8 92" stroke-dashoffset="-42" class="segment"></circle>
              
              <!-- Procrastinateur (Red) 17% -->
              <circle cx="50" cy="50" r="15.9155" fill="transparent" stroke="#ef4444" stroke-width="32"
                      stroke-dasharray="17 83" stroke-dashoffset="-50" class="segment"></circle>
             
              <!-- Moyen (Orange) 33% -->
              <circle cx="50" cy="50" r="15.9155" fill="transparent" stroke="#f59e0b" stroke-width="32"
                      stroke-dasharray="33 67" stroke-dashoffset="-67" class="segment"></circle>
           </g>
           
           <!-- Optional inner white circle for donut effect, or keep solid for pie. 
                User asked for "image 2" style previously which was solid. 
                Performance chart is lines. 
                I will keep it solid pie but with the layout of Performance chart. 
           -->
        </svg>

        <!-- Legend matched to Performance Chart style -->
        <div class="legend">
           <div class="legend-item"><span class="indicator green"></span>Assidu 42%</div>
           <div class="legend-item"><span class="indicator purple"></span>Irrégulier 8%</div>
           <div class="legend-item"><span class="indicator orange"></span>Moyen 33%</div>
           <div class="legend-item"><span class="indicator red"></span>Procrast. 17%</div>
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
    }
    
    .indicator { 
      width: 8px; 
      height: 8px; 
      border-radius: 50%; 
    }
    
    .indicator.green { background: #10b981; }
    .indicator.purple { background: #8b5cf6; }
    .indicator.orange { background: #f59e0b; }
    .indicator.red { background: #ef4444; }
  `]
})
export class PieChart { }
