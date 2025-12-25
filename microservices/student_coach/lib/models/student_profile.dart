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
      studentId: json['student_id']?.toString() ?? '',
      profileType: json['profile_name'] ?? json['profile_type'] ?? 'Assidu',
      riskLevel: json['risk_level'] ?? 'Low',
      engagementScore: (json['mean_score'] ?? json['engagement_score'] ?? 0.8).toDouble(),
      completionRate: (json['progress_rate'] ?? json['completion_rate'] ?? 0.6).toDouble(),
      lastActivity: json['last_activity'] ?? 'Aujourd\'hui',
    );
  }
}
