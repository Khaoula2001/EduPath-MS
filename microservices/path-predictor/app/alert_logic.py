def generate_alert(probability_success: float) -> str:
    if probability_success >= 0.60:
        return "✅ Fortes chances de réussite"
    elif probability_success >= 0.40:
        return "⚠️ Étudiant fragile"
    else:
        return "🚨 Risque élevé d’échec"
