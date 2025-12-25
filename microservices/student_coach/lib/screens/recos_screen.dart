import 'package:flutter/material.dart';
import '../models/recommendation.dart';
import '../services/recommendation_service.dart';

class RecosScreen extends StatefulWidget {
  const RecosScreen({super.key});

  @override
  State<RecosScreen> createState() => _RecosScreenState();
}

class _RecosScreenState extends State<RecosScreen> {
  final RecommendationService _recoService = RecommendationService();
  List<Recommendation> _recommendations = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadRecommendations();
  }

  Future<void> _loadRecommendations() async {
    try {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });

      // Simulation : on demande des recommandations pour le profil "Assidu"
      // Dans une version finale, on récupèrerait le profil depuis un State Management (Provider, Bloc)
      final recos = await _recoService.getRecommendations('student_123', 'Assidu');

      setState(() {
        _recommendations = recos;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Recommendations',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1A1C24),
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Ressources sélectionnées par l\'IA pour votre profil',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          
          if (_isLoading)
            const Center(child: Padding(
              padding: EdgeInsets.all(50.0),
              child: CircularProgressIndicator(),
            ))
          else if (_errorMessage != null)
            Center(
              child: Column(
                children: [
                  Text('Erreur: $_errorMessage', style: const TextStyle(color: Colors.red)),
                  ElevatedButton(onPressed: _loadRecommendations, child: const Text('Réessayer')),
                ],
              ),
            )
          else if (_recommendations.isEmpty)
            const Center(child: Text('Aucune recommandation pour le moment.'))
          else
            ..._recommendations.map((reco) => _buildRecoCard(reco)).toList(),
        ],
      ),
    );
  }

  Widget _buildRecoCard(Recommendation reco) {
    // Déterminer la couleur et l'icône selon le type
    Color typeColor = Colors.blue;
    IconData icon = Icons.description_outlined;
    
    if (reco.type.toLowerCase().contains('video')) {
      typeColor = const Color(0xFFFF6B6B);
      icon = Icons.videocam_outlined;
    } else if (reco.type.toLowerCase().contains('pdf')) {
      typeColor = const Color(0xFF4ECDC4);
      icon = Icons.picture_as_pdf_outlined;
    } else if (reco.type.toLowerCase().contains('exercice')) {
      typeColor = const Color(0xFFFFD93D);
      icon = Icons.fitness_center_outlined;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.grey.withOpacity(0.1)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: typeColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: typeColor, size: 24),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: typeColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            reco.type.toUpperCase(),
                            style: TextStyle(
                              color: typeColor,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        if (reco.relevanceBoosted)
                          const Icon(Icons.star, color: Colors.amber, size: 16),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      reco.title,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1A1C24),
                      ),
                    ),
                    Text(
                      'Pertinence : ${((1 - reco.distance) * 100).toInt()}%',
                      style: const TextStyle(
                        fontSize: 13,
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                // Ici on pourrait ouvrir l'URL dans un navigateur
                print('Ouverture de : ${reco.url}');
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF8B80F8),
                foregroundColor: Colors.white,
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.launch, size: 20),
                  SizedBox(width: 8),
                  Text(
                    'Accéder à la ressource',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

