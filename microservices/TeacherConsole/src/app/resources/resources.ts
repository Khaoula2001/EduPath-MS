import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { catchError, map } from 'rxjs/operators';
import { of } from 'rxjs';

interface Resource {
    id: string;
    title: string;
    description: string;
    type: string;
    url: string;
    tags: string;
    // UI props
    desc?: string;
    tagType?: string;
    tagLevel?: string;
    tagLevelColor?: string;
}

@Component({
    selector: 'app-resources',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './resources.html',
    styleUrls: ['./resources.css']
})
export class Resources implements OnInit {
    showModal = false;
    resources: Resource[] = [];
    isLoading = true;

    stats = [
        { label: 'Total Ressources', count: 0 },
        { label: 'Vidéos', count: 0 },
        { label: 'Documents', count: 0 },
        { label: 'Quiz & Exercices', count: 0 }
    ];

    searchTerm: string = '';
    selectedType: string = 'Tous les types';
    selectedLevel: string = 'Tous les niveaux';

    // API URL via Gateway
    private apiUrl = 'http://localhost:4000/api/recco/resources';

    constructor(private http: HttpClient) { }

    ngOnInit() {
        this.fetchResources();
    }

    fetchResources() {
        this.isLoading = true;
        this.http.get<Resource[]>(this.apiUrl).pipe(
            map(data => data.map(r => this.mapResourceToUI(r))),
            catchError(err => {
                console.error('Error fetching resources:', err);
                return of([]);
            })
        ).subscribe(data => {
            this.resources = data;
            this.updateStats();
            this.isLoading = false;
        });
    }

    private mapResourceToUI(r: any): Resource {
        // Parse tags for level
        const tags = (r.tags || '').toLowerCase();
        let level = 'Moyen';
        let color = 'orange';

        if (tags.includes('débutant') || tags.includes('faible')) {
            level = 'Faible';
            color = 'green';
        } else if (tags.includes('avancé') || tags.includes('élevé')) {
            level = 'Élevé';
            color = 'red';
        } else if (tags.includes('moyen')) {
            level = 'Moyen';
            color = 'orange';
        } else {
            level = 'Tous';
            color = 'gray';
        }

        // Map type
        let uiType = r.type;
        if (r.type === 'video') uiType = 'vidéo';
        if (r.type === 'pdf') uiType = 'document';
        if (r.type === 'exercise') uiType = 'exercice';

        return {
            ...r,
            desc: r.description,
            tagType: uiType,
            tagLevel: level,
            tagLevelColor: color
        };
    }

    updateStats() {
        this.stats = [
            { label: 'Total Ressources', count: this.resources.length },
            { label: 'Vidéos', count: this.resources.filter(r => r.type === 'video').length },
            { label: 'Documents', count: this.resources.filter(r => r.type === 'pdf' || r.type === 'document').length },
            { label: 'Quiz & Exercices', count: this.resources.filter(r => r.type === 'quiz' || r.type === 'exercise').length }
        ];
    }

    get filteredResources() {
        return this.resources.filter(res => {
            const matchesSearch = (res.title || '').toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                (res.desc || '').toLowerCase().includes(this.searchTerm.toLowerCase());

            let typeMatch = true;
            if (this.selectedType !== 'Tous les types') {
                if (this.selectedType === 'Vidéos' && res.type !== 'video') typeMatch = false;
                if (this.selectedType === 'Documents' && (res.type !== 'document' && res.type !== 'pdf')) typeMatch = false;
                if (this.selectedType === 'Quiz' && res.type !== 'quiz' && res.type !== 'exercise') typeMatch = false;
            }

            const levelMatch = this.selectedLevel === 'Tous les niveaux' || res.tagLevel === this.selectedLevel;

            return matchesSearch && typeMatch && levelMatch;
        });
    }

    openModal() {
        this.showModal = true;
    }

    closeModal() {
        this.showModal = false;
    }

    getTagTypeClass(type: string) {
        switch ((type || '').toLowerCase()) {
            case 'vidéo': return 'tag-purple';
            case 'video': return 'tag-purple';
            case 'document': return 'tag-blue';
            case 'pdf': return 'tag-blue';
            case 'quiz': return 'tag-green';
            case 'exercice': return 'tag-orange';
            case 'exercise': return 'tag-orange';
            default: return 'tag-gray';
        }
    }

    getTagLevelClass(color: string) {
        switch (color) {
            case 'red': return 'tag-red';
            case 'orange': return 'tag-orange';
            case 'green': return 'tag-green';
            default: return 'tag-gray';
        }
    }
}
