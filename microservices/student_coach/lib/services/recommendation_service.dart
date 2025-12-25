import '../models/recommendation.dart';
import 'api_service.dart';

class RecommendationService {
  final ApiService _apiService = ApiService();

  Future<List<Recommendation>> getRecommendations(String studentId, String query) async {
    final response = await _apiService.post('/recommendations/recommend', {
      'student_id': studentId,
      'query': query,
      'top_k': 5,
    });
    
    final List<dynamic> recosJson = response['recommendations'] ?? [];
    return recosJson.map((json) => Recommendation.fromJson(json)).toList();
  }

  Future<List<Recommendation>> getPersonalizedContent(String studentId, String profileType) async {
    return await getRecommendations(studentId, profileType);
  }
}
