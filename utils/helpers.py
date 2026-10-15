from __future__ import annotations

import socket
from datetime import date
from pathlib import Path

import pandas as pd

from config.settings import PROJECT_ROOT, SETTINGS


def project_root() -> Path:
    return PROJECT_ROOT


def ensure_generated_dir() -> Path:
    SETTINGS.generated_dir.mkdir(parents=True, exist_ok=True)
    return SETTINGS.generated_dir


def month_starts(end: date, months: int) -> list[date]:
    periods = pd.period_range(end=pd.Period(end, freq="M"), periods=months, freq="M")
    return [p.to_timestamp().date() for p in periods]


def add_months(start: date, months: int) -> date:
    return (pd.Timestamp(start) + pd.DateOffset(months=months)).date()


def as_month(d: date | pd.Timestamp) -> date:
    ts = pd.Timestamp(d)
    return date(ts.year, ts.month, 1)


def lan_url(port: int = 8501) -> str:
    """LAN address so a phone on the same Wi-Fi can open the app."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        sock.close()
    return f"http://{ip}:{port}"


def weighted_choice(rng, items: list, weights: list):
    total = float(sum(weights))
    if total <= 0:
        return items[0]
    draw = rng.random() * total
    cumulative = 0.0
    for item, weight in zip(items, weights):
        cumulative += weight
        if draw <= cumulative:
            return item
    return items[-1]
