import json

with open('tests/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== Data JSON Analysis ===')
print()
print('Players count:', len(data.get('players', [])))
print()
for i, p in enumerate(data.get('players', [])):
    print(f'Player {i}:')
    print(f'  name={p.get("name")}')
    print(f'  account={p.get("account")}')
    print(f'  profession={p.get("profession")}')
    print(f'  group={p.get("group")}')
    print(f'  hasCommanderTag={p.get("hasCommanderTag")}')
    print()

print('=== First Player Complete Data ===')
if data.get('players'):
    first_player = data['players'][0]
    print('Keys:', list(first_player.keys()))
    print()
    print('Full player data (truncated for large fields):')
    for k, v in first_player.items():
        if isinstance(v, (list, dict)):
            print(f'  {k}: <{type(v).__name__} (length={len(v)})>')
        else:
            print(f'  {k}: {v}')

print()
print('=== Checking for "帅妹妹丶.8297/帅姐姐" and "Doubface.5319/我直接加钟" ===')
target_accounts = ["帅妹妹丶.8297", "Doubface.5319"]
target_names = ["帅姐姐", "我直接加钟"]
for p in data.get('players', []):
    if p.get('account') in target_accounts or p.get('name') in target_names:
        print(f'Found matching player:')
        print(f'  name={p.get("name")}')
        print(f'  account={p.get("account")}')
        print()

print('=== Checking for PIN fields ===')
if data.get('players'):
    first_player = data['players'][0]
    print('Looking for PIN-related keys in first player:')
    for k in first_player.keys():
        if 'pin' in k.lower():
            print(f'  Found: {k}')
