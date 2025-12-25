class StudentProfile {
  final String studentId;
  final String profileType;
  final String riskLevel;
  final double engagementScore;
  final double completionRate;
  final String lastActivity;

  StudentProfile({
    required this.studentId,
    required this.profileType,
    required this.riskLevel,
    required this.engagementScore,
    required this.completionRate,
    required this.lastActivity,
  });

  factory StudentProfile.fromJson(Map<String, dynamic> json) {
    return StudentProfile(
      studentId: json['student_id'] ?? '',
      profileType: json['profile_type'] ?? 'Inconnu',
      riskLevel: json['risk_level'] ?? 'Low',
      engagementScore: (json['engagement_score'] ?? 0.0).toDouble(),
      completionRate: (json['completion_rate'] ?? 0.0).toDouble(),
      lastActivity: json['last_activity'] ?? '',
    );
  }
}
