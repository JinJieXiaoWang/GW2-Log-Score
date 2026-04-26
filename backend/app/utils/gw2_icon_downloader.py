#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GW2 BUFF 图标下载器
下载 Guild Wars 2 游戏中的 BUFF 图标并生成映射文件
"""

import json
import argparse
import asyncio
import aiohttp
from pathlib import Path


class GW2BuffIconDownloader:
    """
    GW2 BUFF 图标下载器
    """

    API_BASE_URL = "https://api.guildwars2.com/v2"

    @classmethod
    async def fetch_buff_info(
        cls, session: aiohttp.ClientSession, buff_id: int
    ) -> dict:
        """
        从GW2 API 获取 BUFF 信息
        
        Args:
            session: aiohttp 会话
            buff_id: BUFF ID
        
        Returns:
            BUFF 信息字典，失败返回 None
        """
        url = f"{cls.API_BASE_URL}/skills/{buff_id}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "name": data.get("name", f"Buff_{buff_id}"),
                        "icon": data.get("icon", ""),
                    }
                return None
        except Exception as e:
            print(f"获取 BUFF {buff_id} 信息失败: {e}")
            return None

    @classmethod
    async def download_icon(
        cls, url: str, output_path: Path, force: bool = False
    ) -> bool:
        """
        下载图标到指定路径
        
        Args:
            url: 图标 URL
            output_path: 输出路径
            force: 是否强制下载
        
        Returns:
            是否下载成功
        """
        if output_path.exists() and not force:
            print(f"图标已存在，跳过: {output_path}")
            return True

        # 确保目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(output_path, "wb") as f:
                            f.write(content)
                        print(f"下载成功: {output_path}")
                        return True
                    else:
                        print(f"下载失败 {response.status}: {url}")
                        return False
        except Exception as e:
            print(f"下载图标失败: {e}")
            return False

    @classmethod
    async def process_buff(
        cls,
        session: aiohttp.ClientSession,
        buff_id: int,
        output_root: Path,
        mapping: dict,
        force: bool = False,
    ) -> None:
        """
        处理单个 BUFF
        
        Args:
            session: aiohttp 会话
            buff_id: BUFF ID
            output_root: 输出根目录
            mapping: 映射字典
            force: 是否强制下载
        """
        buff_info = await cls.fetch_buff_info(session, buff_id)
        if not buff_info or not buff_info.get("icon"):
            print(f"无法获取 BUFF {buff_id} 的图标信息")
            return

        name = buff_info["name"]
        icon_url = buff_info["icon"]
        filename = f"{buff_id}.png"
        icon_path = output_root / "buffs" / filename

        await cls.download_icon(icon_url, output_root / "buffs" / filename, force=force)
        mapping[str(buff_id)] = {
            "name": name,
            "icon_path": str(icon_path).replace("\\", "/"),
            "icon_url": icon_url,
        }

    @classmethod
    async def download_buff_icons(
        cls, buff_ids: list, output_dir: str, force: bool = False
    ) -> dict:
        """
        批量下载 BUFF 图标
        
        Args:
            buff_ids: BUFF ID 列表
            output_dir: 输出目录
            force: 是否强制下载
        
        Returns:
            图标映射字典
        """
        output_root = Path(output_dir)
        mapping = {}

        async with aiohttp.ClientSession() as session:
            tasks = [
                cls.process_buff(session, buff_id, output_root, mapping, force)
                for buff_id in buff_ids
            ]
            await asyncio.gather(*tasks)

        # 保存映射文件
        mapping_path = output_root.parent / "buff_mapping.json"
        with open(mapping_path, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        return mapping


def load_buff_ids_from_file(file_path: str) -> list:
    """
    从文件加载 BUFF ID 列表
    
    Args:
        file_path: 文件路径
    
    Returns:
        BUFF ID 列表
    """
    buff_ids = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and line.isdigit():
                    buff_ids.append(int(line))
    except Exception as e:
        print(f"读取文件失败: {e}")
    return buff_ids


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(
        description="下载 Guild Wars 2 BUFF 图标并生成映射文件"
    )
    parser.add_argument(
        "--buff-ids",
        nargs="+",
        type=int,
        help="要下载的 BUFF ID 列表，例如 --buff-ids 35676 37233",
    )
    parser.add_argument(
        "--ids-file",
        type=str,
        help="从文本文件读取 BUFF ID，每行一个 ID",
    )
    parser.add_argument(
        "--output-dir",
        default="resources/icons",
        help="图标保存目录，默认 resources/icons",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制重新下载已存在的图标",
    )

    args = parser.parse_args()

    # 收集 BUFF ID
    buff_ids = []
    if args.buff_ids:
        buff_ids.extend(args.buff_ids)
    if args.ids_file:
        buff_ids.extend(load_buff_ids_from_file(args.ids_file))

    if not buff_ids:
        print("错误: 未指定 BUFF ID")
        parser.print_help()
        return

    # 去重
    buff_ids = list(set(buff_ids))
    print(f"准备下载 {len(buff_ids)} 个 BUFF 图标")

    # 执行下载
    mapping = asyncio.run(
        GW2BuffIconDownloader.download_buff_icons(buff_ids, args.output_dir, args.force)
    )

    print(f"\n下载完成，共处理 {len(mapping)} 个 BUFF 图标")
    print(f"映射文件已保存到: {Path(args.output_dir).parent / 'buff_mapping.json'}")


if __name__ == "__main__":
    main()
