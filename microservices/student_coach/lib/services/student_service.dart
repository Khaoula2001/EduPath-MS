import '../models/student_profile.dart';
import 'api_service.dart';

class StudentService {
  final ApiService _apiService = ApiService();

  Future<StudentProfile> getMyProfile(String studentId) async {
    // Le microservice utilise /profile/{id} au singulier
    final data = await _apiService.get('/profiler/profile/$studentId');
    return StudentProfile.fromJson(data);
  }

  Future<Map<String, dynamic>> getMyStats(String studentId) async {
    return await _apiService.get('/student/stats/$studentId');
  }
}
