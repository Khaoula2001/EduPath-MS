class Recommendation {
  final String id;
  final String title;
  final String type;
  final String url;
  final double distance;
  final bool relevanceBoosted;

  Recommendation({
    required this.id,
    required this.title,
    required this.type,
    required this.url,
    this.distance = 0.0,
    this.relevanceBoosted = false,
  });

  factory Recommendation.fromJson(Map<String, dynamic> json) {
    return Recommendation(
      id: json['id']?.toString() ?? '',
      title: json['title'] ?? '',
      type: json['type'] ?? 'resource',
      url: json['url'] ?? '',
      distance: (json['distance'] ?? 0.0).toDouble(),
      relevanceBoosted: json['relevance_boosted'] ?? false,
    );
  }
}

class Activity {
  final int id;
  final String title;
  final String message;
  final String type;

  Activity({
    required this.id,
    required this.title,
    required this.message,
    required this.type,
  });

  factory Activity.fromJson(Map<String, dynamic> json) {
    return Activity(
      id: json['id'] ?? 0,
      title: json['title'] ?? '',
      message: json['message'] ?? '',
      type: json['type'] ?? 'info',
    );
  }
}

class StudentProfile {
  final String studentId;
  final String profileType;
  final String riskLevel;
  final double engagementScore;
  final double completionRate;
  final String lastActivity;
  final List<Recommendation> recommendations;
  final List<Activity> recentActivities;

  StudentProfile({
    required this.studentId,
    required this.profileType,
    required this.riskLevel,
    required this.engagementScore,
    required this.completionRate,
    required this.lastActivity,
    this.recommendations = const [],
    this.recentActivities = const [],
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

  StudentProfile copyWith({
    List<Recommendation>? recommendations,
    List<Activity>? recentActivities,
  }) {
    return StudentProfile(
      studentId: studentId,
      profileType: profileType,
      riskLevel: riskLevel,
      engagementScore: engagementScore,
      completionRate: completionRate,
      lastActivity: lastActivity,
      recommendations: recommendations ?? this.recommendations,
      recentActivities: recentActivities ?? this.recentActivities,
    );
  }
}
