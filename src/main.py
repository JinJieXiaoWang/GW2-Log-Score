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
    def __init__(self, db_path="databases/gw2_logs.db"):
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


def main():
    parser = argparse.ArgumentParser(description="激战2日志解析与出勤评分系统")
    parser.add_argument("--dir", help="指定待解析日志所在的文件夹路径")
    parser.add_argument("--file", help="指定单个待解析日志文件路径")
    parser.add_argument("--export", help="导出全量历史评分报表 (CSV路径)")
    parser.add_argument("--db", default="databases/gw2_logs.db", help="指定数据库文件路径")
    parser.add_argument("--serve", action="store_true", help="启动FastAPI服务器")
    parser.add_argument("--host", default=HOST, help="服务器主机地址")
    parser.add_argument("--port", default=PORT, type=int, help="服务器端口")

    args = parser.parse_args()

    if args.serve:
        logger.info(f"Starting server on {args.host}:{args.port}")
        uvicorn.run("src.core.application:app", host=args.host, port=args.port)
    else:
        app = App(args.db)

        if args.file:
            app.process_file(args.file)
        elif args.dir:
            app.process_folder(args.dir)
        elif args.export:
            app.export_report(args.export)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
