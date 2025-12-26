class StudentContextService:
    def augment_query(self, query: str, student_profile: str = None, risk_level: str = None) -> str:
        augmented_query = query
        
        if risk_level == "High":
            augmented_query += " basic remediation fundamental support"
        elif risk_level == "Medium":
            augmented_query += " reinforcement practice"
        
        if student_profile == "Procrastinateur (Procrastinator)":
            augmented_query += " short engaging interactive video"
        elif student_profile == "Assidu (Regular)":
            augmented_query += " advanced enrichment deeper dive"
        elif student_profile == "En difficulté (At-Risk)":
            augmented_query += " remedial assistance step-by-step"
            
        return augmented_query

student_context_service = StudentContextService()
