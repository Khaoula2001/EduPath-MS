import 'package:flutter/material.dart';

class AlertsScreen extends StatelessWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Predictive Alerts',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1A1C24),
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Insights to optimize your learning',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          _buildAlertCard(
            icon: Icons.error_outline,
            color: const Color(0xFFFF6B6B),
            title: 'Drop in regularity detected',
            description: 'Your study sessions have decreased by 30% this week compared to last week.',
          ),
          _buildAlertCard(
            icon: Icons.trending_up,
            color: const Color(0xFF51CF66),
            title: 'Performance peak identified',
            description: 'You perform best between 2-4 PM. Consider scheduling difficult topics during this time.',
          ),
          _buildAlertCard(
            icon: Icons.info_outline,
            color: const Color(0xFF339AF0),
            title: 'Weekly summary available',
            description: 'Your weekly analytics report is ready. Check your progress and insights.',
          ),
          _buildAlertCard(
            icon: Icons.warning_amber_outlined,
            color: const Color(0xFFFCC419),
            title: 'Quiz deadline approaching',
            description: 'Physics quiz due in 2 days. You have 3 recommended resources to review.',
          ),
          _buildAlertCard(
            icon: Icons.trending_up,
            color: const Color(0xFF51CF66),
            title: 'Streak milestone reached',
            description: 'Congratulations! You\'ve maintained a 7-day study streak. Keep it going!',
          ),
        ],
      ),
    );
  }

  Widget _buildAlertCard({
    required IconData icon,
    required Color color,
    required String title,
    required String description,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.withOpacity(0.1)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                width: 4,
                color: color,
              ),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: color.withOpacity(0.1),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(icon, color: color, size: 20),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              title,
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF1A1C24),
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              description,
                              style: const TextStyle(
                                fontSize: 14,
                                color: Colors.grey,
                                height: 1.4,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
