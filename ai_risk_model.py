import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Load dataset
data = pd.read_csv("risk_dataset.csv")

# Input features
X = data[[
    "directorships",
    "new_entities",
    "years",
    "group_companies",
    "exposure",
    "profit_margin",
    "debt_ratio"
]]

# Target
y = data["risk"]

# Train Random Forest Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

def predict_risk(features):
    prediction = model.predict([features])
    return prediction[0]
def predict_risk_probability(features):

    probabilities = model.predict_proba([features])[0]

    labels = model.classes_

    result = dict(zip(labels, probabilities))

    return result
def get_feature_importance():

    features = [
        "directorships",
        "new_entities",
        "years",
        "group_companies",
        "exposure",
        "profit_margin",
        "debt_ratio"
    ]

    importance = model.feature_importances_

    return dict(zip(features, importance))

print("AI model trained successfully using Random Forest")