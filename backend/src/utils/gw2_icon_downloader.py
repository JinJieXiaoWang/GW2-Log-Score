# -*- coding: utf-8 -*-
"""Guild Wars 2 BUFF 图标下载库

这个模块可以从 GW2 API 拉取 buff metadata，并下载对应的 icon PNG 文件到本地目录。
"""

import argparse
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

GW2_API_BASE = "https://api.guildwars2.com/v2"
BUFFS_ENDPOINT = "buffs"


class GW2BuffIconDownloader:
    @staticmethod
    def _build_url(path: str, query: Optional[Dict[str, str]] = None) -> str:
        base = f"{GW2_API_BASE}/{path.strip('/')}"
        if not query:
            return base
        return f"{base}?{urllib.parse.urlencode(query)}"

    @classmethod
    def fetch_buff_metadata(cls, buff_ids: Iterable[int]) -> List[Dict[str, Any]]:
        ids = [str(i) for i in buff_ids if i is not None]
        if not ids:
            return []
        url = cls._build_url(BUFFS_ENDPOINT, {"ids": ",".join(ids), "v": "latest"})
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "GW2-Log-Score Buff Icon Downloader"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status != 200:
                    raise RuntimeError(f"GW2 API 返回状态码 {response.status}: {url}")
                return json.load(response)
        except urllib.error.HTTPError as err:
            raise RuntimeError(f"GW2 API 请求失败: {err.code} {err.reason}") from err
        except urllib.error.URLError as err:
            raise RuntimeError(f"网络请求失败: {err}") from err

    @staticmethod
    def normalize_name(name: str) -> str:
        safe = re.sub(r"[\\/:*?\"<>|]+", "", name)
        safe = safe.strip().replace(" ", "_").replace("'", "")
        return re.sub(r"_+", "_", safe)[:100].strip("_")

    @staticmethod
    def download_icon(icon_url: str, output_path: Path, force: bool = False) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists() and not force:
            return output_path
        request = urllib.request.Request(
            icon_url,
            headers={"User-Agent": "GW2-Log-Score Buff Icon Downloader"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status != 200:
                    raise RuntimeError(f"图标下载失败: {response.status} {icon_url}")
                content = response.read()
                output_path.write_bytes(content)
                return output_path
        except urllib.error.HTTPError as err:
            raise RuntimeError(f"图标下载失败: {err.code} {err.reason}") from err
        except urllib.error.URLError as err:
            raise RuntimeError(f"图标下载失败: {err}") from err

    @classmethod
    def download_buff_icons(
        cls,
        buff_ids: Iterable[int],
        output_dir: str = "resources/icons/buffs",
        force: bool = False,
    ) -> Dict[int, Path]:
        metadata = cls.fetch_buff_metadata(buff_ids)
        output_root = Path(output_dir)
        result: Dict[int, Path] = {}
        for item in metadata:
            buff_id = item.get("id")
            if buff_id is None:
                continue
            name = item.get("name", str(buff_id))
            icon_url = item.get("icon") or item.get("icon_url")
            if not icon_url:
                continue
            filename = f"{buff_id}_{cls.normalize_name(name)}.png"
            output_path = output_root / filename
            cls.download_icon(icon_url, output_path, force=force)
            result[buff_id] = output_path
        return result

    @classmethod
    def build_buff_mapping(
        cls,
        buff_ids: Iterable[int],
        mapping_path: str = "resources/icons/buffs/buff_mapping.json",
        output_dir: str = "resources/icons/buffs",
        force: bool = False,
    ) -> Dict[str, Dict[str, Any]]:
        output_root = Path(output_dir)
        output_root.mkdir(parents=True, exist_ok=True)
        metadata = cls.fetch_buff_metadata(buff_ids)
        mapping: Dict[str, Dict[str, Any]] = {}
        for item in metadata:
            buff_id = item.get("id")
            if buff_id is None:
                continue
            name = item.get("name", str(buff_id))
            icon_url = item.get("icon") or item.get("icon_url")
            if not icon_url:
                continue
            filename = f"{buff_id}_{cls.normalize_name(name)}.png"
            icon_path = str(output_root / filename)
            cls.download_icon(icon_url, output_root / filename, force=force)
            mapping[str(buff_id)] = {
                "name": name,
                "icon_path": icon_path.replace("\\", "/"),
                "icon_url": icon_url,
            }
        Path(mapping_path).write_text(
            json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return mapping


def main() -> None:
    parser = argparse.ArgumentParser(
        description="下载 Guild Wars 2 BUFF 图标并生成映射文件"
    )
    parser.add_argument(
        "--buff-ids",
        nargs="+",
        type=int,
        help="要下载的 BUFF ID 列表，例: --buff-ids 35676 37233",
    )
    parser.add_argument(
        "--ids-file",
        type=str,
        help="从文本文件读取 BUFF ID，每行一个 ID",
    )
    parser.add_argument(
        "--output-dir",
        default="resources/icons/buffs",
        help="图标保存目录，默认为 resources/icons/buffs",
    )
    parser.add_argument(
        "--mapping-file",
        default="resources/icons/buffs/buff_mapping.json",
        help="生成的映射 JSON 文件路径",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="已存在时强制重新下载图标",
    )
    args = parser.parse_args()

    ids: List[int] = []
    if args.buff_ids:
        ids.extend(args.buff_ids)
    if args.ids_file:
        ids_file = Path(args.ids_file)
        if ids_file.exists():
            for line in ids_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    try:
                        ids.append(int(line))
                    except ValueError:
                        raise ValueError(f"无效 BUFF ID: {line}")
        else:
            raise FileNotFoundError(f"ids file not found: {args.ids_file}")

    if not ids:
        raise ValueError("必须通过 --buff-ids 或 --ids-file 提供至少一个 BUFF ID")

    mapping = GW2BuffIconDownloader.build_buff_mapping(
        ids,
        mapping_path=args.mapping_file,
        output_dir=args.output_dir,
        force=args.force,
    )

    print(f"已下载 {len(mapping)} 个 BUFF 图标 到 {args.output_dir}")
    print(f"映射文件已生成：{args.mapping_file}")


if __name__ == "__main__":
    main()
