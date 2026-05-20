from flask import Flask, render_template, request, session, send_file, redirect
from scraper import scrape_company
from risk_engine import generate_risk_flags
from ai_risk_model import predict_risk, predict_risk_probability
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = "credit_risk_secret"

# SIMPLE USER DATABASE
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "analyst": {"password": "analyst123", "role": "analyst"}
}

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:

            session["user"] = username
            session["role"] = users[username]["role"]

            return redirect("/")

        else:
            return render_template("login.html", error="Invalid login")

    return render_template("login.html")


@app.route("/", methods=["GET", "POST"])
def index():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        data = {
            "company_name": request.form["company_name"],
            "website": request.form["website"],
            "industry": request.form["industry"],
            "years": request.form["years"],
            "business_model": request.form["business_model"],

            "group_companies": request.form["group_companies"],
            "activities": request.form["activities"],
            "exposure": request.form["exposure"],

            "promoter_name": request.form["promoter_name"],
            "education": request.form["education"],
            "experience": request.form["experience"],
            "track_record": request.form["track_record"],
            "key_functions": request.form["key_functions"],

            "directorships": int(request.form["directorships"]),
            "new_entities": request.form["new_entities"],
            "profit_margin": float(request.form["profit_margin"]),
            "debt_ratio": float(request.form["debt_ratio"])
        }

        # AUTO-GENERATED COMPANY PROFILE
        data["about"] = scrape_company(data["website"])

        # PROMOTER RISK FLAGS
        data["risks"] = generate_risk_flags(
            data["directorships"], data["new_entities"]
        )

        # RED FLAG EXPLANATION ENGINE
        risk_explanations = {}

        for r in data["risks"]:
            if r == "Frequent Directorships":
                risk_explanations[r] = (
                    "Holding multiple directorships may reduce management focus "
                    "and increase governance and oversight risk."
                )

            elif r == "Formation of New Entities":
                risk_explanations[r] = (
                    "Frequent formation of new entities may indicate aggressive expansion "
                    "or complex ownership and fund flow structures."
                )

            elif r == "Low Promoter Risk":
                risk_explanations[r] = (
                    "No major promoter-related governance or compliance risks were identified."
                )

        data["risk_explanations"] = risk_explanations


        # PROMOTER RISK LEVEL
        years = int(re.sub(r'\D', '', data["years"]))
        group_companies = int(re.sub(r'\D', '', data["group_companies"]))
        exposure = int(re.sub(r'\D', '', data["exposure"]))
        profit_margin = float(re.sub(r'[^0-9.]', '', str(data["profit_margin"])))
        debt_ratio = float(re.sub(r'[^0-9.]', '', str(data["debt_ratio"])))

        ai_risk = predict_risk([
        data["directorships"],
        1 if data["new_entities"].lower() == "yes" else 0,
        years,
        group_companies,
        exposure,
        profit_margin,
        debt_ratio
    ])

        data["risk_level"] = ai_risk
        data["risk_probability"] = predict_risk_probability([
        data["directorships"],
        1 if data["new_entities"].lower() == "yes" else 0,
        years,
        group_companies,
        exposure,
        profit_margin,
        debt_ratio
   ])
    

       # AI-BASED CORPORATE CREDIT SCORE
        risk_prob = data["risk_probability"]
        low_prob = risk_prob["Low"]
        credit_score = int(300 + (low_prob * 600))

        data["credit_score"] = credit_score 


        # QUALITATIVE RISK SCORE (Higher is better)

        if ai_risk == "Low":
         data["risk_score"] = 85
        elif ai_risk == "Medium":
         data["risk_score"] = 65
        else:
         data["risk_score"] = 40
    

        # CREDIT OPINION
        if data["risk_score"] >= 80:
            data["credit_opinion"] = (
                "The company demonstrates strong qualitative fundamentals supported by "
                "experienced promoters, stable operations, and sound governance practices."
            )
        elif data["risk_score"] >= 60:
            data["credit_opinion"] = (
                "The company exhibits satisfactory qualitative strength; however, certain "
                "promoter-related risk indicators warrant periodic monitoring."
            )
        else:
            data["credit_opinion"] = (
                "The qualitative assessment highlights elevated promoter-related risks. "
                "A cautious lending approach is advised."
            )

        if data["credit_score"] >= 750:
           decision = "Loan Approved"

        elif data["credit_score"] >= 650:
           decision = "Approved with Monitoring"
        else:
           decision = "Loan Not Recommended"
        data["loan_decision"] = decision
        
        # STRENGTHS & WEAKNESSES
        strengths = []
        weaknesses = []

        if data["risk_level"] == "Low":
            strengths.append("Strong promoter governance")
        else:
            weaknesses.append("Promoter-related risk indicators observed")

        try:
            if int(data["years"]) >= 10:
                strengths.append("Established operational track record")
            else:
                weaknesses.append("Limited operational history")
        except:
            pass

        data["strengths"] = strengths
        data["weaknesses"] = weaknesses

        # ENSURE NON-EMPTY DISPLAY
        if not data["strengths"]:
            data["strengths"] = ["-"]

        if not data["weaknesses"]:
            data["weaknesses"] = ["-"]


        # KEY OBSERVATIONS
        data["key_observations"] = [
            f"Promoter Risk Level assessed as {data['risk_level']}",
            f"Qualitative Risk Score: {data['risk_score']} / 100",
            "Assessment based on manual inputs and website disclosures"
        ]


        # SMART SUMMARY
        data["summary"] = (
            f"{data['company_name']} operates in the {data['industry']} sector with "
            f"{data['years']} years of operational presence. The qualitative assessment "
            f"indicates a {data['risk_level'].lower()} promoter risk profile with a "
            f"risk score of {data['risk_score']} out of 100."
        )


        # FINAL RECOMMENDATION
        if data["risk_score"] >= 80:
            data["recommendation"] = "Recommended for long-term lending exposure."
        elif data["risk_score"] >= 60:
            data["recommendation"] = "Recommended with monitoring conditions."
        else:
            data["recommendation"] = "Cautious lending approach advised."


        # STORE DATA IN SESSION
        session["report_data"] = data

        # POST → REDIRECT → GET
        return redirect("/dashboard")

    return render_template("index.html")


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    data = session.get("report_data")

    if not data:
        return redirect("/")

    return render_template("dashboard.html", **data)

   # LOGOUT ROUTE
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/view-report")
def view_report():
    data = session.get("report_data")
    if not data:
        return redirect("/")
    return render_template("report.html", **data)


@app.route("/download-pdf")
def download_pdf():
    data = session.get("report_data")
    if not data:
        return redirect("/")

    file_path = "final_report.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path)

    content = []
    report_date = datetime.now().strftime("%d-%m-%Y")

    content.append(
        Paragraph(
            f"<b>{data['company_name']}</b><br/>"
            f"Final Qualitative Credit Assessment<br/>"
            f"Internal Credit Appraisal Note<br/>"
            f"Report Date: {report_date}<br/><br/>",
            styles["Title"]
        )
    )

    # COMPANY & GROUP BACKGROUND
    content.append(Paragraph("<b>Company & Group Background</b><br/>", styles["Heading2"]))
    content.append(Paragraph(f"<b>Company:</b> {data['company_name']}", styles["Normal"]))
    content.append(Paragraph(f"<b>Industry:</b> {data['industry']}", styles["Normal"]))
    content.append(Paragraph(f"<b>Years of Operation:</b> {data['years']}", styles["Normal"]))
    content.append(Paragraph(f"<b>Business Model:</b> {data['business_model']}", styles["Normal"]))
    content.append(Paragraph("<br/><b>About Company</b><br/>", styles["Normal"]))
    content.append(Paragraph(data["about"], styles["Normal"]))

    # PROMOTER PROFILE SUMMARY
    content.append(Paragraph("<br/><b>Promoter Profile Summary</b><br/>", styles["Heading2"]))
    content.append(Paragraph(f"<b>Name:</b> {data['promoter_name']}", styles["Normal"]))
    content.append(Paragraph(f"<b>Education:</b> {data['education']}", styles["Normal"]))
    content.append(Paragraph(f"<b>Experience:</b> {data['experience']}", styles["Normal"]))
    content.append(Paragraph(f"<b>Track Record:</b> {data['track_record']}", styles["Normal"]))

    # PROMOTER RISK ANALYSIS
    content.append(Paragraph("<br/><b>Promoter Risk Analysis</b><br/>", styles["Heading2"]))
    content.append(Paragraph(f"<b>Risk Level:</b> {data['risk_level']}", styles["Normal"]))
    content.append(Paragraph(f"<b>Risk Score:</b> {data['risk_score']} / 100", styles["Normal"]))

    for r in data["risks"]:
        content.append(Paragraph(f"- {r}", styles["Normal"]))

    content.append(Paragraph("<br/><b>Risk Explanation</b><br/>", styles["Heading2"]))
    for exp in data["risk_explanations"].values():
        content.append(Paragraph(f"- {exp}", styles["Normal"]))

    content.append(Paragraph("<br/><b>Credit Opinion</b><br/>", styles["Heading2"]))
    content.append(Paragraph(data["credit_opinion"], styles["Normal"]))

    content.append(Paragraph("<br/><b>Qualitative Strengths</b><br/>", styles["Heading2"]))
    for s in data["strengths"]:
        content.append(Paragraph(f"- {s}", styles["Normal"]))

    content.append(Paragraph("<br/><b>Qualitative Weaknesses</b><br/>", styles["Heading2"]))
    for w in data["weaknesses"]:
        content.append(Paragraph(f"- {w}", styles["Normal"]))

    content.append(Paragraph("<br/><b>Summary</b><br/>", styles["Heading2"]))
    content.append(Paragraph(data["summary"], styles["Normal"]))

    content.append(Paragraph("<br/><b>Recommendation</b><br/>", styles["Heading2"]))
    content.append(Paragraph(data["recommendation"], styles["Normal"]))

    doc.build(content)

    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)