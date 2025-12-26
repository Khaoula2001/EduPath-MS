class User {
  final String id;
  final String username;
  final String role;
  final String token;

  User({
    required this.id,
    required this.username,
    required this.role,
    required this.token,
  });

  factory User.fromJson(Map<String, dynamic> json, String token) {
    return User(
      id: json['id']?.toString() ?? '1',
      username: json['name'] ?? '',
      role: json['role'] ?? 'student',
      token: token,
    );
  }
}
