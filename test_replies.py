import sys
sys.path.append(r'c:\python projects\csm bot_new\core')
from nlp_engine.chatbot_v3 import get_bot_response

for i in range(1, 30):
    msg = f"hello {i}"
    resp = get_bot_response(msg)
    print(i, resp)
