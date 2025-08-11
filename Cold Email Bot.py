def generate_email(to_name, company):
    subject = f"Grow {company} with AI Marketing Tools"
    body = (
        f"Hi {to_name},\n\n"
        f"We're helping businesses like {company} increase conversions using AI-driven outreach tools.\n"
        "Let's book a quick 15-minute chat this week.\n\n"
        "Best,\nYour Marketing Team"
    )
    return subject, body

subject, body = generate_email("John", "TechCo")
print("Subject:", subject)
print("Body:\n", body)
