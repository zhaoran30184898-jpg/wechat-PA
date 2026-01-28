"""简单测试Gemini API"""
import google.generativeai as genai

# 配置API密钥
API_KEY = "AIzaSyAE0l6dh9jiXMFzhvhO351GHp3yN9E7lPI"
genai.configure(api_key=API_KEY)

print("创建模型...")
model = genai.GenerativeModel('gemini-1.5-pro')

print("发送测试请求...")
try:
    response = model.generate_content("请用一句话介绍什么是化油器（carburetor）")
    print("\n响应:")
    print(response.text)
    print("\n测试成功！")
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
