import json

def check_defenses_structure():
    print("=" * 80)
    print("检查 defenses 字段结构")
    print("=" * 80)

    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'players' not in data or len(data['players']) == 0:
        print("✗ 没有玩家数据")
        return

    first_player = data['players'][0]

    # 检查 defenses
    if 'defenses' in first_player:
        print("\n✓ defenses 字段存在")
        defenses_list = first_player['defenses']
        print(f"  类型: {type(defenses_list)}")
        print(f"  长度: {len(defenses_list)}")

        if len(defenses_list) > 0:
            defenses_dict = defenses_list[0]
            print(f"\n  defenses[0] 的所有键:")
            for key in sorted(defenses_dict.keys()):
                print(f"    - {key}: {defenses_dict[key]}")

            # 检查是否有 downCount 和 deadCount
            print(f"\n  关键字段检查:")
            print(f"    - downCount: {'存在' if 'downCount' in defenses_dict else '缺失'}")
            print(f"    - deadCount: {'存在' if 'deadCount' in defenses_dict else '缺失'}")
            print(f"    - downedCount: {'存在' if 'downedCount' in defenses_dict else '缺失'}")
            print(f"    - deathCount: {'存在' if 'deathCount' in defenses_dict else '缺失'}")
    else:
        print("\n✗ defenses 字段不存在")

    # 检查 dpsAll
    if 'dpsAll' in first_player:
        print("\n✓ dpsAll 字段存在")
        dps_all_list = first_player['dpsAll']
        print(f"  类型: {type(dps_all_list)}")
        print(f"  长度: {len(dps_all_list)}")

        if len(dps_all_list) > 0:
            dps_all_dict = dps_all_list[0]
            print(f"\n  dpsAll[0] 的所有键:")
            for key in sorted(dps_all_dict.keys()):
                print(f"    - {key}: {dps_all_dict[key]}")

    # 检查 support
    if 'support' in first_player:
        print("\n✓ support 字段存在")
        support_list = first_player['support']
        print(f"  类型: {type(support_list)}")
        print(f"  长度: {len(support_list)}")

        if len(support_list) > 0:
            support_dict = support_list[0]
            print(f"\n  support[0] 的所有键:")
            for key in sorted(support_dict.keys()):
                print(f"    - {key}: {support_dict[key]}")

if __name__ == "__main__":
    check_defenses_structure()