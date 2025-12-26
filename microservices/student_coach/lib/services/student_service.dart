import '../models/student_profile.dart';
import 'api_service.dart';

class StudentService {
  final ApiService _apiService = ApiService();

  Future<StudentProfile> getMyProfile(String studentId) async {
    // 1. Get basic profile
    final profileData = await _apiService.get('/profiler/profile/$studentId');
    StudentProfile profile = StudentProfile.fromJson(profileData);

    // 2. Get notifications/activities
    try {
      final List<dynamic> activitiesData = await _apiService.get('/coach/notifications/$studentId');
      final activities = activitiesData.map((a) => Activity.fromJson(a)).toList();
      profile = profile.copyWith(recentActivities: activities);
    } catch (e) {
      print('Error fetching activities: $e');
    }

    // 3. Get recommendations
    try {
      final recoData = await _apiService.post('/recco/recommend', {
        'query': 'ressources recommandées pour mon profil',
        'student_id': studentId,
        'student_profile': profile.profileType,
        'risk_level': profile.riskLevel,
        'top_k': 3
      });
      
      if (recoData['recommendations'] != null) {
        final List<dynamic> recosList = recoData['recommendations'];
        final recos = recosList.map((r) => Recommendation.fromJson(r)).toList();
        profile = profile.copyWith(recommendations: recos);
      }
    } catch (e) {
      print('Error fetching recommendations: $e');
    }

    return profile;
  }

  Future<Map<String, dynamic>> getMyStats(String studentId) async {
    return await _apiService.get('/coach/student/stats/$studentId');
  }
}
