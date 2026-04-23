import os
import sys
import time
import json
from scripts.wvw_evtc_parser import ZevtcParser, process_file, detect_play_style, score_players, load_weights

# 测试文件路径
TEST_FILE = r'd:\Code\GW2-Log-Score\tests\20260421-215642.zevtc'
DB_PATH = 'test_wvw_logs.db'

print("=" * 80)
print("ZEVTC 解析器全面测试")
print("=" * 80)

# 测试 1: 文件读取和格式识别
print("\n1. 测试文件读取和格式识别")
print("-" * 50)
try:
    parser = ZevtcParser(TEST_FILE)
    start_time = time.time()
    meta, agents, players = parser.parse()
    parse_time = time.time() - start_time
    print("OK: 成功读取并识别文件格式")
    print("  文件名: {}".format(os.path.basename(TEST_FILE)))
    print("  文件大小: {:.2f} KB".format(os.path.getsize(TEST_FILE) / 1024))
    print("  解析时间: {:.3f} 秒".format(parse_time))
    print("  战斗时间: {:.1f} 秒".format(meta.duration_s))
    print("  地图: {} (ID: {})".format(meta.map_name, meta.map_id))
    print("  玩家数量: {}".format(len(players)))
    print("  是WvW地图: {}".format("是" if meta.is_wvw else "否"))
except Exception as e:
    print("ERROR: 解析失败: {}".format(e))
    sys.exit(1)

# 测试 2: 数据完整性检查
print("\n2. 测试数据完整性")
print("-" * 50)
try:
    # 检查核心数据结构
    print("OK: 战斗元数据: {}, 版本: {}".format(meta.build_date, meta.revision))
    print("OK: 玩家数据: {} 名玩家".format(len(players)))
    print("OK: 代理数据: {} 个代理".format(len(agents)))
    
    # 检查玩家数据字段
    if players:
        player = players[0]
        print("OK: 玩家数据字段完整: 名称={}, 账号={}, 职业={}".format(player.name, player.account, player.profession))
        print("  伤害数据: 总伤害={}, 物理伤害={}, 条件伤害={}".format(player.total_damage, player.power_damage, player.condi_damage))
        print("  生存数据: 倒地={}, 死亡={}".format(player.own_downs, player.own_deaths))
        print("  辅助数据: 撕BUFF={}, 清条件={}".format(player.boon_strips, player.condi_cleanses))
        print("  BUFF覆盖率: {} 个BUFF".format(len(player.buff_uptime)))
    
    # 检查战斗信息
    print("OK: 战斗时长: {:.1f} 秒".format(meta.duration_s))
    print("OK: 开始时间: {}".format(meta.start_datetime))
    print("OK: 玩法类型: {}".format(detect_play_style(len(players), meta)))
except Exception as e:
    print("ERROR: 数据完整性检查失败: {}".format(e))

# 测试 3: 评分功能
print("\n3. 测试评分功能")
print("-" * 50)
try:
    play_style = detect_play_style(len(players), meta)
    weights = load_weights()
    scores = score_players(players, play_style, weights)
    
    print("OK: 评分计算成功: {} 个评分".format(len(scores)))
    if scores:
        top_player = scores[0]
        print("OK: 最高分玩家: {} ({})".format(top_player['name'], top_player['profession']))
        print("  总分: {:.2f}".format(top_player['total_score']))
        print("  角色: {}".format(top_player['role']))
        print("  详细评分: {}".format(json.dumps(top_player['score_details'], ensure_ascii=False)))
except Exception as e:
    print("ERROR: 评分功能测试失败: {}".format(e))

# 测试 4: 完整处理流程
print("\n4. 测试完整处理流程")
print("-" * 50)
try:
    start_time = time.time()
    result = process_file(TEST_FILE, DB_PATH, None, verbose=True)
    process_time = time.time() - start_time
    print("OK: 完整处理流程成功")
    print("  处理时间: {:.3f} 秒".format(process_time))
except Exception as e:
    print("ERROR: 完整处理流程失败: {}".format(e))

# 测试 5: 异常处理
print("\n5. 测试异常处理")
print("-" * 50)
try:
    # 测试不存在的文件
    non_existent_file = r'd:\Code\GW2-Log-Score\tests\non_existent.zevtc'
    parser = ZevtcParser(non_existent_file)
    parser.parse()
    print("ERROR: 应该抛出文件不存在异常")
except FileNotFoundError as e:
    print("OK: 正确处理文件不存在异常: {}".format(e))
except Exception as e:
    print("ERROR: 异常类型不正确: {}".format(e))

# 测试 6: 性能测试
print("\n6. 测试解析性能")
print("-" * 50)
try:
    iterations = 3
    total_time = 0
    
    for i in range(iterations):
        start_time = time.time()
        parser = ZevtcParser(TEST_FILE)
        meta, agents, players = parser.parse()
        iteration_time = time.time() - start_time
        total_time += iteration_time
        print("  第 {} 次: {:.3f} 秒".format(i+1, iteration_time))
    
    avg_time = total_time / iterations
    file_size = os.path.getsize(TEST_FILE) / (1024 * 1024)  # MB
    throughput = file_size / avg_time
    
    print("OK: 性能测试完成")
    print("  平均解析时间: {:.3f} 秒".format(avg_time))
    print("  文件大小: {:.2f} MB".format(file_size))
    print("  解析速度: {:.2f} MB/s".format(throughput))
except Exception as e:
    print("ERROR: 性能测试失败: {}".format(e))

# 测试 7: 输出验证
print("\n7. 测试输出验证")
print("-" * 50)
try:
    # 验证JSON输出
    json_output = r'd:\Code\GW2-Log-Score\tests\20260421-215642_parsed.json'
    process_file(TEST_FILE, DB_PATH, None, json_output, verbose=False)
    
    if os.path.exists(json_output):
        with open(json_output, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("OK: JSON输出成功: {}".format(json_output))
        print("  输出包含: {}".format(list(data.keys())))
        print("  玩家数量: {}".format(len(data.get('players', []))))
        print("  评分数量: {}".format(len(data.get('scores', []))))
        # 清理测试文件
        os.remove(json_output)
    else:
        print("ERROR: JSON输出文件不存在")
except Exception as e:
    print("ERROR: 输出验证失败: {}".format(e))

# 清理测试数据库
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("\nOK: 清理测试数据库完成")

print("\n" + "=" * 80)
print("测试完成!")
print("=" * 80)
