from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any


def _location_label(result: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("city", "state", "country"):
        value = str(result.get(key) or "").strip()
        if value and value not in parts:
            parts.append(value)
    return ", ".join(parts) or "Location unavailable"


def _captured_at_utc(captured_at: datetime | None) -> str:
    value = captured_at or datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return (
        value.astimezone(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def resolve_user_location(
    latitude: float,
    longitude: float,
    *,
    accuracy: float | None = None,
    captured_at: datetime | None = None,
    device_timezone: str | None = None,
) -> dict[str, Any]:
    """Resolve browser coordinates locally and return persisted plus transient context.

    The persisted record deliberately excludes latitude and longitude. Coordinates are
    rounded to three decimals only in the transient prompt context returned to the
    requesting browser.
    """
    import reverse_geocode

    resolved = reverse_geocode.get((latitude, longitude)) or {}
    label = _location_label(resolved)
    updated_at = _captured_at_utc(captured_at)
    timezone_name = (device_timezone or "").strip()[:128]
    accuracy_m = round(accuracy) if accuracy is not None else None

    saved_location = f"{label} (browser location, updated {updated_at})"
    saved_info = {
        "location": saved_location,
        "location_label": label,
        "location_updated_at": updated_at,
        "location_source": "browser",
        "location_accuracy_m": accuracy_m,
    }

    details = [
        label,
        f"approximate coordinates {latitude:.3f}, {longitude:.3f}",
    ]
    if accuracy_m is not None:
        details.append(f"reported accuracy about {accuracy_m} meters")
    details.append(f"captured {updated_at}")
    if timezone_name:
        details.append(f"device time zone {timezone_name}")
    details.append("browser-provided and may be approximate")

    return {
        **saved_info,
        "location_context": "; ".join(details),
    }


async def resolve_user_location_async(*args, **kwargs) -> dict[str, Any]:
    return await asyncio.to_thread(resolve_user_location, *args, **kwargs)
