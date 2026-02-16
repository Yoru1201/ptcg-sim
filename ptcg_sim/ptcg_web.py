import streamlit as st
import random
import uuid
import os
import time

st.set_page_config(page_title="瑪俐的長毛巨魔 ex-1 牌組模擬", layout="wide", page_icon="😈")

# ==========================================
# 1. 圖片路徑處理
# ==========================================
IMAGE_FOLDER = os.path.dirname(os.path.abspath(__file__))
def get_smart_image_path(base_name):
    # 這裡可以根據您的圖檔命名習慣自行擴充
    exts = [".jpg", ".png", ".jpeg"]
    for ext in exts:
        full_path = os.path.join(IMAGE_FOLDER, f"{base_name}{ext}")
        if os.path.exists(full_path): return full_path
    return None

# ==========================================
# 2. 完整卡牌資料庫 (含所有新卡數據)
# ==========================================
CARD_DB = {
    # --- 核心寶可夢 ---
    "瑪俐的長毛巨魔 ex": {
        "cat": "Pokemon", "is_basic": False, "stage": "Stage 2", "pre": "瑪俐的詐唬魔",
        "hp": 320, "type": "Darkness", "weakness": "Grass", "retreat": 2,
        "img_base": "grimmsnarl_ex", "tags": ["ex", "Marnie"], "prize": 2,
        "ability": {"n": "龐克練肌", "desc": "進化時，從牌庫充5張惡能量(模擬簡化為直接充能)"},
        "moves": [{"n": "暗影子彈", "cost": {"Darkness": 2}, "d": 180, "eff": "bench_30"}]
    },
    "瑪俐的詐唬魔": {
        "cat": "Pokemon", "is_basic": False, "stage": "Stage 1", "pre": "瑪俐的搗蛋小妖",
        "hp": 100, "type": "Darkness", "weakness": "Grass", "retreat": 1,
        "img_base": "morgrem", "tags": ["Marnie"], "prize": 1,
        "moves": [{"n": "推擊", "cost": {"Darkness": 2}, "d": 60}]
    },
    "瑪俐的搗蛋小妖": {
        "cat": "Pokemon", "is_basic": True, "stage": "Basic",
        "hp": 70, "type": "Darkness", "weakness": "Grass", "retreat": 1,
        "img_base": "impidimp", "tags": ["Marnie"], "prize": 1,
        "moves": [
            {"n": "偷盜", "cost": {"Colorless": 1}, "d": 0, "eff": "draw_1"},
            {"n": "推擊", "cost": {"Darkness": 1}, "d": 10}
        ]
    },

    # --- 輔助寶可夢 ---
    "願增猿": {
        "cat": "Pokemon", "is_basic": True, "stage": "Basic", "hp": 110, "type": "Psychic",
        "weakness": "Darkness", "retreat": 1, "img_base": "munkidori", "prize": 1,
        "ability": {"n": "腎上腺素腦", "desc": "附有惡能量時，撤退費用為0"},
        "moves": [{"n": "精神歪曲", "cost": {"Psychic": 1, "Colorless": 1}, "d": 60, "eff": "confusion"}]
    },
    "月月熊 赫月 ex": {
        "cat": "Pokemon", "is_basic": True, "stage": "Basic", "hp": 260, "type": "Colorless",
        "weakness": "Fighting", "retreat": 3, "img_base": "bloodmoon_ursaluna", "tags": ["ex"], "prize": 2,
        "ability": {"n": "老練技藝", "desc": "依對手拿取的獎賞卡數量減少招式所需無色能量"},
        "moves": [{"n": "血月", "cost": {"Colorless": 5}, "d": 240}]
    },
    "含羞苞": {
        "cat": "Pokemon", "is_basic": True, "stage": "Basic", "hp": 30, "type": "Grass",
        "weakness": "Fire", "retreat": 0, "img_base": "budew", "prize": 1,
        "moves": [{"n": "發現寶藏", "cost": {}, "d": 0, "eff": "search_trainer"}] # 0費招式
    },
    "米立龍": {
        "cat": "Pokemon", "is_basic": True, "stage": "Basic", "hp": 70, "type": "Dragon",
        "weakness": None, "retreat": 1, "img_base": "tatsugiri", "prize": 1,
        "ability": {"n": "現場指揮", "desc": "若在戰鬥場，看牌庫上方6張選支援者上手"},
        "moves": [{"n": "衝浪", "cost": {"Fire": 1, "Water": 1}, "d": 50}]
    },
    "雪童子": {
        "cat": "Pokemon", "is_basic": True, "stage": "Basic", "hp": 60, "type": "Water",
        "weakness": "Metal", "retreat": 1, "img_base": "snorunt", "prize": 1,
        "moves": [{"n": "寒意", "cost": {"Water": 1}, "d": 10}]
    },
    "雪妖女": {
        "cat": "Pokemon", "is_basic": False, "stage": "Stage 1", "pre": "雪童子", "hp": 90, "type": "Water",
        "weakness": "Metal", "retreat": 1, "img_base": "froslass", "prize": 1,
        "ability": {"n": "凍結幕簾", "desc": "雙方不能從手牌使用物品卡(模擬器僅提示)"},
        "moves": [{"n": "冰霜粉碎", "cost": {"Water": 1, "Colorless": 1}, "d": 60}]
    },
    "可達鴨": {
        "cat": "Pokemon", "is_basic": True, "stage": "Basic", "hp": 70, "type": "Water",
        "weakness": "Lightning", "retreat": 1, "img_base": "psyduck", "prize": 1,
        "moves": [{"n": "頭錘", "cost": {"Colorless": 1}, "d": 20}]
    },

    # --- 訓練家 (物品) ---
    "寶可平板": {"cat": "Trainer", "sub": "Item", "img_base": "poke_tablet", "logic": "search_pokemon_no_rule", "desc": "找1張非規則寶可夢"},
    "好友寶芬": {"cat": "Trainer", "sub": "Item", "img_base": "buddy_poffin", "logic": "search_basic_hp70", "desc": "找2張HP70以下基礎怪放備戰"},
    "夜間擔架": {"cat": "Trainer", "sub": "Item", "img_base": "night_stretcher", "logic": "recover_one", "desc": "回收1張怪或能量"},
    "神奇糖果": {"cat": "Trainer", "sub": "Item", "img_base": "rare_candy", "logic": "skip_evolve", "desc": "基礎怪直接進化成2階"},
    "能量轉移": {"cat": "Trainer", "sub": "Item", "img_base": "energy_switch", "logic": "move_energy", "desc": "移動場上1個能量"},
    "高級球": {"cat": "Trainer", "sub": "Item", "img_base": "ultra_ball", "logic": "discard_2_search_any", "desc": "棄2張手牌找任意怪"},
    "不公印章": {"cat": "Trainer", "sub": "Item", "tags": ["ACE SPEC"], "img_base": "unfair_stamp", "logic": "unfair_stamp", "desc": "上回合氣絕可用。你抽5對手抽2"},
    
    # --- 訓練家 (道具) ---
    "氣球": {"cat": "Trainer", "sub": "Tool", "img_base": "air_balloon", "logic": "retreat_minus_2", "desc": "撤退費-2"},

    # --- 訓練家 (支援者) ---
    "莉莉艾的決意": {"cat": "Trainer", "sub": "Supporter", "img_base": "lillie_resolve", "logic": "lillie_draw", "desc": "抽牌直到6張(若獎賞剩6張則抽8張)"},
    "老大的指令": {"cat": "Trainer", "sub": "Supporter", "img_base": "boss_orders", "logic": "force_switch", "desc": "強制換對手怪"},
    "火箭隊的拉姆達": {"cat": "Trainer", "sub": "Supporter", "img_base": "rocket_lambda", "logic": "search_trainer", "desc": "找1張訓練家卡"},
    "丹瑜": {"cat": "Trainer", "sub": "Supporter", "img_base": "carmine", "logic": "carmine_draw", "desc": "先攻首回合可用。棄手牌抽5張"},

    # --- 訓練家 (競技場) ---
    "尖釘鎮道館": {"cat": "Trainer", "sub": "Stadium", "img_base": "spikemuth_gym", "logic": "search_marnie", "desc": "每回合找1張瑪俐的寶可夢"},

    # --- 能量 ---
    "基本惡能量": {"cat": "Energy", "type": "Darkness", "img_base": "dark_energy"}
}

# ==========================================
# 3. 牌組構成 (60張)
# ==========================================
DECK_LIST_CONFIG = {
    "瑪俐的長毛巨魔 ex": 2,
    "瑪俐的詐唬魔": 2,
    "瑪俐的搗蛋小妖": 3,
    "願增猿": 4,
    "含羞苞": 1,
    "可達鴨": 1,
    "雪童子": 2,
    "雪妖女": 2,
    "月月熊 赫月 ex": 1,
    "米立龍": 1,
    "寶可平板": 3,
    "好友寶芬": 3,
    "夜間擔架": 3,
    "神奇糖果": 2,
    "能量轉移": 1,
    "高級球": 1,
    "不公印章": 1,
    "氣球": 1,
    "莉莉艾的決意": 4,
    "老大的指令": 3,
    "火箭隊的拉姆達": 4,
    "丹瑜": 3,
    "尖釘鎮道館": 3,
    "基本惡能量": 9
}

# 驗證牌組張數
TOTAL_CARDS = sum(DECK_LIST_CONFIG.values())
# 為了對戰，我們建立一個鏡像牌組給對手
ALL_DECKS = {
    "瑪俐的長毛巨魔ex-1": [],
    "對手測試牌組": []
}

def build_deck_list():
    deck = []
    for name, count in DECK_LIST_CONFIG.items():
        if name in CARD_DB:
            deck.extend([name] * count)
        else:
            print(f"Warning: {name} not found in DB")
    return deck

ALL_DECKS["瑪俐的長毛巨魔ex-1"] = build_deck_list()
ALL_DECKS["對手測試牌組"] = build_deck_list() # 為了方便，對手也用一樣的牌組

# ==========================================
# 4. 遊戲核心邏輯
# ==========================================
if 'phase' not in st.session_state:
    st.session_state.phase = 'lobby'
    st.session_state.game = None
    st.session_state.log = []

def log_msg(msg):
    st.session_state.log.append(f"[{time.strftime('%H:%M')}] {msg}")

def create_card(name):
    base = CARD_DB.get(name)
    if not base: return {"name": name, "cat": "Unknown"}
    c = base.copy()
    c['id'] = str(uuid.uuid4())[:8]
    c['name'] = name
    if c['cat'] == 'Pokemon':
        c['damage'] = 0
        c['attached'] = []
        c['tool'] = [] # 道具槽
        c['status'] = {"poison": False, "burn": False, "sleep": False, "paralysis": False, "confusion": False}
    return c

def check_mulligan(deck):
    """起手無基礎怪重抽"""
    hand = deck[:7]
    has_basic = any(c['cat'] == 'Pokemon' and c['is_basic'] for c in hand)
    return has_basic, hand

def init_game(p_deck_name, o_deck_name, player_first):
    # 玩家
    p_raw = [create_card(n) for n in ALL_DECKS[p_deck_name]]
    random.shuffle(p_raw)
    valid, p_hand = check_mulligan(p_raw)
    while not valid:
        random.shuffle(p_raw)
        valid, p_hand = check_mulligan(p_raw)
    
    # 對手
    o_raw = [create_card(n) for n in ALL_DECKS[o_deck_name]]
    random.shuffle(o_raw)
    valid_o, o_hand = check_mulligan(o_raw)
    while not valid_o: # 對手也要有基礎怪
        random.shuffle(o_raw)
        valid_o, o_hand = check_mulligan(o_raw)

    st.session_state.game = {
        "turn": 1, "is_player_turn": player_first, "supporter_used": False, "energy_attached": False, "first_player": "player" if player_first else "opponent",
        "ko_last_turn": False,
        "player": {"deck": p_raw[13:], "hand": p_raw[:7], "prizes": p_raw[7:13], "active": None, "bench": [], "discard": []},
        "opponent": {"deck": o_raw[13:], "hand": o_raw[:7], "prizes": o_raw[7:13], "active": o_raw.pop(0), "bench": [], "discard": []}
    }
    
    # 若後攻，模擬對手第一回合結束
    if not player_first:
        st.session_state.game['turn'] = 1
        st.session_state.game['is_player_turn'] = True
        log_msg("對手已結束第一回合 (後攻)")
    else:
        log_msg("你獲得先攻")

    st.session_state.phase = 'battle'

# --- 招式與能力 ---
def calculate_attack_cost(card, move):
    """計算招式能量 (含月月熊邏輯)"""
    cost = move['cost'].copy()
    
    # 月月熊 赫月 ex 特性：依對手拿取獎賞卡數減少無色能量
    if card.get('ability', {}).get('n') == "老練技藝":
        op_prizes_taken = 6 - len(st.session_state.game['opponent']['prizes'])
        if 'Colorless' in cost:
            cost['Colorless'] = max(0, cost['Colorless'] - op_prizes_taken)
            
    return cost

def action_attack(move_idx):
    game = st.session_state.game
    pl = game['player']
    op = game['opponent']
    active = pl['active']
    move = active['moves'][move_idx]
    
    # 檢查先攻首回合
    if game['turn'] == 1 and game['first_player'] == 'player':
        st.toast("🚫 先攻第一回合不能攻擊")
        return

    # 計算傷害
    dmg = move['d']
    if op['active']['weakness'] == active['type']:
        dmg *= 2
        log_msg("⚠️ 弱點！傷害加倍")
        
    op['active']['damage'] += dmg
    log_msg(f"💥 {active['name']} 使用 {move['n']} 造成 {dmg} 傷害")
    
    # 效果處理
    if move.get('eff') == 'bench_30': # 暗影子彈
        if op['bench']:
            target = op['bench'][0] # 簡化：打第一隻
            target['damage'] += 30
            log_msg(f"☄️ 對手備戰的 {target['name']} 受到 30 傷害")
            
    if move.get('eff') == 'draw_1': # 偷盜
        if pl['deck']: pl['hand'].append(pl['deck'].pop(0))
        log_msg("抽了1張卡")

    if move.get('eff') == 'search_trainer': # 含羞苞
        # 簡化：直接給一張寶可平板
        log_msg("發現寶藏！(模擬：加入一張寶可平板到手牌)")
        pl['hand'].append(create_card("寶可平板"))

    # 氣絕檢查
    check_knockout('opponent')
    
    # 回合結束
    game['turn'] += 1
    game['supporter_used'] = False
    game['energy_attached'] = False
    if pl['deck']: pl['hand'].append(pl['deck'].pop(0))
    st.rerun()

def check_knockout(side):
    game = st.session_state.game
    target = game[side]
    attacker = game['player'] if side == 'opponent' else game['opponent']
    
    if target['active'] and target['active']['damage'] >= target['active']['hp']:
        game['ko_last_turn'] = True
        p_take = target['active'].get('prize', 1)
        log_msg(f"💀 {target['active']['name']} 氣絕！拿 {p_take} 張獎賞卡")
        target['discard'].append(target['active'])
        target['active'] = None
        
        for _ in range(p_take):
            if attacker['prizes']: attacker['hand'].append(attacker['prizes'].pop(0))
            
        if not attacker['prizes']:
            st.success("🏆 獲勝！獎賞卡拿完"); st.stop()
        if not target['bench'] and not target['active']:
            st.success("🏆 對手場空，獲勝！"); st.stop()

def action_retreat():
    pl = st.session_state.game['player']
    active = pl['active']
    if not active: return

    cost = active['retreat']
    
    # 道具：氣球
    if any(t['name'] == '氣球' for t in active.get('tool', [])):
        cost = max(0, cost - 2)

    # 特性：願增猿 (若有惡能量則0費)
    if active.get('ability', {}).get('n') == "腎上腺素腦":
        if any(e['type'] == 'Darkness' for e in active['attached']):
            cost = 0
            
    if len(active['attached']) >= cost:
        # 簡單處理：清空能量模擬消耗
        active['attached'] = []
        pl['bench'].append(active)
        pl['active'] = None
        st.rerun()
    else:
        st.toast(f"❌ 撤退需要 {cost} 能量")

def use_trainer(card, index):
    game = st.session_state.game
    pl = game['player']
    
    # 規則檢查
    if card['sub'] == 'Supporter':
        if game['supporter_used']: st.toast("❌ 已使用過支援者"); return
        if game['turn'] == 1 and game['first_player'] == 'player' and card['name'] != "丹瑜":
            st.toast("❌ 先攻T1只能用丹瑜"); return

    logic = card.get('logic')
    
    if logic == 'search_basic_hp70': # 好友寶芬
        cnt = 0
        for _ in range(2):
            if len(pl['bench']) < 5:
                # 模擬：找搗蛋小妖
                pl['bench'].append(create_card("瑪俐的搗蛋小妖"))
                cnt += 1
        log_msg(f"好友寶芬：鋪了 {cnt} 隻小妖")

    elif logic == 'skip_evolve': # 神奇糖果
        st.toast("🍬 請點擊備戰區小妖進行進化")
        return # 不丟棄卡片，等待點擊進化

    elif logic == 'lillie_draw': # 莉莉艾
        # 洗回手牌 (簡化為不洗，直接補到對應張數)
        pl['deck'].extend(pl['hand']) # 把手牌丟回牌庫
        pl['hand'] = [] # 清空
        target = 8 if len(pl['prizes']) == 6 else 6
        for _ in range(target):
            if pl['deck']: pl['hand'].append(pl['deck'].pop(0))
        log_msg(f"莉莉艾：抽滿 {target} 張")

    elif logic == 'unfair_stamp': # 不公印章
        if not game['ko_last_turn']: st.toast("❌ 上回合無氣絕"); return
        pl['hand'] = [pl['deck'].pop(0) for _ in range(5) if pl['deck']]
        game['opponent']['hand'] = [game['opponent']['deck'].pop(0) for _ in range(2) if game['opponent']['deck']]
        log_msg("不公印章：我方抽5，對手抽2")
        
    elif logic == 'retreat_minus_2': # 氣球 (道具)
        if pl['active']:
            pl['active']['tool'].append(card)
            pl['hand'].pop(index) # 裝備後移除
            log_msg("氣球已裝備到戰鬥寶可夢")
            st.rerun()
        return

    # 結尾處理
    if card['sub'] == 'Supporter': game['supporter_used'] = True
    if card in pl['hand']: pl['hand'].remove(card)
    pl['discard'].append(card)
    st.rerun()

# ==========================================
# 5. UI
# ==========================================
def render_card(card, size=110, is_active=False, idx=None, source='hand'):
    if not card: return
    path = get_smart_image_path(card['img_base'])
    st.image(path if path else "https://placehold.co/100x140?text=Card", width=size)
    
    if card['cat'] == 'Pokemon':
        if is_active:
            st.caption(f"❤️ {card['hp'] - card['damage']}/{card['hp']}")
            st.caption(f"⚡ {len(card['attached'])}")
            if card.get('tool'): st.caption(f"🎒 {card['tool'][0]['name']}")
            if card.get('ability'): st.caption(f"🌟 {card['ability']['n']}")

    if source == 'hand':
        if card['cat'] == 'Trainer':
            if st.button("使用", key=f"u_{idx}"): use_trainer(card, idx)
        elif card['cat'] == 'Pokemon' and card['is_basic']:
            if st.button("打出", key=f"p_{idx}"):
                game = st.session_state.game
                if not game['player']['active']: game['player']['active'] = game['player']['hand'].pop(idx)
                elif len(game['player']['bench']) < 5: game['player']['bench'].append(game['player']['hand'].pop(idx))
                st.rerun()
        elif card['cat'] == 'Energy':
            if st.button("貼能", key=f"e_{idx}"):
                game = st.session_state.game
                if not game['energy_attached'] and game['player']['active']:
                    game['player']['active']['attached'].append(game['player']['hand'].pop(idx))
                    game['energy_attached'] = True
                    st.rerun()

# 主程序
if st.session_state.phase == 'lobby':
    st.title("PTCG 模擬器：瑪俐特化牌組 v23")
    st.write(f"目前牌組：瑪俐的長毛巨魔ex-1 (共 {TOTAL_CARDS} 張)")
    
    if st.button("開始對戰 (Start Game)"):
        init_game("瑪俐的長毛巨魔ex-1", "對手測試牌組", True)
        st.rerun()

elif st.session_state.phase == 'battle':
    game = st.session_state.game
    pl, op = game['player'], game['opponent']
    
    with st.sidebar:
        st.header(f"Turn: {game['turn']}")
        if st.button("結束回合"):
            game['turn'] += 1; game['supporter_used']=False; game['energy_attached']=False
            st.rerun()
        st.write("---")
        for l in reversed(st.session_state.log[-8:]): st.caption(l)

    # 場地
    c1, c2 = st.columns([1, 4])
    with c1: st.write("😈 對手"); render_card(op['active'], 120, True)
    with c2: 
        st.write(f"備戰 (獎賞剩 {len(op['prizes'])})")
        cols = st.columns(5)
        for i, b in enumerate(op['bench']): 
            with cols[i]: render_card(b, 80)
            
    st.divider()
    
    c1, c2 = st.columns([4, 1])
    with c1:
        st.write(f"我方備戰 (獎賞剩 {len(pl['prizes'])})")
        cols = st.columns(5)
        for i, b in enumerate(pl['bench']):
            with cols[i]: 
                render_card(b, 80)
                # 進化邏輯 (需手牌有進化型)
                for h_idx, h_card in enumerate(pl['hand']):
                    if h_card.get('pre') == b['name']:
                        if st.button(f"進化成 {h_card['name']}", key=f"evo_{i}"):
                            # 繼承傷害與能量
                            h_card['damage'] = b['damage']
                            h_card['attached'] = b['attached']
                            pl['bench'][i] = pl['hand'].pop(h_idx)
                            # 觸發特性：龐克練肌
                            if h_card['name'] == "瑪俐的長毛巨魔 ex":
                                log_msg("龐克練肌！自動充能惡能量")
                                h_card['attached'].extend([create_card("基本惡能量")]*2)
                            st.rerun()
    with c2:
        st.write("我方戰鬥")
        if pl['active']:
            render_card(pl['active'], 140, True)
            if st.button("🏳️ 撤退"): action_retreat()
            
            for i, m in enumerate(pl['active']['moves']):
                cost = calculate_attack_cost(pl['active'], m)
                if st.button(f"💥 {m['n']} ({m['d']})", help=str(cost)): action_attack(i)
        else: st.warning("請放置戰鬥寶可夢")
        
    st.write(f"手牌 ({len(pl['hand'])})")
    cols = st.columns(10)
    for i, c in enumerate(pl['hand']):
        with cols[i % 10]: render_card(c, 90, idx=i)