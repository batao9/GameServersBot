# Discord Game Server Bot

Discord 上で複数のゲームサーバー（例: Minecraft, Sons of the Forest, Ark など）を管理するためのボットです。  
Discord チャットを通じて、ゲームサーバーの起動、停止、状態確認などを簡単に操作できます。
身内で遊ぶとき向けです。

---

## 機能

- **複数のゲームサーバーを管理**:
  - 各ゲームサーバーに対応するコマンド（例: `mc.start`, `sof.start`）を使用して操作可能。
- **サーバーの起動・停止**
  - `<prefix>.start` コマンドで、特定のサーバーを起動。
  - `<prefix>.stop` コマンドで、特定のサーバーを停止。
- **サーバーの状態確認**:
  - `r.status` コマンドで、すべてのサーバーの状態を一覧表示。
  - `<prefix>.status` コマンドで、特定のサーバーの状態を確認。
- **ヘルプメッセージ**:
  - `r.help` コマンドで、利用可能なゲームサーバーとコマンドを確認。
  - `<prefix>.help` コマンドで、特定のゲームサーバーの詳細なコマンドを確認。
- **管理者専用コマンド**:
  - 管理者のみが実行可能な `.cmd` コマンドをサポート（例: 任意のサーバーコマンドを送信）。

---

## セットアップ

1. **必要なライブラリをインストール**
   ```bash
   pip install -r requirements.txt
   ```

2. **`config.json` を設定**
   - `config.json` ファイルを作成し、以下のように記述。

   ```json
   {
       "token": "YOUR_DISCORD_BOT_TOKEN",
       "games": [
           {
               "name": "minecraft",
               "prefix": "mc",
               "runsh": "Servers/mc/run.sh",
               "stop_method": "command",
               "stop_command": "stop",
               "admin_only_commands": true,
               "enabled": true
           },
           {
               "name": "sons_of_the_forest",
               "prefix": "sof",
               "runsh": "Servers/sof/run.sh",
               "stop_method": "ctrl_c",
               "stop_wait_time": 120,
               "admin_only_commands": false,
               "enabled": true
           }
       ]
   }
   ```

   - **`token`**: Discord Bot のトークンを設定。
   - **`games`**: 管理するゲームサーバーの設定を記述。
     - `name`: ゲームの名前。
     - `prefix`: Discord コマンドで使用するプレフィックス（例: `mc`）。
     - `runsh`: サーバー起動スクリプトのパス。
     - `stop_method`: サーバー停止方法（`command` または `ctrl_c`）。
     - `stop_command`: 停止コマンド（`stop_method` が `command` の場合に必要）。
     - `stop_wait_time`: 停止コマンド送信後に待機する時間（秒単位）。
     - `admin_only_commands`: 管理者専用コマンドを有効にするかどうか。
     - **`enabled`**:
        - `true`: サーバーを有効化（ボットで管理対象にする）。
        - `false`: サーバーを無効化（ボットで管理対象から外す）。

4. **ボットを起動**
   ```bash
   python serverstarterbot.py
   ```

---

## 使用方法

### **基本コマンド**

- **`r.help`**:
  - 利用可能なゲームサーバーとコマンドを一覧表示。

- **`r.status`**:
  - すべてのゲームサーバーの現在の状態を一覧表示。

- **`r.reload`**:
  - 設定ファイル（`config.json`）を再読み込みし、ゲームサーバーの設定を更新。
  - サーバーの有効/無効を切り替えるには、`config.json`の`enabled`項目を変更してから`r.reload`を実行する。

- **`<prefix>.help`**:
  - 特定のゲームサーバーの詳細なコマンドを表示。

- **`<prefix>.start`**:
  - 指定したゲームサーバーを起動。

- **`<prefix>.stop`**:
  - 指定したゲームサーバーを停止。

- **`<prefix>.kill`**:
  - 指定したゲームサーバーを強制終了。

- **`<prefix>.status`**:
  - 指定したゲームサーバーの現在の状態を確認。

- **`<prefix>.cmd <コマンド>`**:
  - 任意のコマンドをサーバーに送信（管理者専用）。
  - 例：`mc.cmd time set day`

---
