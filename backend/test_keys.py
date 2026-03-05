import google.genai as genai
from config import config

with open("test_api_keys.log", "w", encoding="utf-8") as f:
    f.write("Testing API Keys...\n")
    for k in config.GEMINI_API_KEYS:
        f.write(f"Testing key ending in ...{k[-4:]}\n")
        try:
            client = genai.Client(api_key=k)
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents='Say hello'
            )
            f.write(" -> OK: " + response.text.replace('\n', ' ') + "\n")
        except Exception as e:
            f.write(f" -> FAIL: {type(e).__name__}: {str(e)}\n")
