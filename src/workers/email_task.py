import smtplib
from email.message import EmailMessage

from fastapi import BackgroundTasks
from pydantic import EmailStr

from src.config import settings


def get_email_template_referal_code(
    username: str,
    email_to: EmailStr,
    referal_code: int,
    href: str,
    href_name: str,
) -> EmailMessage:
    email = EmailMessage()
    email["Subject"] = "Получение реферального кода"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        "<div>"
        f'<h1 style="color: green;">Здравствуй, {username} 😊, Реферальный код для регистрации:</h1>'
        f'<h2 style="color: black; position: absolute;">{referal_code}</h2>'
        f"<h3><a href={href}>{href_name}</a></h3>"
        "</div>",
        subtype="html",
    )

    return email


def send_email_report_referal_code(
    username: str,
    email_to: EmailStr,
    invite_code: int,
    href: str,
    href_name: str,
) -> None:
    email = get_email_template_referal_code(
        username,
        email_to,
        invite_code,
        href,
        href_name,
    )
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(email)


def get_referal_code_report(
    background_tasks: BackgroundTasks,
    email_to: EmailStr,
    username: str,
    referal_code: int,
    href: str = "",
    href_name: str = "",
):
    background_tasks.add_task(
        send_email_report_referal_code,
        username=username,
        email_to=email_to,
        invite_code=referal_code,
        href=href,
        href_name=href_name,
    )
