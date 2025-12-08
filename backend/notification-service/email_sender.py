"""
Email sender service for sending notifications.
Uses SMTP to send emails (can be configured for Gmail, SendGrid, etc.)
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class EmailSender:
    """
    Email sender using SMTP.
    """

    def __init__(self):
        """Initialize email sender with configuration from environment variables."""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_pass = os.getenv('SMTP_PASS', '')
        self.sender_email = os.getenv('SENDER_EMAIL', self.smtp_user)
        self.sender_name = os.getenv('SENDER_NAME', 'Talentlink')

        # For development/testing: if no SMTP credentials, use console logging
        self.use_console = not self.smtp_user or not self.smtp_pass

    def send_application_accepted_email(self, employee_email, employee_username, job_title=None):
        """
        Send email notification when an application is accepted.

        Args:
            employee_email (str): Email address of the employee
            employee_username (str): Username of the employee
            job_title (str, optional): Title of the job
        """
        if not employee_email:
            print("⚠️ Cannot send email: employee email is missing")
            return False

        subject = "🎉 Your Job Application Has Been Accepted!"

        # Create HTML email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    color: #4CAF50;
                    font-size: 24px;
                    margin-bottom: 20px;
                }}
                .message {{
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <div class="header">Congratulations {employee_username}!</div>
                    <div class="message">
                        <p>Great news! Your job application has been accepted.</p>
                        {f'<p><strong>Position:</strong> {job_title}</p>' if job_title else ''}
                        <p>The employer has reviewed your application and would like to move forward with the interview process.</p>
                        <p>You should expect to receive further details about the interview schedule soon.</p>
                        <p><strong>Next Steps:</strong></p>
                        <ul>
                            <li>Check your Talentlink account for interview details</li>
                            <li>Prepare your documents and portfolio</li>
                            <li>Research the company and position</li>
                        </ul>
                    </div>
                    <div class="footer">
                        <p>This is an automated message from Talentlink.</p>
                        <p>Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version
        text_body = f"""
Congratulations {employee_username}!

Great news! Your job application has been accepted.
{f'Position: {job_title}' if job_title else ''}

The employer has reviewed your application and would like to move forward with the interview process.
You should expect to receive further details about the interview schedule soon.

Next Steps:
- Check your Talentlink account for interview details
- Prepare your documents and portfolio
- Research the company and position

---
This is an automated message from Talentlink.
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        return self._send_email(employee_email, subject, text_body, html_body)

    def _send_email(self, to_email, subject, text_body, html_body=None):
        """
        Send an email using SMTP.

        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            text_body (str): Plain text email body
            html_body (str, optional): HTML email body

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # For development: just print to console
        if self.use_console:
            print("\n" + "="*80)
            print("📧 EMAIL NOTIFICATION (Console Mode - No SMTP configured)")
            print("="*80)
            print(f"To: {to_email}")
            print(f"From: {self.sender_name} <{self.sender_email}>")
            print(f"Subject: {subject}")
            print("-"*80)
            print(text_body)
            print("="*80 + "\n")
            return True

        # Production: send via SMTP
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = to_email

            # Attach text and HTML parts
            part1 = MIMEText(text_body, 'plain')
            message.attach(part1)

            if html_body:
                part2 = MIMEText(html_body, 'html')
                message.attach(part2)

            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(message)

            print(f"✅ Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False
