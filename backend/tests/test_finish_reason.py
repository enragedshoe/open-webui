import json
import unittest

from open_webui.utils.finish_reason import (
    MALFORMED_STREAM_FINISH_REASON,
    MISSING_FINISH_REASON,
    PREMATURE_EOF_FINISH_REASON,
    RESPONSE_CANCELLED_FINISH_REASON,
    RESPONSE_FAILED_FINISH_REASON,
    finalize_output_statuses,
    finish_reason_after_stream,
    is_incomplete_finish_reason,
    is_responses_terminal_event,
    non_streaming_finish_reason,
    update_finish_reason,
)

SSE_FIXTURES = {
    'stop': [
        'data: {"choices":[{"delta":{"content":"Done"},"finish_reason":null}]}',
        'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}',
        'data: [DONE]',
    ],
    'length': [
        'data: {"choices":[{"delta":{"content":"Partial"},"finish_reason":null}]}',
        'data: {"choices":[{"delta":{},"finish_reason":"length"}]}',
        'data: [DONE]',
    ],
    'content_filter': [
        'data: {"choices":[{"delta":{},"finish_reason":"content_filter"}]}',
        'data: [DONE]',
    ],
    'premature_eof': [
        'data: {"choices":[{"delta":{"content":"Partial"},"finish_reason":null}]}',
    ],
    'finish_without_done': [
        'data: {"choices":[{"delta":{"content":"Looks done"},"finish_reason":null}]}',
        'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}',
    ],
    'responses_completed': [
        'data: {"type":"response.output_text.delta","delta":"Done"}',
        'data: {"type":"response.completed","response":{"status":"completed"}}',
    ],
    'responses_incomplete': [
        'data: {"type":"response.output_text.delta","delta":"Partial"}',
        'data: {"type":"response.incomplete","response":{"status":"incomplete","incomplete_details":{"reason":"max_output_tokens"}}}',
    ],
    'responses_failed': [
        'data: {"type":"response.output_text.delta","delta":"Partial"}',
        'data: {"type":"response.failed","response":{"status":"failed","error":{"code":"server_error"}}}',
    ],
    'responses_cancelled': [
        'data: {"type":"response.output_text.delta","delta":"Partial"}',
        'data: {"type":"response.cancelled","response":{"status":"cancelled"}}',
    ],
    'done_only': ['data: [DONE]'],
}


def finish_reason_from_fixture(lines: list[str], *, tolerate_malformed: bool = False) -> str | None:
    reason = None
    done_sentinel_seen = False
    responses_terminal_event_seen = False
    malformed_event_seen = False
    for line in lines:
        payload = line.removeprefix('data: ').strip()
        if payload == '[DONE]':
            done_sentinel_seen = True
            continue
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            malformed_event_seen = True
            if tolerate_malformed:
                continue
            raise
        reason = update_finish_reason(reason, event)
        responses_terminal_event_seen = responses_terminal_event_seen or is_responses_terminal_event(event)
    return finish_reason_after_stream(
        reason,
        done_sentinel_seen=done_sentinel_seen,
        responses_terminal_event_seen=responses_terminal_event_seen,
        malformed_event_seen=malformed_event_seen,
    )


class FinishReasonTests(unittest.TestCase):
    def test_stop_fixture_completes_output(self):
        reason = finish_reason_from_fixture(SSE_FIXTURES['stop'])
        output = [{'type': 'message', 'status': 'in_progress'}]

        self.assertEqual(reason, 'stop')
        self.assertFalse(is_incomplete_finish_reason(reason))
        self.assertEqual(finalize_output_statuses(output, reason)[0]['status'], 'completed')

    def test_length_fixture_marks_final_message_incomplete(self):
        reason = finish_reason_from_fixture(SSE_FIXTURES['length'])
        output = [
            {'type': 'reasoning', 'status': 'in_progress'},
            {'type': 'message', 'status': 'in_progress'},
        ]

        self.assertEqual(reason, 'length')
        self.assertEqual(
            [item['status'] for item in finalize_output_statuses(output, reason)],
            ['completed', 'incomplete'],
        )
        self.assertEqual(output[-1]['finish_reason'], 'length')

    def test_content_filter_fixture_is_incomplete(self):
        reason = finish_reason_from_fixture(SSE_FIXTURES['content_filter'])
        output = [{'type': 'message', 'status': 'completed'}]

        self.assertTrue(is_incomplete_finish_reason(reason))
        self.assertEqual(finalize_output_statuses(output, reason)[0]['status'], 'incomplete')

    def test_non_choice_events_do_not_erase_the_finish_reason(self):
        self.assertEqual(update_finish_reason('length', {'usage': {'output_tokens': 4}}), 'length')

    def test_eof_without_terminal_event_is_incomplete(self):
        reason = finish_reason_from_fixture(SSE_FIXTURES['premature_eof'])
        output = [{'type': 'message', 'status': 'in_progress'}]

        self.assertEqual(reason, PREMATURE_EOF_FINISH_REASON)
        self.assertEqual(finalize_output_statuses(output, reason)[0]['status'], 'incomplete')

    def test_responses_api_completed_event_is_a_clean_terminal_path(self):
        self.assertIsNone(finish_reason_from_fixture(SSE_FIXTURES['responses_completed']))

    def test_responses_api_incomplete_reason_is_preserved(self):
        reason = finish_reason_from_fixture(SSE_FIXTURES['responses_incomplete'])
        self.assertEqual(reason, 'max_output_tokens')
        self.assertTrue(is_incomplete_finish_reason(reason))

    def test_responses_api_failed_event_is_incomplete(self):
        reason = finish_reason_from_fixture(SSE_FIXTURES['responses_failed'])
        self.assertEqual(reason, RESPONSE_FAILED_FINISH_REASON)
        self.assertTrue(is_incomplete_finish_reason(reason))

    def test_responses_api_cancelled_event_is_incomplete(self):
        reason = finish_reason_from_fixture(SSE_FIXTURES['responses_cancelled'])
        self.assertEqual(reason, RESPONSE_CANCELLED_FINISH_REASON)
        self.assertTrue(is_incomplete_finish_reason(reason))

    def test_malformed_frame_cannot_be_hidden_by_later_stop_and_done(self):
        lines = [
            'data: {not-json}',
            *SSE_FIXTURES['stop'],
        ]
        reason = finish_reason_from_fixture(lines, tolerate_malformed=True)

        self.assertEqual(reason, MALFORMED_STREAM_FINISH_REASON)
        self.assertTrue(is_incomplete_finish_reason(reason))

    def test_done_sentinel_without_reason_is_incomplete(self):
        self.assertEqual(
            finish_reason_from_fixture(SSE_FIXTURES['done_only']),
            PREMATURE_EOF_FINISH_REASON,
        )

    def test_finish_reason_without_done_sentinel_is_incomplete(self):
        self.assertEqual(
            finish_reason_from_fixture(SSE_FIXTURES['finish_without_done']),
            PREMATURE_EOF_FINISH_REASON,
        )

    def test_non_streaming_completion_requires_finish_reason(self):
        event = {'choices': [{'message': {'content': 'Looks done'}, 'finish_reason': None}]}
        reason = non_streaming_finish_reason(event)

        self.assertEqual(reason, MISSING_FINISH_REASON)
        self.assertTrue(is_incomplete_finish_reason(reason))

    def test_intentional_local_stop_is_not_misclassified_as_eof(self):
        self.assertIsNone(
            finish_reason_after_stream(
                None,
                done_sentinel_seen=False,
                responses_terminal_event_seen=False,
                intentionally_stopped=True,
            )
        )


if __name__ == '__main__':
    unittest.main()
