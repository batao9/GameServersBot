import os
import signal
import asyncio
import json
import logging
import discord
from discord.ext import tasks


class Config:
    """設定ファイルを扱うクラス"""
    def __init__(self, file_path='config.json'):
        with open(file_path) as f:
            self._config = json.load(f)

    @property
    def token(self):
        return self._config["token"]

    @property
    def games(self):
        return self._config["games"]


class DiscordBot:
    """Discordボットのメインクラス"""
    def __init__(self, config):
        self.config = config
        self.client = self._initialize_client()
        self.servers = {game["prefix"]: ServerProcess(game) for game in self.config.games}
        self.game_status = {prefix: "stopped" for prefix in self.servers}  # 初期状態はすべて停止
        self.admin_only = {game["prefix"]: game.get("admin_only_commands", False) for game in self.config.games}

    def _initialize_client(self):
        """Discordクライアントの初期化"""
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            """起動時の処理"""
            print(f'ログインしました: {client.user.name} (ID: {client.user.id})')
            self._update_presence.start()

        @client.event
        async def on_message(message):
            """メッセージ受信時の処理"""
            await self._handle_message(message)

        return client
    
    @tasks.loop(seconds=1)
    async def _update_presence(self):
        """サーバーの状態をチェックし、プレゼンスを更新"""
        presence_message = "r.help | "
        presence_message += " | ".join(
            f"{prefix}: {'Running' if server.is_running() else 'Stopped'}"
            for prefix, server in self.servers.items()
        )
        # Discordのプレゼンスを更新
        await self.client.change_presence(activity=discord.Game(name=presence_message))
        
    async def _handle_message(self, message):
        """メッセージのハンドリング"""
        if message.author.bot:
            return

        command, *args = message.content.split(" ", 1)
        if command == "r.help":
            await self._handle_r_help(message)
        elif command == "r.status":
            await self._handle_r_status(message)
        else:
            prefix, action = command.split(".", 1) if "." in command else (None, None)
            if prefix in self.servers:
                server = self.servers[prefix]
                if action == "start":
                    await self._handle_start_command(message, server, prefix)
                elif action == "stop":
                    await self._handle_stop_command(message, server, prefix)
                elif action == "kill":
                    await self._handle_kill_command(message, server, prefix)
                elif action == "help":
                    await self._handle_help_command(message, prefix)
                elif action == "status":
                    await self._handle_status_command(message, prefix)
                elif action == "cmd" and self.admin_only[prefix]:
                    await self._handle_cmd_command(message, server, prefix, *args)
                else:
                    await message.channel.send(f"無効なコマンドです。`{prefix}.help`で利用可能なコマンドを確認してください。")

    async def _handle_r_help(self, message):
        """r.helpコマンドの処理"""
        help_message = "利用可能なゲームサーバーとコマンド:\n"
        for prefix, server in self.servers.items():
            help_message += (
                f"- **{prefix}**: `{prefix}.help`で詳細を確認\n"
                f"  コマンド例: `{prefix}.start`, `{prefix}.stop`, `{prefix}.status`\n"
            )
        help_message += "\n全体の状態を確認するには`r.status`を使用してください。"
        await message.channel.send(f"{help_message}")

    async def _handle_r_status(self, message):
        """r.statusコマンドの処理"""
        status_message = "現在のサーバーステータス:\n"
        for prefix, server in self.servers.items():
            status_message += f"- {prefix}: {'Running' if server.is_running() else 'Stopped'}\n"
        await message.channel.send(f"{status_message}")


    async def _handle_start_command(self, message, server, prefix):
        """サーバー起動コマンドの処理"""
        if not server.is_running():
            await message.channel.send('サーバー起動します...')
            await server.start()
            self.game_status[prefix] = "running"  # ステータスを更新
        else:
            await message.channel.send('既に起動中です')

    async def _handle_stop_command(self, message, server, prefix):
        """サーバー停止コマンドの処理"""
        if server.is_running():
            await message.channel.send(f"{server.stop_wait_time}秒後にサーバーを停止します...")
            await server.stop()
            self.game_status[prefix] = "stopped"  # ステータスを更新
        else:
            await message.channel.send('既に終了しています')

    async def _handle_kill_command(self, message, server, prefix):
        """サーバー強制終了コマンドの処理"""
        await message.channel.send('強制終了します')
        server.kill()
        self.game_status[prefix] = "stopped"  # ステータスを更新
        
    async def _handle_cmd_command(self, message, server, prefix, command=None):
        """任意のコマンドを実行する処理"""
        # 管理者制限が有効か確認
        if not message.author.guild_permissions.administrator:
            await message.channel.send("このコマンドは管理者のみが実行できます。")
            return

        if not server.is_running():
            await message.channel.send("サーバーが起動していません。")
            return

        if not command:
            await message.channel.send(f"コマンドが指定されていません。`{prefix}.cmd <コマンド>`の形式で入力してください。")
            return

        await message.channel.send(f"`{command}` を実行します...")
        try:
            result = await server.execute_command(command)
            await message.channel.send(f"```\n{result}\n```")
        except Exception as e:
            await message.channel.send(f"コマンド実行中にエラーが発生しました: {e}")

    async def _handle_help_command(self, message, prefix):
        """ヘルプコマンドの処理"""
        # 利用可能なコマンドを動的に生成
        game_name = next(
            (game["name"] for game in self.config.games if game["prefix"] == prefix),
            "Unknown Game"
        )
        help_message = f"**{game_name} ({prefix})** の利用可能なコマンド:\n"
        help_message += f"`{prefix}.help`: このヘルプを表示\n"
        help_message += f"`{prefix}.start`: サーバーを起動\n"
        help_message += f"`{prefix}.stop`: サーバーを停止\n"
        help_message += f"`{prefix}.kill`: サーバーを強制終了\n"
        help_message += f"`{prefix}.status`: サーバーの状態を確認\n"

        # admin_only_commands が true の場合のみ .cmd を追加
        if self.admin_only[prefix]:
            help_message += f"`{prefix}.cmd <コマンド>`: 任意のコマンドを実行 (管理者のみ)\n"

        await message.channel.send(f"{help_message}")

    async def _handle_status_command(self, message, prefix):
        """特定のゲームサーバーの状態を確認するコマンド"""
        server = self.servers[prefix]
        status = "Running" if server.is_running() else "Stopped"
        await message.channel.send(f"{prefix}: {status}")

    def run(self):
        """ボットを起動"""
        self.client.run(self.config.token)


class ServerProcess:
    """サーバープロセスを管理するクラス"""
    def __init__(self, game_config):
        self.server = None
        self.command = [game_config["runsh"]]
        self.stop_method = game_config["stop_method"]
        self.stop_command = game_config.get("stop_command", None)
        self.runsh_dir = os.path.dirname(game_config["runsh"])
        self.runsh = os.path.basename(game_config["runsh"])
        self.stop_wait_time = game_config.get("stop_wait_time", 5)

    async def start(self):
        """サーバーを起動"""
        if not self.is_running():
            try:
                # 起動スクリプトのディレクトリに移動して実行
                self.server = await asyncio.create_subprocess_exec(
                    f"./{self.runsh}",
                    cwd=self.runsh_dir,  # 実行ディレクトリを指定
                    preexec_fn=os.setsid,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            except Exception as e:
                print(f"サーバー起動中にエラーが発生しました: {e}")
        else:
            print("サーバーは既に起動しています")

    async def stop(self):
        """サーバーを停止"""
        if self.is_running():
            if self.stop_method == "command" and self.stop_command:
                print(f"{self.stop_wait_time}秒後に終了します。")
                await asyncio.sleep(self.stop_wait_time)

                self.server.stdin.write(f"{self.stop_command}\n".encode())
                await self.server.stdin.drain()

                try:
                    # プロセスが終了するのを待つ
                    await asyncio.wait_for(self.server.wait(), timeout=15)
                    self.server = None
                    print("正常に終了しました。")
                except asyncio.TimeoutError:
                    print("サーバーの停止がタイムアウトしました。強制終了します。")
                    self.kill()
            elif self.stop_method == "ctrl_c":
                print(f"{self.stop_wait_time}秒後に終了します。")
                await asyncio.sleep(self.stop_wait_time)
                
                if self.server and self.server.pid:
                    print("サーバーにSIGINTを送信します。")
                    os.killpg(os.getpgid(self.server.pid), signal.SIGINT)

                try:
                    # プロセスが終了するのを待つ
                    await asyncio.wait_for(self.server.wait(), timeout=15)
                    self.server = None
                    print("正常に終了しました。")
                except asyncio.TimeoutError:
                    print("サーバーの停止がタイムアウトしました。強制終了します。")
                    self.kill()
        else:
            print("サーバーは既に停止しています")

    def kill(self):
        """サーバーを強制終了"""
        if self.is_running():
            self.server.terminate()
            self.server = None
            print("サーバーを強制終了しました")
        else:
            print("サーバーは既に停止しています")

    def is_running(self):
        """サーバーが起動中かどうかを確認"""
        return self.server is not None and self.server.returncode is None
    
    async def execute_command(self, command):
        """任意のコマンドをサーバーに送信して結果を取得"""
        if self.is_running():
            # コマンドの識別子を設定
            start_marker = "[BOT_CMD_START]"
            end_marker = "[BOT_CMD_END]"

            # サーバーにコマンドを送信
            self.server.stdin.write(f"say {start_marker}\n".encode())  # 開始マーカーを送信
            await self.server.stdin.drain()
            self.server.stdin.write(f"{command}\n".encode())  # 実行コマンドを送信
            await self.server.stdin.drain()
            self.server.stdin.write(f"say {end_marker}\n".encode())  # 終了マーカーを送信
            await self.server.stdin.drain()

            # コマンドの結果を収集
            output_lines = []
            try:
                while True:
                    line = await asyncio.wait_for(self.server.stdout.readline(), timeout=5)
                    decoded_line = line.decode().strip()
                    if start_marker in decoded_line:
                        # 開始マーカーが見つかったら結果の収集を開始
                        output_lines = []
                    elif end_marker in decoded_line:
                        # 終了マーカーが見つかったら収集を終了
                        break
                    else:
                        # 結果を収集
                        output_lines.append(decoded_line)
            except asyncio.TimeoutError:
                return "コマンドの実行がタイムアウトしました"

            # 結果を結合して返す
            return "\n".join(output_lines)
        else:
            return "サーバーは起動していません"


def setup_logging():
    """ログの設定"""
    logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    setup_logging()
    config = Config()
    bot = DiscordBot(config)
    bot.run()
