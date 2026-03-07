import os
from datetime import datetime, timedelta, date

import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TIMEZONE = os.environ.get("TIMEZONE", "America/Sao_Paulo")


def get_service(credentials_info: dict, user_email: str):
    creds = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=SCOPES
    ).with_subject(user_email)
    return build("calendar", "v3", credentials=creds)


def get_events(service, target_date: date = None, days: int = 1) -> list[dict]:
    tz = pytz.timezone(TIMEZONE)

    if target_date is None:
        target_date = datetime.now(tz).date()

    start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=tz)
    end = start + timedelta(days=days)

    result = service.events().list(
        calendarId="primary",
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return result.get("items", [])


def format_events(events: list[dict], label: str = "hoje") -> str:
    if not events:
        return f"Agenda limpa pra {label} kkk"

    tz = pytz.timezone(TIMEZONE)
    lines = [f"Agenda de {label}:"]

    for event in events:
        start_raw = event["start"].get("dateTime", event["start"].get("date", ""))
        if "T" in start_raw:
            dt = datetime.fromisoformat(start_raw).astimezone(tz)
            time_str = dt.strftime("%H:%M")
        else:
            time_str = "Dia todo"

        summary = event.get("summary", "Sem título")
        location = event.get("location", "")
        line = f"• {time_str} — {summary}"
        if location:
            line += f" ({location})"
        lines.append(line)

    return "\n".join(lines)
