# Python `ContextVar` と `run_in_executor()` のデバッグラボ

この最小プロジェクトは、非同期ハンドラーで設定したリクエストIDが `loop.run_in_executor()` へ渡した同期処理で **`missing` になる**挙動を再現します。主題は、`ContextVar` の値がグローバル変数ではなく、実行中の `Context` に属するという契約です。

## 前提

| 項目 | 固定値 |
| --- | --- |
| Python | 3.11 以上（検証: 3.12.3） |
| 外部依存 | `pytest` のみ |
| ネットワーク・時刻・乱数 | 使用しない |

## 不具合状態を再現する

バグ導入コミットをチェックアウトした場合は、観測スクリプトとテストを次のように実行します。

```bash
python3 observe.py
python3 -m pytest tests/test_context_debug.py -q
```

観測の期待値は下表です。現在のTaskと `asyncio.to_thread()` ではIDを読める一方、`run_in_executor()` のワーカーでは既定値が返ります。

| 実行経路 | 期待するID | 不具合状態の実測 |
| --- | --- | --- |
| イベントループ上のTask | `req-2026-001` | `req-2026-001` |
| `loop.run_in_executor()` | `req-2026-001` | `missing` |
| `asyncio.to_thread()` | `req-2026-001` | `req-2026-001` |

## 構成

```text
.
├── context_debug.py          # 再現コード
├── observe.py                # 実行経路の観測
├── tests/test_context_debug.py
└── evidence/                 # 実行済みの観測・テスト出力
```

## このラボで守る契約

同期ログ処理をスレッドへ退避しても、同じリクエスト処理の一部であるなら、その処理はリクエストIDを参照できなければなりません。修正後は、失敗したテストを残したまま全テストを成功させます。

## 参考資料

- [Python documentation: `contextvars`](https://docs.python.org/3/library/contextvars.html)
- [Python documentation: `asyncio.to_thread`](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread)
- [PEP 567: Context Variables](https://peps.python.org/pep-0567/#offloading-execution-to-other-threads)
