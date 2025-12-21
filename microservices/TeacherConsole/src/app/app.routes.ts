import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard').then(m => m.Dashboard)
  },
  {
    path: 'students',
    loadComponent: () => import('./students/students').then(m => m.StudentsComponent)
  },
  {
    path: 'alerts',
    loadComponent: () => import('./alerts/alerts').then(m => m.Alerts)
  },
  {
    path: 'profiles',
    loadComponent: () => import('./profiles/profiles').then(m => m.Profiles)
  },
  {
    path: 'resources',
    loadComponent: () => import('./resources/resources').then(m => m.Resources)
  },
  {
    path: 'student/:id',
    loadComponent: () => import('./student-detail/student-detail').then(m => m.StudentDetail)
  }
];
