import subprocess
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
        self.game_status = {
            "idle": discord.Game("サーバー停止中"),
            "starting": discord.Game("サーバー起動中")
        }

    def _initialize_client(self):
        """Discordクライアントの初期化"""
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            """起動時の処理"""
            print(f'ログインしました: {client.user.name} (ID: {client.user.id})')

        @client.event
        async def on_message(message):
            """メッセージ受信時の処理"""
            await self._handle_message(message)

        return client

    async def _handle_message(self, message):
        """メッセージのハンドリング"""
        if message.author.bot:
            return

        command, *args = message.content.split(" ", 1)
        prefix, action = command.split(".", 1) if "." in command else (None, None)

        if prefix in self.servers:
            server = self.servers[prefix]
            if action == "start":
                await self._handle_start_command(message, server)
            elif action == "stop":
                await self._handle_stop_command(message, server)
            elif action == "kill":
                await self._handle_kill_command(message, server)
            elif action == "cmd":
                await self._handle_cmd_command(message, server, *args)
            else:
                await message.channel.send("無効なコマンドです。`<prefix>.help`で利用可能なコマンドを確認してください。")

    async def _handle_start_command(self, message, server):
        """サーバー起動コマンドの処理"""
        if not server.is_running():
            await message.channel.send('サーバー起動します...')
            await server.start()
        else:
            await message.channel.send('既に起動中です')

    async def _handle_stop_command(self, message, server):
        """サーバー停止コマンドの処理"""
        if server.is_running():
            await message.channel.send('終了します')
            await server.stop()
        else:
            await message.channel.send('既に終了しています')

    async def _handle_kill_command(self, message, server):
        """サーバー強制終了コマンドの処理"""
        await message.channel.send('強制終了します')
        server.kill()

    async def _handle_cmd_command(self, message, server, command=None):
        """任意のコマンドを実行する処理"""
        if not server.is_running():
            await message.channel.send("サーバーが起動していません。")
            return

        if not command:
            await message.channel.send("コマンドが指定されていません。`<prefix>.cmd <コマンド>`の形式で入力してください。")
            return

        await message.channel.send(f"`{command}`")
        result = await server.execute_command(command)
        await message.channel.send(f"```\n{result}\n```")

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

    async def start(self):
        """サーバーを起動"""
        if not self.is_running():
            self.server = await asyncio.create_subprocess_exec(
                *self.command, 
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        else:
            print("サーバーは既に起動しています")

    async def stop(self):
        """サーバーを停止"""
        if self.is_running():
            if self.stop_method == "command" and self.stop_command:
                self.server.stdin.write(f"{self.stop_command}\n".encode())
                await self.server.stdin.drain()
                try:
                    await asyncio.wait_for(self.server.wait(), timeout=15)
                    self.server = None
                except asyncio.TimeoutError:
                    print("サーバーの停止がタイムアウトしました。強制終了します。")
                    self.kill()
            elif self.stop_method == "ctrl_c":
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


def setup_logging():
    """ログの設定"""
    logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    setup_logging()
    config = Config()
    bot = DiscordBot(config)
    bot.run()
