import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // Assuming I might need forms later, but CommonModule is enough for *ngIf

@Component({
    selector: 'app-resources',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './resources.html',
    styleUrls: ['./resources.css']
})
export class Resources {
    showModal = false;

    stats = [
        { label: 'Total Ressources', count: 6 },
        { label: 'Vidéos', count: 2 },
        { label: 'Documents', count: 2 },
        { label: 'Quiz & Exercices', count: 2 }
    ];

    resources = [
        {
            type: 'video',
            title: 'Vidéo: Techniques de gestion du temps',
            desc: 'Aide les étudiants procrastinateurs à mieux organiser leur travail',
            tagType: 'vidéo',
            tagLevel: 'Élevé',
            tagLevelColor: 'red'
        },
        {
            type: 'document',
            title: 'Document: Guide de révision efficace',
            desc: 'Méthodes de révision pour améliorer les performances',
            tagType: 'document',
            tagLevel: 'Moyen',
            tagLevelColor: 'orange'
        },
        {
            type: 'quiz',
            title: 'Quiz: Auto-évaluation - Chapitre 3',
            desc: 'Quiz formatif pour tous les niveaux',
            tagType: 'quiz',
            tagLevel: 'Tous',
            tagLevelColor: 'gray'
        },
        {
            type: 'exercise',
            title: 'Exercice: Problèmes pratiques avancés',
            desc: 'Défis supplémentaires pour étudiants performants',
            tagType: 'exercice',
            tagLevel: 'Faible',
            tagLevelColor: 'green'
        },
        {
            type: 'video',
            title: 'Vidéo: Techniques de mémorisation',
            desc: 'Stratégies mnémotechniques pour retenir les concepts',
            tagType: 'vidéo',
            tagLevel: 'Moyen',
            tagLevelColor: 'orange'
        },
        {
            type: 'document',
            title: 'Document: Plan de rattrapage personnalisé',
            desc: 'Guide pour aider les étudiants en difficulté',
            tagType: 'document',
            tagLevel: 'Élevé',
            tagLevelColor: 'red'
        }
    ];



    searchTerm: string = '';
    selectedType: string = 'Tous les types';
    selectedLevel: string = 'Tous les niveaux';

    get filteredResources() {
        return this.resources.filter(res => {
            const matchesSearch = res.title.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                res.desc.toLowerCase().includes(this.searchTerm.toLowerCase());

            // Mapping standard types to dropdown values maybe? 
            // Dropdown: Vidéos, Documents, Quiz
            // Data types: video, document, quiz, exercise

            let typeMatch = true;
            if (this.selectedType !== 'Tous les types') {
                if (this.selectedType === 'Vidéos' && res.type !== 'video') typeMatch = false;
                if (this.selectedType === 'Documents' && res.type !== 'document') typeMatch = false;
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
        switch (type.toLowerCase()) {
            case 'vidéo': return 'tag-purple';
            case 'document': return 'tag-blue';
            case 'quiz': return 'tag-green';
            case 'exercice': return 'tag-orange';
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
