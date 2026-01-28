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


async def test_article_rewrite(url: str, style_name: str = None, publish: bool = False):
    """测试AI改写功能"""
    from src.article_fetcher.fetcher import ArticleFetcher
    from src.content_rewriter.rewriter import ContentRewriter
    from src.content_rewriter.style_learning import StyleManager
    from src.models.style import StyleProfile
    from src.wechat_publisher import DraftManager
    import json

    logger.info("=" * 60)
    logger.info("测试AI改写功能")
    logger.info("=" * 60)

    # 加载风格配置（如果指定）
    style = None
    if style_name:
        style_manager = StyleManager()
        style = style_manager.load_style(style_name)
        if style:
            logger.info(f"使用风格: {style.name} - {style.description}")
        else:
            logger.warning(f"未找到风格 '{style_name}'，使用默认风格")

    fetcher = ArticleFetcher()
    rewriter = ContentRewriter()
    draft_manager = None

    if publish:
        draft_manager = DraftManager()

    try:
        await fetcher.start()
        await rewriter.start()

        # 1. 抓取文章
        logger.info("步骤1: 抓取文章")
        fetch_result = await fetcher.fetch(url)

        if not fetch_result.success:
            logger.error(f"抓取失败: {fetch_result.error_message}")
            return

        article = fetch_result.article
        logger.info(f"抓取成功: {article.title}")
        logger.info(f"字数: {article.word_count}")

        # 2. AI改写
        logger.info("\n步骤2: AI改写中...")
        rewrite_result = await rewriter.rewrite_article(article, target_language="zh-CN", style=style)

        logger.success("[SUCCESS] AI改写完成！")

        # 3. 显示结果
        logger.info("\n" + "=" * 60)
        logger.info("原标题: " + article.title)
        logger.info("新标题: " + (article.rewritten_title or "无"))
        logger.info("=" * 60)

        logger.info("\n改写后的内容预览 (前500字):")
        if article.rewritten_content:
            preview = article.rewritten_content[:500] + "..." if len(article.rewritten_content) > 500 else article.rewritten_content
            logger.info(preview)
        else:
            logger.warning("改写内容为空")

        # 4. 保存结果
        output_file = Path("logs") / f"article_rewritten_{int(asyncio.get_event_loop().time())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(
                article.model_dump(mode='json'),
                f,
                ensure_ascii=False,
                indent=2
            )
        logger.info(f"\n改写结果已保存到: {output_file}")

        # 5. 发布到微信草稿（如果指定）
        if publish and draft_manager:
            logger.info("\n步骤3: 发布到微信草稿...")
            try:
                media_id = draft_manager.publish_to_draft(article)
                logger.success(f"[SUCCESS] 草稿发布成功! media_id: {media_id}")

                # 更新JSON文件，保存media_id
                article.wechat_draft_id = media_id
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(
                        article.model_dump(mode='json'),
                        f,
                        ensure_ascii=False,
                        indent=2
                    )
                logger.info(f"已更新文件，保存草稿ID: {output_file}")

            except Exception as e:
                logger.error(f"发布草稿失败: {e}")
                logger.info("文章改写已完成，但未发布到微信草稿")

    except Exception as e:
        logger.exception(f"测试过程出错: {e}")
    finally:
        await fetcher.close()
        await rewriter.close()
        if draft_manager:
            draft_manager.close()


async def list_styles():
    """列出所有可用的风格"""
    from src.content_rewriter.style_learning import StyleManager

    logger.info("=" * 60)
    logger.info("可用的文章风格")
    logger.info("=" * 60)

    style_manager = StyleManager()
    styles = style_manager.list_styles()

    if not styles:
        logger.warning("未找到任何风格配置")
        return

    # 分组显示
    predefined = [s for s in styles if s.is_predefined]
    user_custom = [s for s in styles if not s.is_predefined]

    if predefined:
        logger.info("\n预定义风格:")
        for style in predefined:
            logger.info(f"  - {style.name} - {style.description}")

    if user_custom:
        logger.info("\n用户自定义风格:")
        for style in user_custom:
            logger.info(f"  - {style.name} - {style.description}")

    logger.info(f"\n总计: {len(styles)} 个风格")
    logger.info("\n使用方法: python main.py --rewrite <URL> --style <风格名>")


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
        command = sys.argv[1]

        if command == "--list-styles":
            # 列出所有可用风格
            await list_styles()

        elif command == "--rewrite" or command == "-r":
            # 改写模式
            url = None
            style_name = None
            publish = False

            # 解析参数
            i = 2
            while i < len(sys.argv):
                if sys.argv[i] == "--style" and i + 1 < len(sys.argv):
                    style_name = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--publish":
                    publish = True
                    i += 1
                elif url is None:
                    url = sys.argv[i]
                    i += 1
                else:
                    i += 1

            if url:
                logger.info(f"改写模式: 抓取并改写 -> {url}")
                if style_name:
                    logger.info(f"使用风格: {style_name}")
                if publish:
                    logger.info("将发布到微信草稿箱")
                await test_article_rewrite(url, style_name, publish)
            else:
                logger.error("错误: 改写模式需要提供URL")
                logger.info("用法: python main.py --rewrite <URL> [--style <风格名>] [--publish]")

        elif command == "--fetch" or command == "-f":
            # 抓取模式
            if len(sys.argv) > 2:
                url = sys.argv[2]
                logger.info(f"抓取模式: 抓取URL -> {url}")
                await test_article_fetch(url)
            else:
                logger.error("错误: 抓取模式需要提供URL")
                logger.info("用法: python main.py --fetch <URL>")
        else:
            # 默认抓取模式（向后兼容）
            url = command
            logger.info(f"抓取模式: 抓取URL -> {url}")
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
