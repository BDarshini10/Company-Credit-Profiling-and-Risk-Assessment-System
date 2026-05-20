import pandas as pd
import random

rows = []

for i in range(1000):

    directorships = random.randint(1,10)
    new_entities = random.randint(0,1)
    years = random.randint(1,30)
    group_companies = random.randint(1,10)
    exposure = random.randint(5,40)
    profit_margin = random.randint(5,25)
    debt_ratio = random.randint(20,70)

    # Assign risk logically
    if directorships > 6 or new_entities == 1 or debt_ratio > 60:
        risk = "High"
    elif directorships > 4 or debt_ratio > 45:
        risk = "Medium"
    else:
        risk = "Low"

    rows.append([
        directorships,
        new_entities,
        years,
        group_companies,
        exposure,
        profit_margin,
        debt_ratio,
        risk
    ])

columns = [
    "directorships",
    "new_entities",
    "years",
    "group_companies",
    "exposure",
    "profit_margin",
    "debt_ratio",
    "risk"
]

df = pd.DataFrame(rows, columns=columns)

df.to_csv("risk_dataset.csv", index=False)

print("Dataset with 1000 companies generated successfully.")