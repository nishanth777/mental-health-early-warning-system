from app.auth.email_service import send_email

try:
    response = send_email(
        to_email="nishanthmr77777@gmail.com",
        subject="Clarity Email Verification Test",
        html_content="""
        <h2>Email delivery test</h2>
        <p>Your Flask backend successfully sent this email using Resend.</p>
        <p>Email verification setup is progressing!</p>
        """
    )

    print("Email sent successfully!")
    print(response)

except Exception as error:
    print("Email sending failed.")
    print(error)