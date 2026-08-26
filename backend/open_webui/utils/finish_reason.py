"""Normalize provider finish reasons into truthful chat output state."""

from __future__ import annotations

from typing import Any

PREMATURE_EOF_FINISH_REASON = 'premature_eof'
MISSING_FINISH_REASON = 'missing_finish_reason'
MALFORMED_STREAM_FINISH_REASON = 'malformed_stream'
RESPONSE_FAILED_FINISH_REASON = 'response_failed'
RESPONSE_CANCELLED_FINISH_REASON = 'response_cancelled'
INCOMPLETE_FINISH_REASONS = frozenset(
    {
        'length',
        'max_tokens',
        'max_output_tokens',
        'content_filter',
        'incomplete',
        MALFORMED_STREAM_FINISH_REASON,
        MISSING_FINISH_REASON,
        PREMATURE_EOF_FINISH_REASON,
        RESPONSE_CANCELLED_FINISH_REASON,
        RESPONSE_FAILED_FINISH_REASON,
    }
)
TERMINAL_RESPONSES_EVENTS = frozenset(
    {
        'response.completed',
        'response.incomplete',
        'response.failed',
        'response.cancelled',
    }
)


def update_finish_reason(current: str | None, event: dict[str, Any]) -> str | None:
    """Return the latest non-empty Chat Completions finish reason in an SSE event."""
    choices = event.get('choices')
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        reason = choices[0].get('finish_reason')
        if isinstance(reason, str) and reason:
            return reason

    if event.get('type') == 'response.incomplete':
        response = event.get('response')
        details = response.get('incomplete_details') if isinstance(response, dict) else None
        reason = details.get('reason') if isinstance(details, dict) else None
        return reason if isinstance(reason, str) and reason else 'incomplete'

    if event.get('type') == 'response.failed':
        return RESPONSE_FAILED_FINISH_REASON

    if event.get('type') == 'response.cancelled':
        return RESPONSE_CANCELLED_FINISH_REASON

    return current


def non_streaming_finish_reason(event: dict[str, Any]) -> str | None:
    """Require a semantic terminal reason for non-streaming Chat Completions."""
    reason = update_finish_reason(None, event)
    choices = event.get('choices')
    if isinstance(choices, list) and choices and isinstance(choices[0], dict) and reason is None:
        return MISSING_FINISH_REASON
    return reason


def is_responses_terminal_event(event: dict[str, Any]) -> bool:
    """Return whether a decoded Responses API event explicitly terminates its stream."""
    return event.get('type') in TERMINAL_RESPONSES_EVENTS


def finish_reason_after_stream(
    finish_reason: str | None,
    *,
    done_sentinel_seen: bool,
    responses_terminal_event_seen: bool,
    intentionally_stopped: bool = False,
    malformed_event_seen: bool = False,
) -> str | None:
    """Enforce each streaming protocol's full terminal sequence."""
    if intentionally_stopped:
        return finish_reason
    if malformed_event_seen:
        return MALFORMED_STREAM_FINISH_REASON
    if responses_terminal_event_seen:
        return finish_reason
    if finish_reason is not None and done_sentinel_seen:
        return finish_reason
    return PREMATURE_EOF_FINISH_REASON


def is_incomplete_finish_reason(finish_reason: str | None) -> bool:
    return finish_reason in INCOMPLETE_FINISH_REASONS


def finalize_output_statuses(output: list[dict], finish_reason: str | None) -> list[dict]:
    """Close pending output items, preserving an incomplete final assistant message."""
    for item in output:
        if item.get('status') == 'in_progress':
            item['status'] = 'completed'

    if not is_incomplete_finish_reason(finish_reason):
        return output

    target = next(
        (item for item in reversed(output) if item.get('type') == 'message'),
        output[-1] if output else None,
    )
    if target is not None and target.get('status') != 'failed':
        target['status'] = 'incomplete'
        target['finish_reason'] = finish_reason

    return output
