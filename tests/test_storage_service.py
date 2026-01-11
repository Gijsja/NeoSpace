
import pytest
import os
import shutil
from services.storage_service import StorageService

def test_save_file_raw(app):
    with app.app_context():
        # Setup a temporary upload folder
        test_upload = "static/test_uploads"
        app.config["UPLOAD_FOLDER"] = test_upload
        app.config["STORAGE_SHARDING"] = False
        
        # Save raw bytes
        filename = "test_raw.bin"
        user_id = 123
        res_url = StorageService.save_file(b"content", user_id, "test_cat", filename=filename)
        
        assert res_url.startswith("/files/user_123/test_cat/test_raw.bin")
        
        # Verify file exists on disk
        full_path = os.path.join(app.root_path, test_upload, "user_123", "test_cat", filename)
        assert os.path.exists(full_path)
        with open(full_path, 'rb') as f:
            assert f.read() == b"content"
            
        # Cleanup
        shutil.rmtree(os.path.join(app.root_path, test_upload))

def test_save_file_sharding(app):
    with app.app_context():
        app.config["STORAGE_SHARDING"] = True
        app.config["UPLOAD_FOLDER"] = "static/sharded_uploads"
        
        user_id = 98765
        shard = "65" # last 2 digits
        res_url = StorageService.save_file(b"data", user_id, "cat")
        
        assert f"/{shard}/user_98765/cat/" in res_url
        
        # Cleanup
        shutil.rmtree(os.path.join(app.root_path, "static/sharded_uploads"))

def test_get_url(app):
    with app.app_context():
        from services.storage_service import LocalStorage
        ls = LocalStorage("static/uploads")
        
        assert ls.get_url("/files/foo.jpg") == "/files/foo.jpg"
        assert ls.get_url("/static/uploads/bar.png") == "/files/bar.png"
        assert ls.get_url("baz.webp") == "/files/baz.webp"

def test_unsupported_backend(app):
    with app.app_context():
        app.config["STORAGE_BACKEND"] = "s3"
        with pytest.raises(ValueError, match="Unsupported storage backend"):
            StorageService.get_backend()
