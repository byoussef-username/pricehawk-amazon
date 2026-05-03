import smtplib
from email.message import EmailMessage

async def send_notification(client_email, message):
    msg = EmailMessage()
    msg['Subject'] = 'PriceHawk: Price Drop Alert!'
    msg['From'] = 'your_email@gmail.com'
    msg['To'] = client_email
    msg.set_content(message)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('your_email@gmail.com', 'your_app_password')
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")