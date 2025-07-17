# redis_manager.py
import redis
import hashlib
import json

class RedisGroupManager:
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.redis = redis.Redis.from_url(redis_url)  # Changed from self.r to self.redis for consistency

    def hash_file(self, file_path):
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def get_key(self, project_id, filename):
        return f"{project_id}:{filename}"

    def get_or_create_group_id(self, project_id, filename, file_path):
        key = self.get_key(project_id, filename)
        file_hash = self.hash_file(file_path)
        existing_versions = self.redis.lrange(key, 0, -1)  # Changed from self.r to self.redis

        # Check if the hash already exists
        for version_json in existing_versions:
            version = json.loads(version_json.decode('utf-8'))  # Added decode for bytes to string conversion
            if version["hash"] == file_hash:
                return version["group_id"], True  # existing

        version_num = len(existing_versions) + 1
        group_id = f"{project_id}_{filename}_v{version_num}"
        self.redis.rpush(key, json.dumps({"hash": file_hash, "group_id": group_id}))  # Changed from self.r to self.redis
        return group_id, False
    
    def update_latest_version(self, project_id, filename, file_hash, group_id):
        doc_key = self.get_key(project_id, filename)
        versions = self.redis.lrange(doc_key, 0, -1)
    
        version_info = {"hash": file_hash, "group_id": group_id}
    
        # Overwrite latest version (last element)
        if versions:
            self.redis.lset(doc_key, -1, json.dumps(version_info))
        else:
            self.redis.rpush(doc_key, json.dumps(version_info))

    def get_version_history(self, project_id, filename):
        """Get the version history of a document"""
        doc_key = self.get_key(project_id, filename)
        versions = self.redis.lrange(doc_key, 0, -1)
        return [json.loads(version.decode('utf-8')) for version in versions]
