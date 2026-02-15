import streamlit as st
import random
import uuid
import os
import time

st.set_page_config(page_title="PTCG 終極戰鬥模擬器 v20", layout="wide", page_icon="🃏")

# ==========================================
# 1. 圖片讀取邏輯
# ==========================================
IMAGE_FOLDER = os.path.dirname(os.path.abspath(__file__))

def get_smart_image_path(base_name):
    exts = [".jpg", ".JPG", ".png", ".PNG", ".jpeg", ".JPEG"]
    for ext in exts:
        full_path = os.path.join(IMAGE_FOLDER, f"{base_name}{ext}")
        if os.path.exists(full_path): return full_path
    return None

# ==========================================
# 2. 終極卡牌資料庫 (包含所有細節)
# ==========================================
CARD_DB = {
    "瑪俐的長毛巨魔 ex": {"cat": "Pokemon", "is_basic": False, "stage": "Stage 2", "pre": "瑪俐的詐唬魔", "hp": 320, "type": "Darkness", "weakness": "Grass", "resistance": None, "retreat": 2, "img_base": "grimmsnarl_ex", "moves": [{"n": "不知夜", "cost": {"Darkness": 1}, "d": 0}, {"n": "暗影子彈", "cost": {"Darkness": 3}, "d": 180}]},
    "瑪俐的詐唬魔": {"cat": "Pokemon", "is_basic": False, "stage": "Stage 1", "pre": "瑪俐的搗蛋小妖", "hp": 100, "type": "Darkness", "weakness": "Grass", "resistance": None, "retreat": 1, "img_base": "morgrem", "moves": [{"n": "推擊", "cost": {"Darkness": 1}, "d": 40}]},
    "瑪俐的搗蛋小妖": {"cat": "Pokemon", "is_basic": True, "stage": "Basic", "hp": 70, "type": "Darkness", "weakness": "Grass", "resistance": None, "retreat": 1, "img_base": "impidimp", "moves": [{"n": "偷盜", "cost": {"Darkness": 1}, "d": 0}]},
    "願增猿": {"cat": "Pokemon", "is_basic": True, "stage": "Basic", "hp": 110, "type": "Psychic", "weakness": "Darkness", "resistance": "Fighting", "retreat": 1, "img_base": "munkidori", "ability": "腎上腺素腦", "moves": [{"n": "精神歪曲", "cost": {"Psychic": 1, "Colorless": 1}, "d": 60}]},
    "月月熊 赫月 ex": {"cat": "Pokemon", "is_basic": True, "stage": "Basic", "hp": 260, "type": "Colorless", "weakness": "Fighting", "resistance": None, "retreat": 3, "img_base": "bloodmoon_ursaluna", "ability": "老練技藝", "moves": [{"n": "血月", "cost": {"Colorless": 5}, "d": 240}]},
    "雪童子": {"cat": "Pokemon", "is_basic": True, "stage": "Basic", "hp": 60, "type": "Water", "weakness": "Metal", "resistance": None, "retreat": 1, "img_base": "snorunt", "moves": [{"n": "寒意", "cost": {"Water": 1}, "d": 10}]},
    "雪妖女": {"cat": "Pokemon", "is_basic": False, "stage": "Stage 1", "pre": "雪童子", "hp": 90, "type": "Water", "weakness": "Metal", "resistance": None, "retreat": 1, "img_base": "froslass", "ability": "凍結幕簾", "moves": [{"n": "冰霜粉碎", "cost": {"Water": 1, "Colorless": 1}, "d": 60}]},
    
    "好友寶芬": {"cat": "Trainer", "sub": "Item", "img_base": "buddy_poffin", "logic": "search_basic_hp70"},
    "神奇糖果": {"cat": "Trainer", "sub": "Item", "img_base": "rare_candy", "logic": "skip_evolve"},
    "高級球": {"cat": "Trainer", "sub": "Item", "img_base": "ultra_ball", "logic": "search_any"},
    "老大的指令": {"cat": "Trainer", "sub": "Supporter", "img_base": "boss_orders", "logic": "force_switch"},
    "莉莉艾的決意": {"cat": "Trainer", "sub": "Supporter", "img_base": "lillie_resolve", "logic": "draw_to_6"},
    
    "基本惡能量": {"cat": "Energy", "type": "Darkness", "img_base": "dark_energy"},
    "基本水能量": {"cat": "Energy", "type": "Water", "img_base": "water_energy"}
}

ALL_DECKS = {
    "惡系瑪俐牌組": ["瑪俐的長毛巨魔 ex"]*3 + ["瑪俐的詐唬魔"]*2 + ["瑪俐的搗蛋小妖"]*4 + ["願增猿"]*2 + ["好友寶芬"]*4 + ["神奇糖果"]*3 + ["莉莉艾的決意"]*4 + ["基本惡能量"]*12 + ["老大的指令"]*2,
    "水系控制牌組": ["雪妖女"]*4 + ["雪童子"]*4 + ["月月熊 赫月 ex"]*2 + ["莉莉艾的決意"]*4 + ["基本水能量"]*12 + ["高級球"]*4
}

# ==========================================
# 3. 遊戲核心邏輯
# ==========================================

if 'phase' not in st.session_state:
    st.session_state.phase = 'lobby'
    st.session_state.game = None
    st.session_state.log = []

def log_msg(msg):
    st.session_state.log.append(f"[{time.strftime('%H:%M')}] {msg}")

def create_card(name):
    base = CARD_DB.get(name)
    if not base: return None
    c = base.copy()
    c['id'] = str(uuid.uuid4())[:8]
    c['name'] = name
    if c['cat'] == 'Pokemon':
        c['damage'] = 0
        c['attached'] = []
    return c

def init_game(p_deck_name, o_deck_name, player_first):
    p_deck = [create_card(n) for n in ALL_DECKS[p_deck_name]]
    random.shuffle(p_deck)
    o_deck = [create_card(n) for n in ALL_DECKS[o_deck_name]]
    random.shuffle(o_deck)

    st.session_state.game = {
        "turn": 1, "supporter_used": False, "energy_attached": False,
        "player": {"deck": p_deck[13:], "hand": p_deck[:7], "prizes": p_deck[7:13], "active": None, "bench": [], "discard": []},
        "opponent": {"deck": o_deck[13:], "hand": o_deck[:7], "prizes": o_deck[7:13], "active": o_deck.pop(0), "bench": [], "discard": []}
    }
    
    if not player_first:
        log_msg("🔴 對手先攻。")
        # 簡單模擬對手動作
        op = st.session_state.game['opponent']
        if op['active']: op['active']['attached'].append(create_card("基本水能量"))
    else:
        log_msg("🟢 你獲得先攻！")
    
    st.session_state.phase = 'battle'

# --- 計算邏輯 ---
def calculate_attack_cost(card, move):
    """計算實際能量消耗（考慮特性：月月熊）"""
    cost = move['cost'].copy()
    if card.get('ability') == "老練技藝":
        prizes_taken = 6 - len(st.session_state.game['player']['prizes'])
        if 'Colorless' in cost:
            cost['Colorless'] = max(0, cost['Colorless'] - prizes_taken)
    return cost

def action_attack(move_idx):
    game = st.session_state.game
    pl, op = game['player'], game['opponent']
    move = pl['active']['moves'][move_idx]
    
    # 判斷弱點與抗性
    final_dmg = move['d']
    if op['active']['weakness'] == pl['active']['type']:
        final_dmg *= 2
        log_msg("⚠️ 弱點觸發！傷害加倍")
    if op['active']['resistance'] == pl['active']['type']:
        final_dmg = max(0, final_dmg - 30)
        log_msg("🛡️ 抗性觸發！傷害減少 30")

    op['active']['damage'] += final_dmg
    log_msg(f"💥 {pl['active']['name']} 使用 {move['n']} 造成 {final_dmg} 傷害")
    
    if op['active']['damage'] >= op['active']['hp']:
        log_msg(f"💀 對手 {op['active']['name']} 氣絕！")
        op['active'] = None
        if pl['prizes']: pl['hand'].append(pl['prizes'].pop(0))
    st.rerun()

# ==========================================
# 4. 介面渲染
# ==========================================

def render_card(card, size=110, is_active=False):
    if not card: return
    path = get_smart_image_path(card['img_base'])
    if path: st.image(path, width=size)
    else: st.code(f"[{card['name']}]")
    
    if is_active and card['cat'] == 'Pokemon':
        hp_rem = card['hp'] - card['damage']
        st.caption(f"❤️ {hp_rem}/{card['hp']}")
        st.caption(f"🔋 能量: {len(card['attached'])}")

# ==========================================
# 5. 主程序邏輯
# ==========================================

if st.session_state.phase == 'lobby':
    st.title("PTCG 終極模擬器 v20")
    col1, col2 = st.columns(2)
    p_deck = col1.selectbox("你的牌組", list(ALL_DECKS.keys()))
    o_deck = col2.selectbox("對手牌組", list(ALL_DECKS.keys()))
    
    if st.button("🪙 擲硬幣開始"):
        player_first = random.choice([True, False])
        init_game(p_deck, o_deck, player_first)
        st.rerun()

elif st.session_state.phase == 'battle':
    game = st.session_state.game
    pl, op = game['player'], game['opponent']

    with st.sidebar:
        st.header(f"Turn {game['turn']}")
        if st.button("🔚 結束回合"):
            game['turn'] += 1
            game['supporter_used'] = False
            game['energy_attached'] = False
            if pl['deck']: pl['hand'].append(pl['deck'].pop(0))
            st.rerun()
        st.divider()
        for log in reversed(st.session_state.log[-8:]): st.caption(log)
        if st.button("🏠 返回主選單"): st.session_state.phase = 'lobby'; st.rerun()

    # 對手場地
    c1, c2 = st.columns([1, 4])
    with c1: 
        st.write("😈 對手前台")
        render_card(op['active'], 140, True)
    with c2:
        st.write(f"對手備戰 | 獎賞: {len(op['prizes'])}")
        cols = st.columns(5)
        for i, b in enumerate(op['bench']):
            with cols[i]: render_card(b, 80)

    st.divider()

    # 玩家場地
    c1, c2 = st.columns([4, 1])
    with c1:
        st.write("🛡️ 你的備戰")
        cols = st.columns(5)
        for i, b in enumerate(pl['bench']):
            with cols[i]:
                render_card(b, 90, True)
                if st.button("替換", key=f"sw_{i}"):
                    pl['active'], pl['bench'][i] = pl['bench'][i], pl['active']
                    st.rerun()
    with c2:
        st.write("👤 你的前台")
        if pl['active']:
            render_card(pl['active'], 150, True)
            # 撤退邏輯 (願增猿檢查)
            ret_cost = pl['active']['retreat']
            if pl['active'].get('ability') == "腎上腺素腦":
                if any(e['type'] == 'Darkness' for e in pl['active']['attached']): ret_cost = 0
            
            if st.button(f"🚶 撤退 (需 {ret_cost})"):
                if len(pl['active']['attached']) >= ret_cost:
                    pl['bench'].append(pl['active'])
                    pl['active'] = None
                    st.rerun()
            
            # 攻擊按鈕
            for i, m in enumerate(pl['active']['moves']):
                cost = calculate_attack_cost(pl['active'], m)
                if st.button(f"💥 {m['n']} ({m['d']})", help=f"消耗: {cost}"):
                    action_attack(i)
        else:
            st.warning("請派怪！")

    # 手牌區
    st.divider()
    st.subheader(f"✋ 手牌 ({len(pl['hand'])})")
    h_cols = st.columns(8)
    for i, card in enumerate(pl['hand']):
        with h_cols[i % 8]:
            render_card(card, 90)
            if card['cat'] == 'Pokemon':
                if card['is_basic']:
                    if st.button("登場", key=f"play_{i}"):
                        if not pl['active']: pl['active'] = pl['hand'].pop(i)
                        elif len(pl['bench']) < 5: pl['bench'].append(pl['hand'].pop(i))
                        st.rerun()
                else:
                    if st.button("進化", key=f"evo_{i}"):
                        if pl['active'] and pl['active']['name'] == card.get('pre'):
                            card['attached'] = pl['active']['attached']
                            card['damage'] = pl['active']['damage']
                            pl['active'] = pl['hand'].pop(i)
                            st.rerun()

            elif card['cat'] == 'Energy':
                if not game['energy_attached']:
                    if st.button("附著", key=f"en_{i}"):
                        if pl['active']: 
                            pl['active']['attached'].append(pl['hand'].pop(i))
                            game['energy_attached'] = True
                            st.rerun()
            
            elif card['cat'] == 'Trainer':
                if st.button("✨ 使用", key=f"tr_{i}"):
                    if card['logic'] == 'draw_to_6':
                        while len(pl['hand']) < 7 and pl['deck']: pl['hand'].append(pl['deck'].pop(0))
                    elif card['logic'] == 'force_switch' and op['bench']:
                        op['active'], op['bench'][0] = op['bench'][0], op['active']
                    log_msg(f"使用了 {card['name']}")
                    pl['discard'].append(pl['hand'].pop(i))
                    st.rerun()