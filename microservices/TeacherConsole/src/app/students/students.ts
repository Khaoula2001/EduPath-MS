import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { StudentService, Student } from '../services/student.service';

@Component({
    selector: 'app-students',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './students.html',
    styleUrls: ['./students.css']
})
export class StudentsComponent implements OnInit {
    searchTerm: string = '';
    selectedRisk: string = 'Tous les risques';
    selectedProfile: string = 'Tous les profils';

    students: any[] = [];
    isLoading: boolean = true;
    error: string | null = null;

    constructor(private studentService: StudentService) { }

    ngOnInit() {
        this.loadStudents();
    }

    loadStudents() {
        this.isLoading = true;
        this.studentService.getStudents().subscribe({
            next: (data: Student[]) => {
                this.students = data;
                this.isLoading = false;
            },
            error: (err: any) => {
                console.error('Failed to load students', err);
                this.error = 'Erreur lors du chargement des étudiants.';
                this.isLoading = false;
            }
        });
    }

    get filteredStudents() {
        return this.students.filter(student => {
            const matchesSearch = student.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                student.email.toLowerCase().includes(this.searchTerm.toLowerCase());

            const matchesRisk = this.selectedRisk === 'Tous les risques' || student.risk === this.selectedRisk;
            const matchesProfile = this.selectedProfile === 'Tous les profils' || student.profile === this.selectedProfile;

            return matchesSearch && matchesRisk && matchesProfile;
        });
    }

    getProfileClass(color: string) {
        switch (color) {
            case 'green': return 'badge-green';
            case 'blue': return 'badge-blue';
            case 'red': return 'badge-red';
            case 'purple': return 'badge-purple';
            case 'orange': return 'badge-orange';
            default: return 'badge-gray';
        }
    }

    getRiskDotClass(color: string) {
        switch (color) {
            case 'green': return 'dot-green';
            case 'orange': return 'dot-orange';
            case 'red': return 'dot-red';
            default: return 'dot-gray';
        }
    }
}
