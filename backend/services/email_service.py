"""
email_service.py - Módulo de Disparo de E-mails Transacionais
=============================================================
Gerencia o envio de e-mails para os usuários do Apollo usando SMTP.
Ideal para SendGrid, Resend, Amazon SES, etc.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import asyncio

logger = logging.getLogger("EmailService")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.resend.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER", "resend")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
FROM_NAME = os.getenv("FROM_NAME", "Apollo Edit Web")

def send_email_sync(to_email: str, subject: str, html_content: str):
    """Envia o e-mail de forma síncrona (blocking)."""
    if not SMTP_PASS:
        logger.warning(f"[EmailService] Simulação de envio para {to_email} (SMTP_PASS não configurado). Assunto: {subject}")
        return True

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        logger.info(f"[EmailService] E-mail enviado com sucesso para {to_email}")
        return True
    except Exception as e:
        logger.error(f"[EmailService] Falha ao enviar e-mail para {to_email}: {str(e)}")
        return False

async def send_email_async(to_email: str, subject: str, html_content: str):
    """Executa o disparo de e-mail em uma thread do asyncio para não bloquear o servidor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, send_email_sync, to_email, subject, html_content)


# --- Templates Básicos ---
def get_welcome_template(username: str) -> str:
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #1a1a1a; color: #fff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #2d2d2d; border-radius: 8px; padding: 30px;">
                <h1 style="color: #bb86fc;">Bem-vindo ao Apollo! 🚀</h1>
                <p>Olá {username},</p>
                <p>Sua conta foi criada com sucesso. Prepare-se para automatizar seus canais no YouTube sem cair em shadowbans.</p>
                <br/>
                <p>Equipe Apollo Edit Web</p>
            </div>
        </body>
    </html>
    """

def get_password_reset_template(reset_link: str) -> str:
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #1a1a1a; color: #fff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #2d2d2d; border-radius: 8px; padding: 30px;">
                <h1 style="color: #bb86fc;">Recuperação de Senha 🔑</h1>
                <p>Recebemos uma solicitação para redefinir a senha da sua conta.</p>
                <p>Clique no link abaixo para criar uma nova senha:</p>
                <a href="{reset_link}" style="display: inline-block; padding: 10px 20px; background-color: #bb86fc; color: #000; text-decoration: none; border-radius: 5px; font-weight: bold;">Redefinir Senha</a>
                <br/><br/>
                <p>Se você não solicitou, ignore este e-mail.</p>
                <p>Equipe Apollo Edit Web</p>
            </div>
        </body>
    </html>
    """
