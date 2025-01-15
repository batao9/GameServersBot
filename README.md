# Discord Game Server Bot

このプロジェクトは、Discord 上で複数のゲームサーバー（例: Minecraft, Sons of the Forest, Ark など）を管理するためのボットです。  
ユーザーは Discord チャットを通じて、ゲームサーバーの起動、停止、状態確認などを簡単に操作できます。

---

## 機能

- **複数のゲームサーバーを管理**:
  - 各ゲームサーバーに対応するコマンド（例: `mc.start`, `sof.start`）を使用して操作可能。
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
   - `config.json` ファイルを作成し、以下のように記述します。

   ```json
   {
       "token": "YOUR_DISCORD_BOT_TOKEN",
       "games": [
           {
               "name": "minecraft",
               "prefix": "mc",
               "runsh": "./path/to/run.sh",
               "stop_method": "command",
               "stop_command": "stop",
               "admin_only_commands": true
           },
           {
               "name": "sons_of_the_forest",
               "prefix": "sof",
               "runsh": "./path/to/run.sh",
               "stop_method": "ctrl_c",
               "stop_wait_time": 120,
               "admin_only_commands": false
           }
       ]
   }
   ```

   - **`token`**: Discord Bot のトークンを設定してください。
   - **`games`**: 管理するゲームサーバーの設定を記述します。
     - `name`: ゲームの名前。
     - `prefix`: Discord コマンドで使用するプレフィックス（例: `mc`）。
     - `runsh`: サーバー起動スクリプトのパス。
     - `stop_method`: サーバー停止方法（`command` または `ctrl_c`）。
     - `stop_command`: 停止コマンド（`stop_method` が `command` の場合に必要）。
     - `stop_wait_time`: 停止コマンド送信後に待機する時間（秒単位）。
     - `admin_only_commands`: 管理者専用コマンドを有効にするかどうか。

4. **ボットを起動**
   ```bash
   python serverstarterbot.py
   ```

---

## 使用方法

### **基本コマンド**

- **`r.help`**:
  - 利用可能なゲームサーバーとコマンドを一覧表示します。

- **`r.status`**:
  - すべてのゲームサーバーの現在の状態を一覧表示します。

- **`<prefix>.help`**:
  - 特定のゲームサーバーの詳細なコマンドを表示します。

- **`<prefix>.start`**:
  - 指定したゲームサーバーを起動します。

- **`<prefix>.stop`**:
  - 指定したゲームサーバーを停止します。

- **`<prefix>.kill`**:
  - 指定したゲームサーバーを強制終了します。

- **`<prefix>.status`**:
  - 指定したゲームサーバーの現在の状態を確認します。

- **`<prefix>.cmd <コマンド>`**:
  - 任意のコマンドをサーバーに送信します（管理者専用）。

---

## 例

### **Minecraft サーバーの操作**
- サーバーを起動:
  ```
  mc.start
  ```

- サーバーを停止:
  ```
  mc.stop
  ```

- サーバーの状態を確認:
  ```
  mc.status
  ```

- サーバーのヘルプを表示:
  ```
  mc.help
  ```

---
