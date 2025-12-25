import '../models/user.dart';
import 'api_service.dart';

class AuthService {
  final ApiService _apiService = ApiService();
  static User? currentUser;

  Future<bool> login(String username, String password) async {
    try {
      final response = await _apiService.post('/login', {
        'username': username,
        'password': password,
      });

      if (response['accessToken'] != null) {
        currentUser = User.fromJson(
          response['user'] ?? {'name': username, 'role': 'student'},
          response['accessToken'],
        );
        return true;
      }
      return false;
    } catch (e) {
      print('Login error: $e');
      return false;
    }
  }

  Future<bool> signUp(String username, String email, String password) async {
    try {
      // Simulation d'une création de compte (peut être connectée à StudentCoachAPI plus tard)
      await Future.delayed(const Duration(seconds: 1));
      return true;
    } catch (e) {
      print('Signup error: $e');
      return false;
    }
  }

  void logout() {
    currentUser = null;
  }
}
