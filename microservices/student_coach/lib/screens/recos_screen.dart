import 'package:flutter/material.dart';

class RecosScreen extends StatelessWidget {
  const RecosScreen({super.key});

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
            'Curated resources just for you',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          _buildRecoCard(
            type: 'Video',
            typeColor: const Color(0xFFFF6B6B),
            icon: Icons.videocam_outlined,
            title: 'Advanced Calculus Explained',
            subtitle: 'Khan Academy • 15 min',
          ),
          _buildRecoCard(
            type: 'PDF',
            typeColor: const Color(0xFF4ECDC4),
            icon: Icons.description_outlined,
            title: 'Physics: Newton\'s Laws Summary',
            subtitle: 'MIT OpenCourseWare • 8 pages',
          ),
          _buildRecoCard(
            type: 'Exercise',
            typeColor: const Color(0xFFFFD93D),
            icon: Icons.fitness_center_outlined,
            title: 'Practice Quiz: Algebra',
            subtitle: '20 questions • Medium difficulty',
          ),
          _buildRecoCard(
            type: 'Video',
            typeColor: const Color(0xFFFF6B6B),
            icon: Icons.videocam_outlined,
            title: 'Chemistry Bonding Tutorial',
            subtitle: 'Crash Course • 12 min',
          ),
          _buildRecoCard(
            type: 'PDF',
            typeColor: const Color(0xFF4ECDC4),
            icon: Icons.description_outlined,
            title: 'History: World War II Timeline',
            subtitle: 'History Channel • 10 pages',
          ),
        ],
      ),
    );
  }

  Widget _buildRecoCard({
    required String type,
    required Color typeColor,
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
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
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: typeColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        type,
                        style: TextStyle(
                          color: typeColor,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1A1C24),
                      ),
                    ),
                    Text(
                      subtitle,
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
              onPressed: () {},
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
                  Icon(Icons.play_arrow, size: 20),
                  SizedBox(width: 8),
                  Text(
                    'Start',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
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
