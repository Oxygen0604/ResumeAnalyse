import secrets

# 生成一个 URL 安全的随机字符串
secret_key = secrets.token_urlsafe(32)  # 32 字节
print(secret_key)