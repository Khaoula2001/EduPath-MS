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
    // Access via API Gateway -> Teacher Console API
    private teacherApiUrl = 'http://localhost:4000/teacher';

    constructor(private http: HttpClient) { }

    getStudents(): Observable<Student[]> {
        // The new endpoint /teacher/students returns the fully enriched list
        return this.http.get<Student[]>(`${this.teacherApiUrl}/students`).pipe(
            map(students => students || []),
            catchError(err => {
                console.error('Error loading students', err);
                return of([]);
            })
        );
    }

    // getStudentProfile is no longer needed as the list is already enriched.
    // We can keep it or remove it. Removing it to clean up code.
}
