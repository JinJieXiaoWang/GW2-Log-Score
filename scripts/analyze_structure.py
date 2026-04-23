import json

def analyze_json_structure():
    print("=" * 80)
    print("JSON 文件结构分析工具")
    print("=" * 80)

    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        print("\n✓ JSON 文件加载成功\n")

        # 1. 顶级字段
        print("【1】顶级字段列表:")
        for key in data.keys():
            value = data[key]
            if isinstance(value, list):
                print(f"  - {key}: list (长度: {len(value)})")
            elif isinstance(value, dict):
                print(f"  - {key}: dict (键数: {len(value)})")
            else:
                print(f"  - {key}: {type(value).__name__} = {value}")

        # 2. 玩家数据结构分析
        if 'players' in data and len(data['players']) > 0:
            print(f"\n【2】玩家数据分析 (共 {len(data['players'])} 个玩家)")
            first_player = data['players'][0]

            print(f"\n第一个玩家的字段:")
            for key in first_player.keys():
                value = first_player[key]
                if isinstance(value, list):
                    if len(value) > 0:
                        print(f"  - {key}: list (长度: {len(value)}, 首元素类型: {type(value[0]).__name__})")
                        if isinstance(value[0], dict):
                            print(f"      字典键: {list(value[0].keys())[:10]}")  # 只显示前10个键
                    else:
                        print(f"  - {key}: list (空)")
                elif isinstance(value, dict):
                    print(f"  - {key}: dict (键数: {len(value)})")
                else:
                    print(f"  - {key}: {type(value).__name__} = {value}")

            # 检查关键字段是否存在
            print(f"\n关键字段检查:")
            critical_fields = ['name', 'account', 'profession', 'dpsAll', 'dpsTargets',
                             'support', 'defenses', 'buffUptimes', 'statsAll']
            for field in critical_fields:
                exists = field in first_player
                if exists:
                    print(f"  ✓ {field}: 存在")
                else:
                    print(f"  ✗ {field}: 缺失")

        # 3. 模式识别信息
        print(f"\n【3】战斗模式识别信息:")
        mode_fields = ['detailedWvW', 'isWvW', 'isPvP', 'isRaid', 'isStrike', 'isFractal']
        for field in mode_fields:
            if field in data:
                print(f"  - {field}: {data[field]}")
            else:
                print(f"  - {field}: 不存在")

        print(f"\n  fightName: {data.get('fightName', 'N/A')}")
        print(f"  recordedBy: {data.get('recordedBy', 'N/A')}")

        print("\n" + "=" * 80)
        print("分析完成")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_json_structure()