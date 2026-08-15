"""ContextVar を同期処理へ渡す経路を観測する最小実装。"""

from __future__ import annotations

import asyncio
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="missing")


def read_request_id() -> str:
    """同期的なログ処理を模した、現在のリクエストIDの参照。"""
    return request_id.get()


async def read_in_event_loop() -> str:
    """対照実験: 現在のasyncio Taskから読む。"""
    return read_request_id()


async def read_in_executor() -> str:
    """不具合経路: 低水準executor APIへ同期関数を直接渡す。"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, read_request_id)


async def read_with_to_thread() -> str:
    """比較経路: to_threadは現在のContextを伝播する。"""
    return await asyncio.to_thread(read_request_id)
