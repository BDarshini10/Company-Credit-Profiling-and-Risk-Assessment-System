def generate_risk_flags(directorships, new_entities):
    risks = []

    if directorships > 5:
        risks.append("Frequent Directorships")

    if new_entities.lower() == "yes":
        risks.append("Formation of New Entities")

    if not risks:
        risks.append("Low Promoter Risk")

    return risks