"""
Test httpx header encoding with non-ASCII prompt.
"""
import asyncio
import httpx

async def test():
    headers = {
        "Authorization": "Bearer test-key-123",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "user", "content": "你好世界" * 10 + "带中文的prompt测试"}
        ],
    }
    
    # Just test building the request, not sending it
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            req = client.build_request(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0,
            )
            print("Build OK")
            print("Headers:", dict(req.headers))
        except Exception as e:
            print(f"Build FAILED: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(test())
