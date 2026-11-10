import json
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any

DATA_FILE = os.path.join(os.path.dirname(__file__), "store.json")

# Default user accounts for admin access
INITIAL_USERS = [
    {
        "id": "usr_admin",
        "email": "admin@tvadmin.io",
        "username": "admin",
        "name": "Super Admin",
        "password": "admin",
        "role": "Administrator"
    },
    {
        "id": "usr_linkdesk",
        "email": "admin@linkdesk.io",
        "username": "admin@linkdesk.io",
        "name": "LinkDesk Admin",
        "password": "admin",
        "role": "Administrator"
    }
]

class MemoryStore:
    def __init__(self):
        self._load()

    def _load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.urls: list[dict[str, Any]] = data.get("urls", [])
                    self.users: list[dict[str, Any]] = data.get("users", INITIAL_USERS)
                    return
            except Exception:
                pass
        self.urls = []
        self.users = [dict(u) for u in INITIAL_USERS]
        self.save()

    def save(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"urls": self.urls, "users": self.users}, f, indent=2)
        except Exception as e:
            print(f"Error saving data file: {e}")

    # --- User operations ---
    def find_user_by_credential(self, identifier: str) -> Optional[dict[str, Any]]:
        id_lower = identifier.lower().strip()
        for u in self.users:
            if u.get("email", "").lower() == id_lower or u.get("username", "").lower() == id_lower:
                return u
        return None

    def get_user_by_id(self, user_id: str) -> Optional[dict[str, Any]]:
        for u in self.users:
            if u.get("id") == user_id:
                return u
        return None

    # --- URL operations ---
    def list_urls(self) -> list[dict[str, Any]]:
        return list(self.urls)

    def get_url(self, url_id: str) -> Optional[dict[str, Any]]:
        for item in self.urls:
            if item.get("id") == url_id:
                return item
        return None

    def add_url(self, data: dict[str, Any]) -> dict[str, Any]:
        now_str = datetime.now(timezone.utc).isoformat()
        name_val = data.get("title") or data.get("name") or "Untitled Stream"
        addr_val = data.get("url") or data.get("address") or ""
        desc_val = data.get("description") or data.get("notes") or ""

        new_entry = {
            "id": f"url_{int(datetime.now().timestamp() * 1000)}",
            "title": name_val,
            "name": name_val,
            "url": addr_val,
            "address": addr_val,
            "category": data.get("category") or "General",
            "description": desc_val,
            "notes": desc_val,
            "environment": data.get("environment") or "production",
            "status": data.get("status") or "active",
            "refreshInterval": int(data.get("refreshInterval") or 0),
            "createdAt": now_str,
            "updatedAt": now_str,
        }
        self.urls.insert(0, new_entry)
        self.save()
        return new_entry

    def update_url(self, url_id: str, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        for idx, item in enumerate(self.urls):
            if item.get("id") == url_id:
                now_str = datetime.now(timezone.utc).isoformat()
                
                # Handle unified name/title
                if "title" in data and data["title"] is not None:
                    item["title"] = data["title"]
                    item["name"] = data["title"]
                elif "name" in data and data["name"] is not None:
                    item["title"] = data["name"]
                    item["name"] = data["name"]

                # Handle unified url/address
                if "url" in data and data["url"] is not None:
                    item["url"] = data["url"]
                    item["address"] = data["url"]
                elif "address" in data and data["address"] is not None:
                    item["url"] = data["address"]
                    item["address"] = data["address"]

                # Handle unified notes/description
                if "description" in data and data["description"] is not None:
                    item["description"] = data["description"]
                    item["notes"] = data["description"]
                elif "notes" in data and data["notes"] is not None:
                    item["description"] = data["notes"]
                    item["notes"] = data["notes"]

                for field in ["category", "environment", "status", "refreshInterval"]:
                    if field in data and data[field] is not None:
                        item[field] = data[field]

                item["updatedAt"] = now_str
                self.urls[idx] = item
                self.save()
                return item
        return None

    def delete_url(self, url_id: str) -> bool:
        initial_len = len(self.urls)
        self.urls = [item for item in self.urls if item.get("id") != url_id]
        if len(self.urls) < initial_len:
            self.save()
            return True
        return False

    def toggle_url_status(self, url_id: str) -> Optional[dict[str, Any]]:
        for idx, item in enumerate(self.urls):
            if item.get("id") == url_id:
                new_status = "inactive" if item.get("status") == "active" else "active"
                item["status"] = new_status
                item["updatedAt"] = datetime.now(timezone.utc).isoformat()
                self.urls[idx] = item
                self.save()
                return item
        return None

db = MemoryStore()
