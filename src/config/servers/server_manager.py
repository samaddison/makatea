import json
import os
from dataclasses import asdict
from typing import List, Optional

from config.servers.spring_boot_server import SpringBootServer


class ServerManager:
    def __init__(self):
        self.home_dir = os.path.expanduser("~")
        self.config_dir = os.path.join(self.home_dir, ".makatea")
        self.config_file = os.path.join(self.config_dir, "servers.json")
        self.servers: List[SpringBootServer] = []

        self._ensure_config_dir()
        self._load_servers()

    def _ensure_config_dir(self):
        os.makedirs(self.config_dir, exist_ok=True)

    def _load_servers(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                data = json.load(f)
                self.servers = [SpringBootServer.from_dict(item) for item in data]

    def _save_servers(self):
        with open(self.config_file, "w") as f:
            json.dump([asdict(server) for server in self.servers], f, indent=2)

    def add_server(self, server: SpringBootServer):
        self.servers.append(server)
        self._save_servers()

    def remove_server(self, server_id: str) -> bool:
        original_len = len(self.servers)
        self.servers = [s for s in self.servers if s.id != server_id]
        if len(self.servers) < original_len:
            self._save_servers()
            return True
        return False

    def edit_server(self, server_id: str, **kwargs) -> bool:
        for server in self.servers:
            if server.id == server_id:
                for key, value in kwargs.items():
                    if hasattr(server, key):
                        setattr(server, key, value)
                self._save_servers()
                return True
        return False

    def get_server(self, server_id: str) -> Optional[SpringBootServer]:
        return next((s for s in self.servers if s.id == server_id), None)

    def list_servers(self) -> List[SpringBootServer]:
        return self.servers
