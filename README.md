# Python `ContextVar` と `run_in_executor()` のデバッグラボ

この最小プロジェクトは、非同期ハンドラーで設定したリクエストIDが `loop.run_in_executor()` へ渡した同期処理で **`missing` になる**挙動を再現し、`asyncio.to_thread()` への最小変更で修正します。主題は、`ContextVar` の値がグローバル変数ではなく、実行中の `Context` に属するという契約です。

## 前提

| 項目 | 固定値 |
| --- | --- |
| Python | 3.11 以上（検証: 3.12.3） |
| 外部依存 | `pytest` のみ |
| ネットワーク・時刻・乱数 | 使用しない |

## 修正済みの状態を検証する

デフォルトブランチは修正済みです。次のコマンドで、同期ログ処理を別スレッドへ退避してもリクエストIDが保持されることを確認できます。

```bash
python3 observe.py
python3 -m pytest -q
```

| 実行経路 | 期待するID | 修正後の実測 |
| --- | --- | --- |
| イベントループ上のTask | `req-2026-001` | `req-2026-001` |
| アプリケーションのワーカー退避経路 | `req-2026-001` | `req-2026-001` |
| `asyncio.to_thread()` の比較経路 | `req-2026-001` | `req-2026-001` |

## 不具合状態を再現する

不具合を再現するコミットへ切り替えると、アプリケーションのワーカー退避経路は低水準の `loop.run_in_executor()` を使い、リクエストIDを失います。

```bash
# 修正前: 1テストが失敗し、観測値は missing になる
git checkout 4b3e8ea
python3 observe.py
python3 -m pytest tests/test_context_debug.py -q

# 修正後: 失敗したテストを残したまま全件が成功する
git checkout master
python3 observe.py
python3 -m pytest -q
```

> `git checkout master` の代わりに、現在のブランチ名を `git branch --show-current` で確認して使ってください。公開リポジトリへpushしていないローカル教材です。

## 構成

```text
.
├── context_debug.py          # バグ修正後の実装
├── observe.py                # 実行経路の観測
├── tests/test_context_debug.py
└── evidence/                 # 実行済みの観測・テスト出力
```

## このラボで守る契約

同期ログ処理をスレッドへ退避しても、同じリクエスト処理の一部であるなら、その処理はリクエストIDを参照できなければなりません。`asyncio.to_thread()` は呼び出し元の `Context` を伝播するため、この用途に適します。低水準のexecutor APIを保持する必要がある場合は、`contextvars.copy_context()` でコピーしたコンテキストの `run()` をexecutorへ渡します。[1] [2] [3]

## 参考資料

[1]: https://docs.python.org/3/library/contextvars.html "Python documentation: contextvars"
[2]: https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread "Python documentation: asyncio.to_thread"
[3]: https://peps.python.org/pep-0567/#offloading-execution-to-other-threads "PEP 567: Context Variables"
