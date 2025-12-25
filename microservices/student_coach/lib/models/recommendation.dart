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
    required this.distance,
    required this.relevanceBoosted,
  });

  factory Recommendation.fromJson(Map<String, dynamic> json) {
    return Recommendation(
      id: json['id'] ?? '',
      title: json['title'] ?? 'Sans titre',
      type: json['type'] ?? 'document',
      url: json['url'] ?? '',
      distance: (json['distance'] ?? 0.0).toDouble(),
      relevanceBoosted: json['relevance_boosted'] ?? false,
    );
  }
}
