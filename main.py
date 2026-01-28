"""应用入口文件 - 微信公众号海外文章自动化搬运工"""
import asyncio
import sys
from loguru import logger
from pathlib import Path

from config import settings


def setup_logging():
    """配置日志系统"""
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(exist_ok=True)

    # 移除默认handler
    logger.remove()

    # 控制台输出
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.app_log_level,
        colorize=True
    )

    # 文件输出
    logger.add(
        sink=log_dir / "app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.app_log_level,
        rotation="00:00",
        retention=f"{settings.log_retention_days}days",
        compression="zip"
    )

    logger.info(f"日志系统初始化完成 - 日志级别: {settings.app_log_level}")


async def test_article_fetch(url: str):
    """测试文章抓取功能"""
    from src.article_fetcher.fetcher import ArticleFetcher
    import json

    logger.info("=" * 60)
    logger.info("测试文章抓取功能")
    logger.info("=" * 60)

    fetcher = ArticleFetcher()
    try:
        await fetcher.start()

        # 抓取文章
        result = await fetcher.fetch(url)

        # 输出结果
        if result.success:
            logger.success("[SUCCESS] 文章抓取成功！")
            logger.info(f"标题: {result.article.title}")
            logger.info(f"作者: {result.article.author or '未知'}")
            logger.info(f"字数: {result.article.word_count}")
            logger.info(f"图片数: {result.article.image_count}")
            logger.info(f"抓取耗时: {result.fetch_time:.2f}秒")

            # 显示文章摘要
            if result.article.content:
                preview = result.article.content[:200] + "..." if len(result.article.content) > 200 else result.article.content
                logger.info(f"内容预览: {preview}")

            # 显示图片URL
            if result.article.images:
                logger.info(f"图片列表:")
                for i, img in enumerate(result.article.images[:5], 1):
                    logger.info(f"  {i}. {img.url}")
                if result.article.image_count > 5:
                    logger.info(f"  ... 还有 {result.article.image_count - 5} 张图片")

            # 保存到JSON文件
            output_file = Path("logs") / f"article_{int(asyncio.get_event_loop().time())}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(
                    result.article.model_dump(mode='json'),
                    f,
                    ensure_ascii=False,
                    indent=2
                )
            logger.info(f"文章数据已保存到: {output_file}")

        else:
            logger.error(f"[FAILED] 文章抓取失败: {result.error_message}")

    finally:
        await fetcher.close()


async def interactive_mode():
    """交互模式 - 用户输入URL"""
    from src.article_fetcher.fetcher import ArticleFetcher

    logger.info("=" * 60)
    logger.info("交互模式 - 输入文章URL进行抓取")
    logger.info("输入 'quit' 或 'exit' 退出")
    logger.info("=" * 60)

    fetcher = ArticleFetcher()
    try:
        await fetcher.start()

        while True:
            try:
                url = input("\n请输入文章URL: ").strip()

                if url.lower() in ['quit', 'exit', 'q']:
                    logger.info("退出交互模式")
                    break

                if not url:
                    logger.warning("URL不能为空")
                    continue

                # 抓取文章
                result = await fetcher.fetch(url)

                if result.success:
                    logger.success(f"[SUCCESS] 抓取成功: {result.article.title}")
                    logger.info(f"   字数: {result.article.word_count}, 图片: {result.article.image_count}")
                else:
                    logger.error(f"[FAILED] 抓取失败: {result.error_message}")

            except KeyboardInterrupt:
                logger.info("\n收到中断信号，退出...")
                break
            except Exception as e:
                logger.exception(f"处理URL时发生错误: {e}")

    finally:
        await fetcher.close()


async def main():
    """主函数"""
    setup_logging()

    logger.info("微信公众号海外文章自动化搬运工启动")
    logger.info(f"环境: {settings.app_env}")
    logger.info(f"时区: {settings.app_timezone}")
    logger.info(f"AI提供商: {settings.ai_provider}")

    # 解析命令行参数
    if len(sys.argv) > 1:
        url = sys.argv[1]
        logger.info(f"测试模式: 抓取URL -> {url}")
        await test_article_fetch(url)
    else:
        logger.info("交互模式: 请输入文章URL")
        await interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n程序已中断")
    except Exception as e:
        logger.exception(f"程序运行出错: {e}")
