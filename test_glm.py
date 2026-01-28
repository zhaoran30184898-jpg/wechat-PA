"""简单测试GLM API"""
import asyncio
from zhipuai import ZhipuAI

# 配置API密钥
API_KEY = "59edcc9980e84076a3ff625750170211.xwXTs5AmZqxOGH1U"  # GLM API密钥

def test_glm_sync():
    """同步测试GLM API"""
    print("创建GLM客户端...")
    client = ZhipuAI(api_key=API_KEY)

    print("发送测试请求...")
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",  # 使用免费/低成本的模型进行测试
            messages=[
                {"role": "user", "content": "请用一句话介绍什么是化油器（carburetor）"}
            ],
            temperature=0.7,
            max_tokens=500
        )

        print("\n响应:")
        if response.choices:
            print(response.choices[0].message.content)
        print("\n测试成功！")
        return True

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_glm_async():
    """异步测试GLM API"""
    print("创建GLM异步客户端...")
    # GLM SDK不支持原生异步，使用线程池
    import asyncio
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, test_glm_sync)
    return success


if __name__ == "__main__":
    # 检查API密钥
    if API_KEY == "your_glm_api_key_here":
        print("错误: 请先设置GLM API密钥!")
        print("请在脚本中修改: API_KEY = \"你的API密钥\"")
        exit(1)

    print("=" * 60)
    print("GLM API 连接测试")
    print("=" * 60)
    print(f"API密钥: {API_KEY[:20]}...")
    print(f"模型: glm-4-flash (免费模型)")
    print("=" * 60)
    print()

    # 运行测试
    success = asyncio.run(test_glm_async())

    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] GLM API 连接正常!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("[FAILED] GLM API 连接失败!")
        print("=" * 60)
