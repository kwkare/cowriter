import httpx
from cowriter import CONFIG

print("API Key length:", len(CONFIG.aiSettings.openai_api_key))
print("API Key first 8:", CONFIG.aiSettings.openai_api_key[:8])
print("Base URL:", CONFIG.aiSettings.openai_base_url)
print("Model:", CONFIG.aiSettings.openai_model)
print("Provider type:", CONFIG.aiSettings.provider_type)

# Check if headers have non-ASCII
headers = {
    "Authorization": f"Bearer {CONFIG.aiSettings.openai_api_key}",
    "Content-Type": "application/json",
}
for k, v in headers.items():
    try:
        v.encode("ascii")
        print(f"Header {k}: ASCII OK")
    except UnicodeEncodeError as e:
        print(f"Header {k}: FAILED - {e}")
