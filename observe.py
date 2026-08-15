from __future__ import annotations

import asyncio

from context_debug import (
    read_in_event_loop,
    read_in_executor,
    read_with_to_thread,
    request_id,
)


async def main() -> None:
    token = request_id.set("req-2026-001")
    try:
        print(f"event-loop task : {await read_in_event_loop()}")
        print(f"application worker: {await read_in_executor()}")
        print(f"asyncio.to_thread: {await read_with_to_thread()}")
    finally:
        request_id.reset(token)


if __name__ == "__main__":
    asyncio.run(main())
