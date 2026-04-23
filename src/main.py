import argparse
import glob
import os
import sys
import uvicorn
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.logger import Logger
from src.parser.gw2_log_parser import GW2LogParser
from src.database.db_manager import DBManager
from src.scoring.scoring_engine import ScoringEngine
from src.reports.exporter import ReportExporter
from src.config import HOST, PORT

logger = Logger(__name__)


class App:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "databases", "gw2_logs.db"
            )
        self.db = DBManager(db_path)
        self.parser = GW2LogParser()
        self.scorer = ScoringEngine()
        self.exporter = ReportExporter(db_path)

    def process_folder(self, folder_path):
        json_files = glob.glob(os.path.join(folder_path, "*.json"))
        if not json_files:
            logger.warning(f"No JSON logs found in {folder_path}")
            return

        logger.info(f"Found {len(json_files)} logs in {folder_path}. Starting batch process...")
        for file in json_files:
            try:
                self.process_file(file)
            except Exception as e:
                logger.error(f"Error processing {file}: {e}")

    def process_file(self, file_path):
        logger.info(f"Processing: {os.path.basename(file_path)}")

        parsed_data = self.parser.parse_file(file_path)

        self.db.add_combat_log(
            parsed_data['log_id'],
            parsed_data['mode'],
            parsed_data['encounter_name'],
            parsed_data['date'],
            parsed_data['duration'],
            file_path,
            parsed_data['recorded_by']
        )

        scores = self.scorer.calculate_pve_scores(parsed_data)

        for s in scores:
            self.db.add_player(s['player_name'], s['profession'], s['role'])
            self.db.add_combat_score(
                parsed_data['log_id'],
                s['player_name'],
                s['scores'],
                s['total_score'],
                s['details']
            )

        logger.info(f"Successfully processed {parsed_data['encounter_name']} with {len(scores)} players.")

    def export_report(self, output_path=None):
        if not output_path:
            output_path = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            path = self.exporter.export_all_scores_csv(output_path)
            logger.info(f"Report exported to: {path}")
        except Exception as e:
            logger.error(f"Failed to export report: {e}")


def validate_path(path, path_type="file"):
    """验证文件或目录路径是否存在"""
    if not os.path.exists(path):
        return False, f"指定的{path_type}路径不存在: {path}"
    if path_type == "file" and not os.path.isfile(path):
        return False, f"指定的路径不是有效文件: {path}"
    if path_type == "dir" and not os.path.isdir(path):
        return False, f"指定的路径不是有效目录: {path}"
    return True, None

def main():
    parser = argparse.ArgumentParser(
        description="激战2日志解析与出勤评分系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --serve                          # 启动API服务器
  python main.py --serve --port 8080             # 自定义端口启动服务器
  python main.py --dir ./logs                     # 解析指定目录下的所有日志
  python main.py --file ./logs/boss.json          # 解析单个日志文件
  python main.py --export ./report.csv             # 导出历史评分报表
  python main.py --db ./custom.db --serve          # 使用自定义数据库启动服务器

如需查看详细帮助信息，请使用: python main.py -h
        """
    )

    parser.add_argument(
        "--dir",
        help="指定待解析日志所在的文件夹路径",
        metavar="FOLDER_PATH"
    )
    parser.add_argument(
        "--file",
        help="指定单个待解析日志文件路径",
        metavar="FILE_PATH"
    )
    parser.add_argument(
        "--export",
        help="导出全量历史评分报表 (CSV路径)",
        metavar="CSV_PATH"
    )
    parser.add_argument(
        "--db",
        help="指定数据库文件路径 (默认: databases/gw2_logs.db)",
        default="databases/gw2_logs.db",
        metavar="DB_PATH"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="启动FastAPI服务器"
    )
    parser.add_argument(
        "--host",
        default=HOST,
        help=f"服务器主机地址 (默认: {HOST})",
        metavar="HOST"
    )
    parser.add_argument(
        "--port",
        default=PORT,
        type=int,
        help=f"服务器端口 (默认: {PORT})",
        metavar="PORT"
    )

    args = parser.parse_args()

    if args.port:
        if args.port < 1 or args.port > 65535:
            print(f"错误: 端口号必须介于 1 到 65535 之间，当前值: {args.port}")
            sys.exit(1)

    db_dir = os.path.dirname(args.db)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"已创建数据库目录: {db_dir}")
        except Exception as e:
            print(f"错误: 无法创建数据库目录 {db_dir}: {e}")
            sys.exit(1)

    if args.serve:
        logger.info(f"Starting server on {args.host}:{args.port}")
        uvicorn.run("src.core.application:app", host=args.host, port=args.port)
    else:
        app = App(args.db)

        if args.file:
            is_valid, error_msg = validate_path(args.file, "file")
            if not is_valid:
                print(f"错误: {error_msg}")
                sys.exit(1)
            app.process_file(args.file)
        elif args.dir:
            is_valid, error_msg = validate_path(args.dir, "dir")
            if not is_valid:
                print(f"错误: {error_msg}")
                sys.exit(1)
            app.process_folder(args.dir)
        elif args.export:
            app.export_report(args.export)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
