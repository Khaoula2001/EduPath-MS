import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
    selector: 'app-students',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './students.html',
    styleUrls: ['./students.css']
})
export class StudentsComponent {
    searchTerm: string = '';
    selectedRisk: string = 'Tous les risques';
    selectedProfile: string = 'Tous les profils';

    students = [
        {
            initials: 'OB',
            name: 'Omar Benali',
            email: 'omar.benali@edu.ma',
            profile: 'Assidu',
            profileColor: 'green',
            note: '92%',
            presence: '98%',
            engagement: '95%',
            homework: '18/20',
            risk: 'Low',
            riskColor: 'green'
        },
        {
            initials: 'NEA',
            name: 'Nisrine El Amrani',
            email: 'nisrine.elamrani@edu.ma',
            profile: 'Assidu',
            profileColor: 'green',
            note: '88%',
            presence: '95%',
            engagement: '90%',
            homework: '19/20',
            risk: 'Low',
            riskColor: 'green'
        },
        {
            initials: 'KI',
            name: 'Khawla Idrissi',
            email: 'khawla.idrissi@edu.ma',
            profile: 'Moyen',
            profileColor: 'blue',
            note: '72%',
            presence: '85%',
            engagement: '70%',
            homework: '15/20',
            risk: 'Medium',
            riskColor: 'orange'
        },
        {
            initials: 'MC',
            name: 'Mohamed Chakir',
            email: 'mohamed.chakir@edu.ma',
            profile: 'Procrastinateur',
            profileColor: 'red',
            note: '58%',
            presence: '65%',
            engagement: '45%',
            homework: '10/20',
            risk: 'High',
            riskColor: 'red'
        },
        {
            initials: 'FZT',
            name: 'Fatima Zahra Tazi',
            email: 'fatima.tazi@edu.ma',
            profile: 'Assidu',
            profileColor: 'green',
            note: '95%',
            presence: '100%',
            engagement: '98%',
            homework: '20/20',
            risk: 'Low',
            riskColor: 'green'
        },
        {
            initials: 'YA',
            name: 'Youssef Alaoui',
            email: 'youssef.alaoui@edu.ma',
            profile: 'Moyen',
            profileColor: 'blue',
            note: '75%',
            presence: '80%',
            engagement: '75%',
            homework: '14/20',
            risk: 'Medium',
            riskColor: 'orange'
        },
        {
            initials: 'AF',
            name: 'Amine Fassi',
            email: 'amine.fassi@edu.ma',
            profile: 'Irrégulier',
            profileColor: 'purple',
            note: '62%',
            presence: '70%',
            engagement: '55%',
            homework: '11/20',
            risk: 'High',
            riskColor: 'red'
        },
        {
            initials: 'IL',
            name: 'Imane Lahlou',
            email: 'imane.lahlou@edu.ma',
            profile: 'Moyen',
            profileColor: 'blue',
            note: '78%',
            presence: '88%',
            engagement: '80%',
            homework: '16/20',
            risk: 'Medium',
            riskColor: 'orange'
        },
        {
            initials: 'HB',
            name: 'Hamza Benjelloun',
            email: 'hamza.benjelloun@edu.ma',
            profile: 'Procrastinateur',
            profileColor: 'red',
            note: '55%',
            presence: '60%',
            engagement: '40%',
            homework: '9/20',
            risk: 'High',
            riskColor: 'red'
        },
        {
            initials: 'MK',
            name: 'Mariam Kettani',
            email: 'mariam.kettani@edu.ma',
            profile: 'Assidu',
            profileColor: 'green',
            note: '87%',
            presence: '94%',
            engagement: '88%',
            homework: '18/20',
            risk: 'Low',
            riskColor: 'green'
        },
        {
            initials: 'KT',
            name: 'Karim Tazi',
            email: 'karim.tazi@edu.ma',
            profile: 'Moyen',
            profileColor: 'blue',
            note: '70%',
            presence: '82%',
            engagement: '72%',
            homework: '14/20',
            risk: 'Medium',
            riskColor: 'orange'
        }
    ];

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
