"""
Tactical Tipping Table Generator
- Aggregates all tactical, model, and speculative insights into a single table for each match
- Outputs: outputs/tactical_tipping_table_<date>.csv
"""
import pandas as pd
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def safe_load(path):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def send_email_with_table(subject, html_table, to_emails, from_email, smtp_server, smtp_port, smtp_user, smtp_pass):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails)
    html_content = f"""
    <html>
      <body>
        <h2>{subject}</h2>
        {html_table}
      </body>
    </html>
    """
    msg.attach(MIMEText(html_content, 'html'))
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(from_email, to_emails, msg.as_string())

def main():
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs'))
    today = datetime.now().date()
    # Load all relevant outputs
    tips_path = os.path.join(outputs_dir, f'this_weeks_tips_{today}.csv')
    speculative_path = os.path.join(outputs_dir, f'speculative_sweep_report_{today}.csv')
    ktm_path = os.path.join(outputs_dir, 'kick_target_mapping_report.csv')
    lineup_path = os.path.join(outputs_dir, 'lineup_impact_analysis.csv')
    officiating_path = os.path.join(outputs_dir, 'officiating_impact_analysis.csv')
    weather_path = os.path.join(outputs_dir, 'weather_impact_analysis.csv')
    # Load data
    tips = safe_load(tips_path)
    speculative = safe_load(speculative_path)
    ktm = safe_load(ktm_path)
    lineup = safe_load(lineup_path)
    officiating = safe_load(officiating_path)
    weather = safe_load(weather_path)
    # Build table
    table = []
    for idx, row in tips.iterrows():
        fixture = f"{row['HomeTeam']} vs {row['AwayTeam']}"
        venue_time = f"{row.get('Venue','')} {row.get('Date','')} {row.get('Time','')}"
        model_tip = row.get('RecommendedTip', '')
        ml_win_prob = f"{row.get('HomeWinProb','')}% – {row.get('AwayWinProb','')}%"
        edge_mismatch = ''  # Placeholder: fill from tactical analysis
        ktm_info = ''       # Placeholder: fill from KTM output
        back3_pressure = '' # Placeholder: fill from KTM or analysis
        momentum_trend = row.get('MomentumTrend', '')
        coach_impact = row.get('CoachImpact', '')
        lineup_integrity = row.get('LineupIntegrity', '')
        referee = row.get('Referee', '')
        ref_bunker_risk = row.get('RefBunkerRisk', '')
        weather_impact = row.get('WeatherImpact', '')
        upset_risk = row.get('UpsetRisk', '')
        speculative_overlay = row.get('SpeculativeOverlay', '')
        final_conf = row.get('Confidence', '')
        user_tip = ''
        score_pred = row.get('ScorePrediction', '')
        key_matchup = row.get('KeyMatchup', '')
        table.append({
            "Match Fixture": fixture,
            "Venue & Time": venue_time,
            "Model Tip": model_tip,
            "ML Win Probability": ml_win_prob,
            "Edge Mismatch": edge_mismatch,
            "Kick Target Mapping (KTM)": ktm_info,
            "Back 3 Pressure Analysis": back3_pressure,
            "Momentum Trend": momentum_trend,
            "Coach Impact (Model)": coach_impact,
            "Line-up Integrity Check": lineup_integrity,
            "Referee Assigned": referee,
            "Ref/Bunker Risk": ref_bunker_risk,
            "Weather Impact": weather_impact,
            "Upset Risk Score": upset_risk,
            "Speculative Overlay": speculative_overlay,
            "Final Confidence Rating": final_conf,
            "User Tip (if different)": user_tip,
            "Score Prediction (optional)": score_pred,
            "Key Matchup to Watch": key_matchup
        })
    df = pd.DataFrame(table)
    out_path = os.path.join(outputs_dir, f'tactical_tipping_table_{today}.csv')
    df.to_csv(out_path, index=False)
    print(f"[SUCCESS] Tactical tipping table saved to {out_path}")

if __name__ == "__main__":
    main()
    # Prompt for email at the end
    prompt = input("\nWould you like to email the tactical tipping table? (y/n): ").strip().lower()
    if prompt == 'y':
        default_email = 'slangston1986@gmail.com'
        emails = input(f"Enter recipient email(s) separated by comma (default: {default_email}): ").strip()
        to_emails = [e.strip() for e in emails.split(',') if e.strip()] or [default_email]
        smtp_server = 'smtp.gmail.com'
        smtp_port = 465
        from_email = default_email
        smtp_user = default_email
        smtp_pass = input("Enter the SMTP password or app password for the sender email: ").strip()
        # Load the table as HTML
        outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs'))
        today = datetime.now().date()
        out_path = os.path.join(outputs_dir, f'tactical_tipping_table_{today}.csv')
        df = pd.read_csv(out_path)
        html_table = df.to_html(index=False, border=1)
        send_email_with_table(
            subject=f"NRL Tactical Tipping Table {today}",
            html_table=html_table,
            to_emails=to_emails,
            from_email=from_email,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_pass=smtp_pass
        )
        print(f"[SUCCESS] Tactical tipping table emailed to: {', '.join(to_emails)}")
