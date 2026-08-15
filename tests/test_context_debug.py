from __future__ import annotations

import asyncio

from context_debug import (
    read_in_event_loop,
    read_in_executor,
    read_with_to_thread,
    request_id,
)


def test_current_asyncio_task_keeps_request_id() -> None:
    """対照ケース: 現在のTaskでは設定済みのIDを読める。"""
    token = request_id.set("req-2026-001")
    try:
        assert asyncio.run(read_in_event_loop()) == "req-2026-001"
    finally:
        request_id.reset(token)


def test_run_in_executor_keeps_request_id_for_sync_log_writer() -> None:
    """期待契約: 同期ログ処理でもリクエストIDを出力できる。"""
    token = request_id.set("req-2026-001")
    try:
        seen_request_id = asyncio.run(read_in_executor())
    finally:
        request_id.reset(token)

    assert seen_request_id == "req-2026-001"


def test_to_thread_keeps_request_id_for_sync_log_writer() -> None:
    """比較ケース: to_threadでは現在のContextが伝播する。"""
    token = request_id.set("req-2026-001")
    try:
        seen_request_id = asyncio.run(read_with_to_thread())
    finally:
        request_id.reset(token)

    assert seen_request_id == "req-2026-001"
