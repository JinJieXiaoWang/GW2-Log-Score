import csv
import os
import sqlite3

class ReportExporter:
    def __init__(self, db_path="gw2_logs.db"):
        self.db_path = db_path

    def export_all_scores_csv(self, output_path):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 联表查询：战斗信息、玩家评分、玩家基础信息
            cursor.execute('''
                SELECT 
                    cl.date, 
                    cl.encounter_name, 
                    cl.mode, 
                    cs.player_name, 
                    p.profession, 
                    p.role, 
                    cs.score_dps, 
                    cs.score_cc, 
                    cs.score_survival, 
                    cs.score_boon, 
                    cs.total_score,
                    cs.details
                FROM combat_scores cs
                JOIN combat_logs cl ON cs.log_id = cl.log_id
                JOIN players p ON cs.player_name = p.name
                ORDER BY cl.date DESC, cs.total_score DESC
            ''')
            
            rows = cursor.fetchall()
            headers = [
                '日期', '战斗名称', '模式', '玩家名称', '职业', '定位', 
                'DPS得分', 'CC得分', '生存得分', '辅助得分', '总分', '详细数据'
            ]
            
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            
            return output_path

def export_report(db_path, output_path):
    exporter = ReportExporter(db_path)
    return exporter.export_all_scores_csv(output_path)

