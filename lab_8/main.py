import asyncio
import sys
from downloader import AsyncImageDownloader


async def main():
    config_file = "config.json"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    try:
        downloader = AsyncImageDownloader(config_file)
        await downloader.download_all()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
