import os
import secrets
from abc import ABC, abstractmethod
from flask import current_app
from werkzeug.utils import secure_filename

class BaseStorage(ABC):
    @abstractmethod
    def save(self, file, user_id, category, filename=None):
        pass

    @abstractmethod
    def get_url(self, path):
        pass

class LocalStorage(BaseStorage):
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def _get_user_path(self, user_id, category):
        shard = str(user_id)[-2:].zfill(2) if current_app.config.get("STORAGE_SHARDING") else ""
        if shard:
            path = os.path.join(self.upload_folder, shard, f"user_{user_id}", category)
        else:
            path = os.path.join(self.upload_folder, f"user_{user_id}", category)
        
        os.makedirs(os.path.join(current_app.root_path, path), exist_ok=True)
        return path

    def save(self, file, user_id, category, filename=None):
        if not filename:
            if hasattr(file, 'filename') and file.filename:
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'bin'
            else:
                ext = 'bin'
            filename = f"{secrets.token_urlsafe(12)}.{ext}"
        
        filename = secure_filename(filename)
        rel_path = self._get_user_path(user_id, category)
        full_path = os.path.join(current_app.root_path, rel_path, filename)
        
        if hasattr(file, 'save'):
            file.save(full_path)
        else:
            with open(full_path, 'wb') as f:
                f.write(file)
                
        # Return protected URL
        protected_rel_path = rel_path.replace(self.upload_folder, "").lstrip("/")
        return os.path.join("/files", protected_rel_path, filename)

    def get_url(self, path):
        if not path.startswith('/files'):
            # Convert legacy static paths or raw paths to protected route if possible
            if path.startswith('/static/uploads'):
                path = path.replace('/static/uploads', '/files')
            elif not path.startswith('/'):
                path = '/files/' + path
        return path

class StorageService:
    _instance = None

    @classmethod
    def get_backend(cls):
        backend_type = current_app.config.get("STORAGE_BACKEND", "local")
        if backend_type == "local":
            return LocalStorage(current_app.config.get("UPLOAD_FOLDER", "static/uploads"))
        else:
            raise ValueError(f"Unsupported storage backend: {backend_type}")

    @classmethod
    def save_file(cls, file, user_id, category, filename=None):
        return cls.get_backend().save(file, user_id, category, filename)
