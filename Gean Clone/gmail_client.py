import base64
import json
import os
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://mail.google.com/"]


def get_service(credentials_info: dict, user_email: str):
    creds = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=SCOPES
    ).with_subject(user_email)
    return build("gmail", "v1", credentials=creds)


def get_unread_emails(service, max_results: int = 10) -> list[dict]:
    results = service.users().messages().list(
        userId="me",
        q="is:unread NOT from:me label:inbox",
        maxResults=max_results,
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        data = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()

        headers = data["payload"]["headers"]
        subject = _header(headers, "Subject") or "Sem assunto"
        sender = _header(headers, "From") or "Desconhecido"
        message_id = _header(headers, "Message-ID") or ""
        thread_id = data.get("threadId", "")
        body = _extract_body(data["payload"])

        emails.append({
            "id": msg["id"],
            "thread_id": thread_id,
            "subject": subject,
            "sender": sender,
            "body": body[:2000],
            "message_id": message_id,
        })

    return emails


def send_reply(service, email: dict, reply_text: str, from_name: str = "Gean Santos"):
    msg = MIMEMultipart()
    msg["To"] = email["sender"]
    subject = email["subject"]
    msg["Subject"] = subject if subject.startswith("Re:") else f"Re: {subject}"
    msg["In-Reply-To"] = email["message_id"]
    msg["References"] = email["message_id"]
    msg.attach(MIMEText(reply_text, "plain", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(
        userId="me",
        body={"raw": raw, "threadId": email["thread_id"]},
    ).execute()


def mark_as_read(service, message_id: str):
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()


def _header(headers: list, name: str) -> str:
    return next((h["value"] for h in headers if h["name"] == name), "")


def _extract_body(payload: dict) -> str:
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                if data:
                    return _decode_and_clean(data)
        for part in payload["parts"]:
            if part["mimeType"] == "text/html":
                data = part["body"].get("data", "")
                if data:
                    return _strip_html(_decode_and_clean(data))
    else:
        data = payload["body"].get("data", "")
        if data:
            text = _decode_and_clean(data)
            if payload.get("mimeType") == "text/html":
                return _strip_html(text)
            return text
    return ""


def _decode_and_clean(data: str) -> str:
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore").strip()


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
