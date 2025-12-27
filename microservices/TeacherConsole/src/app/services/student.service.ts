import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin, of } from 'rxjs';
import { map, catchError, switchMap } from 'rxjs/operators';

export interface Student {
    id: string;
    name: string;
    email: string;
    initials: string;
    profile?: string;
    profileColor?: string;
    note?: string;
    presence?: string;
    engagement?: string;
    homework?: string;
    risk?: string;
    riskColor?: string;
    // Risk Table Props
    riskScore?: number;
    riskLevel?: string;
    performance?: number;
    lastActivity?: string;
    hasAction?: boolean;
}

@Injectable({
    providedIn: 'root'
})
export class StudentService {
    // Access via API Gateway
    private coachApiUrl = 'http://localhost:4000/api/coach';
    private profilerApiUrl = 'http://localhost:4000/api/profiler';

    constructor(private http: HttpClient) { }

    getStudents(): Observable<Student[]> {
        return this.http.get<Student[]>(`${this.coachApiUrl}/students`).pipe(
            switchMap(students => {
                if (!students || students.length === 0) return of([]);

                // For each student, fetch additional details (profile/risk) in parallel
                const profileRequests = students.map(student =>
                    this.getStudentProfile(student.id).pipe(
                        map(profile => ({ ...student, ...profile })),
                        catchError(() => of(student)) // detailed info fail shouldn't break list
                    )
                );
                return forkJoin(profileRequests);
            })
        );
    }

    getStudentProfile(studentId: string): Observable<Partial<Student>> {
        return this.http.get<any>(`${this.profilerApiUrl}/profile/${studentId}`).pipe(
            map(data => {
                // Transform backend profile data to UI model
                const riskLevel = data.risk_level || 'Low';
                let riskColor = 'green';
                if (riskLevel === 'High' || riskLevel === 'Critique') riskColor = 'red';
                else if (riskLevel === 'Medium' || riskLevel === 'Moyen') riskColor = 'orange';

                return {
                    profile: data.profile_name || 'Standard',
                    profileColor: this.getProfileColor(data.profile_name),
                    note: data.mean_score ? `${Math.round(data.mean_score)}%` : 'N/A',
                    presence: '95%', // Mock for now if not available
                    engagement: data.progress_rate ? `${Math.round(data.progress_rate * 100)}%` : 'N/A',
                    homework: '15/20', // Mock
                    risk: riskLevel,
                    riskColor: riskColor,

                    // Risk Table specifics
                    riskScore: data.risk_score || (riskLevel === 'High' ? 85 : 20),
                    riskLevel: riskLevel,
                    performance: data.mean_score || 0,
                    lastActivity: new Date().toISOString().split('T')[0], // Mock
                    hasAction: true
                };
            })
        );
    }

    private getProfileColor(profileName: string): string {
        if (!profileName) return 'gray';
        const p = profileName.toLowerCase();
        if (p.includes('assidu')) return 'green';
        if (p.includes('procrastinateur')) return 'red';
        if (p.includes('moyen')) return 'blue';
        return 'purple';
    }
}
