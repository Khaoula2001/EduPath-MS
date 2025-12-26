import 'package:flutter/material.dart';
import '../models/student_profile.dart';
import '../services/student_service.dart';
import '../services/auth_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final StudentService _studentService = StudentService();
  StudentProfile? _profile;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
      
      final studentId = AuthService.currentUser?.id ?? '1';
      final profile = await _studentService.getMyProfile(studentId);
      
      setState(() {
        _profile = profile;
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
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_errorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Erreur: $_errorMessage', style: const TextStyle(color: Colors.red)),
            ElevatedButton(onPressed: _loadData, child: const Text('Réessayer')),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 24),
          _buildProgressCard(),
          const SizedBox(height: 16),
          _buildRiskBadge(),
          const SizedBox(height: 24),
          _buildProfileDescriptionCard(),
          const SizedBox(height: 32),
          if (_profile?.recommendations.isNotEmpty ?? false) ...[
            const Text(
              'Recommended Resources',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1A1C24),
              ),
            ),
            const SizedBox(height: 16),
            ...(_profile!.recommendations.map((reco) => _buildActivityItem(
              icon: reco.type == 'video' ? Icons.play_circle_fill : Icons.description,
              iconColor: Colors.purple,
              title: reco.title,
              subtitle: 'Basé sur votre profil ${_profile!.profileType}',
            )).toList()),
            const SizedBox(height: 24),
          ],
          const Text(
            'Recent Activities',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1A1C24),
            ),
          ),
          const SizedBox(height: 16),
          if (_profile?.recentActivities.isEmpty ?? true)
            _buildActivityItem(
              icon: Icons.history,
              iconColor: Colors.blue,
              title: 'Dernière activité',
              subtitle: _profile?.lastActivity ?? 'Aucune activité',
            )
          else
            ...(_profile!.recentActivities.map((activity) => _buildActivityItem(
              icon: activity.type == 'reco' ? Icons.lightbulb : Icons.notifications,
              iconColor: activity.type == 'alert' ? Colors.orange : Colors.blue,
              title: activity.title,
              subtitle: activity.message,
            )).toList()),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Welcome back,',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1A1C24),
              ),
            ),
            Text(
              _profile?.studentId ?? 'Chargement...',
              style: const TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
          ],
        ),
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: const Color(0xffa199ff),
            borderRadius: BorderRadius.circular(24),
          ),
          child: Center(
            child: Text(
              _profile != null && _profile!.studentId.isNotEmpty
                  ? _profile!.studentId.substring(0, _profile!.studentId.length >= 2 ? 2 : 1).toUpperCase()
                  : '..',
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildProgressCard() {
    final double completion = _profile?.completionRate ?? 0.0;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 32),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
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
        children: [
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 120,
                height: 120,
                child: CircularProgressIndicator(
                  value: completion,
                  strokeWidth: 10,
                  backgroundColor: Colors.grey.withOpacity(0.1),
                  valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF8B80F8)),
                  strokeCap: StrokeCap.round,
                ),
              ),
              Text(
                '${(completion * 100).toInt()}%',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1A1C24),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          const Text(
            'Taux de Complétion Global',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRiskBadge() {
    final risk = _profile?.riskLevel ?? 'Low';
    Color color = risk == 'High' ? Colors.red : risk == 'Medium' ? Colors.orange : Colors.green;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.warning_amber, color: color, size: 20),
          const SizedBox(width: 8),
          Text(
            'Risque : $risk',
            style: TextStyle(color: color, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildProfileDescriptionCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF8B80F8), Color(0xFFB9B2FB)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text(
                'Profil IA détecté',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(width: 8),
              const Text('🧠', style: TextStyle(fontSize: 20)),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'L\'IA vous a classé comme : ${_profile?.profileType ?? 'Calcul en cours...'}',
            style: TextStyle(
              fontSize: 16,
              color: Colors.white.withOpacity(0.9),
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Votre score d\'engagement est de ${((_profile?.engagementScore ?? 0) * 100).toInt()}%. Continuez vos efforts !',
            style: TextStyle(
              fontSize: 14,
              color: Colors.white.withOpacity(0.8),
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActivityItem({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.withOpacity(0.1)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: iconColor, size: 24),
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
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1A1C24),
                  ),
                ),
                Text(
                  subtitle,
                  style: const TextStyle(
                    fontSize: 14,
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

