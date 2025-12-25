class User {
  final String username;
  final String role;
  final String token;

  User({
    required this.username,
    required this.role,
    required this.token,
  });

  factory User.fromJson(Map<String, dynamic> json, String token) {
    return User(
      username: json['name'] ?? '',
      role: json['role'] ?? 'student',
      token: token,
    );
  }
}
