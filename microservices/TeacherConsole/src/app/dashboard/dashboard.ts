import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StatsCards } from '../stats-cards/stats-cards';
import { PerformanceChart } from '../performance-chart/performance-chart';
import { PieChart } from '../pie-chart/pie-chart';
import { BarChart } from '../bar-chart/bar-chart';
import { AlertsList } from '../alerts-list/alerts-list';
import { RiskHeatmap } from '../risk-heatmap/risk-heatmap';


@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    StatsCards,
    PerformanceChart,
    PieChart,
    BarChart,
    AlertsList,
    RiskHeatmap
  ],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class Dashboard {
  dashboardTitle = 'Tableau de bord';
  subTitle = 'Vue d\'ensemble des performances de vos étudiants';
}
