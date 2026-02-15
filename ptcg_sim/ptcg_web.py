import streamlit as st
import random
import uuid
import os
import time

st.set_page_config(page_title="PTCG 戰鬥系統 v17 (同層目錄版)", layout="wide", page_icon="⚔️")

# ==========================================
# 1. 圖片路徑設定 (修改為：讀取同一層目錄)
# ==========================================

# 取得 app.py 目前所在的資料夾路徑
IMAGE_FOLDER = os.path.dirname(os.path.abspath(__file__))

def get_smart_image_path(base_name):
    """
    智慧讀圖：
    直接在 app.py 旁邊找檔案，支援 jpg, png, jpeg
    """
    exts = [".jpg", ".JPG", ".png", ".PNG", ".jpeg", ".JPEG"]
    
    for ext in exts:
        # 直接組合成： 資料夾路徑/檔名.副檔名
        full_path = os.path.join(IMAGE_FOLDER, f"{base_name}{ext}")
        if os.path.exists(full_path):
            return full_path
    return None

# ==========================================
# 2. 完整卡片資料庫 (邏輯 + 數值)
# ==========================================
CARD_DB = {
    # --- 寶可夢 ---
    "瑪俐的長毛巨魔 ex": {
        "cat": "Pokemon", "stage": "Stage 2", "hp": 320, "type": "Darkness", "retreat": 2, 
        "weakness": "Grass", "img_base": "grimmsnarl_ex",
        "moves": [{"n": "不知夜", "cost": 1, "d": 0, "eff": "找3張牌"}, {"n": "暗影子彈", "cost": 3, "d": 180, "eff": "備戰受傷60"}]
    },
    "瑪俐的詐唬魔": {
        "cat": "Pokemon", "stage": "Stage 1", "hp": 100, "type": "Darkness", "retreat": 1, 
        "weakness": "Grass", "img_base": "morgrem",
        "moves": [{"n": "推擊", "cost": 1, "d": 40, "eff": ""}]
    },
    "瑪俐的搗蛋小妖": {
        "cat": "Pokemon", "stage": "Basic", "hp": 70, "type": "Darkness", "retreat": 1, 
        "weakness": "Grass", "img_base": "impidimp",
        "moves": [{"n": "偷盜", "cost": 1, "d": 0, "eff": "棄對手1張手牌"}]
    },
    "願增猿": {
        "cat": "Pokemon", "stage": "Basic", "hp": 110, "type": "Psychic", "retreat": 1, 
        "weakness": "Darkness", "resistance": "Fighting", "img_base": "munkidori",
        "ability": {"n": "腎上腺素腦", "desc": "有惡能量則撤退0費"},
        "moves": [{"n": "精神歪曲", "cost": 2, "d": 60, "eff": "混亂"}]
    },
    "雪妖女": {
        "cat": "Pokemon", "stage": "Stage 1", "hp": 90, "type": "Water", "retreat": 1, 
        "weakness": "Metal", "img_base": "froslass",
        "ability": {"n": "凍結幕簾", "desc": "封鎖物品卡"},
        "moves": [{"n": "冰霜粉碎", "cost": 2, "d": 60, "eff": ""}]
    },
    "雪童子": {
        "cat": "Pokemon", "stage": "Basic", "hp": 60, "type": "Water", "retreat": 1, 
        "weakness": "Metal", "img_base": "snorunt",
        "moves": [{"n": "寒意", "cost": 1, "d": 10, "eff": "無法撤退"}]
    },
    "月月熊 赫月 ex": {
        "cat": "Pokemon", "stage": "Basic", "hp": 260, "type": "Colorless", "retreat": 3, 
        "weakness": "Fighting", "img_base": "bloodmoon_ursaluna",
        "ability": {"n": "老練技藝", "desc": "拿獎賞卡減少耗能"},
        "moves": [{"n": "血月", "cost": 5, "d": 240, "eff": "下回合無法攻擊"}]
    },
    "含羞苞": {
        "cat": "Pokemon", "stage": "Basic", "hp": 30, "type": "Grass", "retreat": 0, 
        "weakness": "Fire", "img_base": "budew",
        "moves": [{"n": "發現寶藏", "cost": 0, "d": 0, "eff": "找訓練家卡"}]
    },
    "可達鴨": {
        "cat": "Pokemon", "stage": "Basic", "hp": 70, "type": "Water", "retreat": 1, 
        "weakness": "Lightning", "img_base": "psyduck",
        "moves": [{"n": "過度思考", "cost": 1, "d": 0, "eff": "封鎖訓練家"}]
    },
    "米立龍": {
        "cat": "Pokemon", "stage": "Basic", "hp": 70, "type": "Dragon", "retreat": 1, 
        "img_base": "tatsugiri",
        "moves": [{"n": "衝浪", "cost": 2, "d": 50, "eff": ""}]
    },

    # --- 訓練家 ---
    "寶可平板": {"cat": "Trainer", "sub": "Item", "img_base": "poke_tablet", "logic": "search_prize"},
    "好友寶芬": {"cat": "Trainer", "sub": "Item", "img_base": "buddy_poffin", "logic": "search_deck"},
    "夜間擔架": {"cat": "Trainer", "sub": "Item", "img_base": "night_stretcher", "logic": "recover"},
    "神奇糖果": {"cat": "Trainer", "sub": "Item", "img_base": "rare_candy", "logic": "evolve"},
    "高級球": {"cat": "Trainer", "sub": "Item", "img_base": "ultra_ball", "logic": "search_deck"},
    "能量轉移": {"cat": "Trainer", "sub": "Item", "img_base": "energy_switch", "logic": "move_energy"},
    "不公印章": {"cat": "Trainer", "sub": "Item", "img_base": "unfair_stamp", "logic": "disrupt"},
    "氣球": {"cat": "Trainer", "sub": "Tool", "img_base": "air_balloon", "logic": "tool"},
    
    "莉莉艾的決意": {"cat": "Trainer", "sub": "Supporter", "img_base": "lillie_resolve", "logic": "draw_to_6"},
    "火箭隊的拉姆達": {"cat": "Trainer", "sub": "Supporter", "img_base": "rocket_lambda", "logic": "search_deck"},
    "老大的指令": {"cat": "Trainer", "sub": "Supporter", "img_base": "boss_orders", "logic": "gust"},
    "丹瑜": {"cat": "Trainer", "sub": "Supporter", "img_base": "carmine", "logic": "discard_draw_5"},
    
    "尖釘鎮道館": {"cat": "Trainer", "sub": "Stadium", "img_base": "spikemuth_gym", "logic": "stadium"},

    # --- 能量 ---
    "基本惡能量": {"cat": "Energy", "sub": "Basic", "img_base": "dark_energy"}
}

ALL_DECKS = {
    "惡系強攻牌組": {
        "瑪俐的長毛巨魔 ex": 2, "瑪俐的詐唬魔": 2, "瑪俐的搗蛋小妖": 3, "願增猿": 3,
        "含羞苞": 1, "可達鴨": 1, "雪童子": 1, "雪妖女": 1, "月月熊 赫月 ex": 1,
        "米立龍": 1, "寶可平板": 2, "好友寶芬": 2, "夜間擔架": 2, "神奇糖果": 2,
        "能量轉移": 1, "高級球": 2, "氣球": 1, "莉莉艾的決意": 4,
        "老大的指令": 2, "火箭隊的拉姆達": 2, "丹瑜": 4, "基本惡能量": 10
    }
}

# ==========================================
# 3. 遊戲核心邏輯 (Game State)
# ==========================================

if 'game' not in st.session_state:
    st.session_state.game = None
    st.session_state.log = ["系統就緒。"]

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

def init_game():
    deck_list = []
    for name, count in ALL_DECKS["惡系強攻牌組"].items():
        for _ in range(count):
            card = create_card(name)
            if card: deck_list.append(card)
    
    random.shuffle(deck_list)
    p_hand = [deck_list.pop(0) for _ in range(7)]
    p_prizes = [deck_list.pop(0) for _ in range(6)]
    
    op_deck = deck_list.copy()
    random.shuffle(op_deck)
    op_active = create_card("瑪俐的搗蛋小妖")
    op_bench = [create_card("願增猿"), create_card("雪童子")]
    
    st.session_state.game = {
        "turn": 1,
        "supporter_used": False,
        "player": {
            "deck": deck_list, "hand": p_hand, "prizes": p_prizes,
            "active": None, "bench": [], "discard": []
        },
        "opponent": {
            "deck": op_deck, "hand": [1]*5, "prizes": [1]*6,
            "active": op_active, "bench": op_bench, "discard": []
        }
    }
    log_msg("遊戲開始！手牌已抽取。")

# --- 戰鬥動作 ---
def action_play_basic(card_idx):
    pl = st.session_state.game['player']
    card = pl['hand'][card_idx]
    if not pl['active']:
        pl['active'] = card
        pl['hand'].pop(card_idx)
        log_msg(f"前台出戰：{card['name']}")
    elif len(pl['bench']) < 5:
        pl['bench'].append(card)
        pl['hand'].pop(card_idx)
        log_msg(f"備戰區：{card['name']}")

def action_attach_energy(card_idx, target_loc, target_idx=None):
    pl = st.session_state.game['player']
    energy = pl['hand'][card_idx]
    target = pl['active'] if target_loc=='active' else pl['bench'][target_idx]
    target['attached'].append(energy)
    pl['hand'].pop(card_idx)
    log_msg(f"貼能給 {target['name']}")
    st.rerun()

def action_attack(move_idx):
    game = st.session_state.game
    pl = game['player']
    op = game['opponent']
    if not pl['active']: return
    
    move = pl['active']['moves'][move_idx]
    cost = move['cost']
    current_en = len(pl['active']['attached'])
    
    if current_en < cost:
        st.toast(f"❌ 能量不足！需要 {cost}，目前 {current_en}")
        return

    damage = move['d']
    op_wk = op['active'].get('weakness')
    my_type = pl['active'].get('type')
    
    msg = f"{pl['active']['name']} 使用 {move['n']}！"
    if op_wk and my_type == op_wk:
        damage *= 2
        msg += " (弱點x2!)"
        
    op['active']['damage'] += damage
    log_msg(f"{msg} 造成 {damage} 傷害。")
    
    if op['active']['damage'] >= op['active']['hp']:
        log_msg(f"對手 {op['active']['name']} 氣絕！")
        op['discard'].append(op['active'])
        op['active'] = None
        if pl['prizes']:
            prize = pl['prizes'].pop(0)
            pl['hand'].append(prize)
            log_msg(f"拿取獎賞卡：{prize['name']}")

def action_play_trainer(card_idx):
    game = st.session_state.game
    pl = game['player']
    card = pl['hand'][card_idx]
    
    if card['sub'] == 'Supporter':
        if game['supporter_used']:
            st.toast("本回合已用過支援者"); return
        game['supporter_used'] = True
        
    logic = card.get('logic')
    if logic == 'draw_to_6':
        need = 6 - len(pl['hand']) + 1
        for _ in range(max(0, need)):
            if pl['deck']: pl['hand'].append(pl['deck'].pop(0))
        log_msg(f"使用 {card['name']} 補牌")
    elif logic == 'discard_draw_5':
        pl['discard'].extend(pl['hand'])
        pl['hand'] = []
        for _ in range(5):
            if pl['deck']: pl['hand'].append(pl['deck'].pop(0))
        log_msg(f"使用 {card['name']} 重抽")
    else:
        log_msg(f"使用 {card['name']}")
        
    pl['discard'].append(pl['hand'].pop(card_idx))
    st.rerun()

def end_turn():
    game = st.session_state.game
    game['turn'] += 1
    game['supporter_used'] = False
    pl = game['player']
    if pl['deck']:
        card = pl['deck'].pop(0)
        pl['hand'].append(card)
        log_msg(f"抽牌：{card['name']}")
    st.rerun()

# ==========================================
# 4. 顯示組件 (UI)
# ==========================================

def render_card_with_info(card, width=120, is_active=False):
    if not card: return

    # 1. 直接讀取同目錄下的圖片
    path = get_smart_image_path(card['img_base'])
    
    # 2. 顯示圖片
    if path:
        st.image(path, width=width)
    else:
        st.error(f"❌ 缺圖: {card['name']}")
        st.caption("請把圖片跟 app.py 放在一起")

    # 3. 戰鬥數據
    if is_active and card['cat'] == 'Pokemon':
        hp_rem = card['hp'] - card.get('damage', 0)
        
        st.markdown(f"**HP: {hp_rem} / {card['hp']}**")
        st.caption(f"⚡ {len(card.get('attached', []))} | ↩️ {card.get('retreat')}")
        
        if 'moves' in card:
            st.markdown("---")
            for m in card['moves']:
                st.markdown(f"**⚡{m['cost']} {m['n']} {m['d']}**")
    
    # 4. 訓練家說明
    elif card['cat'] == 'Trainer':
        with st.popover("功能"):
            st.caption(card.get('logic', '一般物品'))

# ==========================================
# 5. 主程式入口
# ==========================================

if st.session_state.game is None:
    st.title("PTCG 圖片戰鬥系統 v17 (同層目錄版)")
    st.write(f"📂 正在此資料夾讀取圖片： `{IMAGE_FOLDER}`")
    
    if st.button("🚀 開始遊戲"):
        init_game()
        st.rerun()

else:
    game = st.session_state.game
    pl = game['player']
    op = game['opponent']

    # --- 側邊欄 ---
    with st.sidebar:
        st.header(f"第 {game['turn']} 回合")
        if st.button("🔚 結束回合"): end_turn()
        
        st.divider()
        if st.button("🪙 擲硬幣"):
            res = random.choice(["正面", "反面"])
            st.info(f"結果：{res}")
            
        st.divider()
        st.write("📜 戰鬥紀錄")
        for l in reversed(st.session_state.log[-8:]): st.caption(l)
        if st.button("重置"): st.session_state.game=None; st.rerun()

    # --- 戰場 ---
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("### 😈 對手")
        if op['active']: render_card_with_info(op['active'], 150, True)
    with col2:
        st.write(f"手牌: {len(op['hand'])} | 獎賞: {len(op['prizes'])}")
        st.caption("對手備戰區")
        cols = st.columns(5)
        for i, c in enumerate(op['bench']):
            with cols[i]: render_card_with_info(c, 80)

    st.markdown("---")

    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption("你的備戰區")
        cols = st.columns(5)
        for i, c in enumerate(pl['bench']):
            with cols[i]: render_card_with_info(c, 80)
            
    with col2:
        st.markdown("### 👤 你")
        if pl['active']:
            render_card_with_info(pl['active'], 160, True)
            # 攻擊選單
            moves = pl['active']['moves']
            move_names = [f"{m['n']} ({m['d']})" for m in moves]
            sel_move = st.selectbox("選擇招式", range(len(moves)), format_func=lambda x: move_names[x])
            if st.button("💥 攻擊"):
                action_attack(sel_move)
                st.rerun()
                
            if st.button("🏳️ 撤退"):
                pl['discard'].append(pl['active'])
                for e in pl['active']['attached']: pl['discard'].append(e)
                pl['active'] = None; st.rerun()
        else:
            st.warning("請派怪上場")

    st.markdown("---")
    
    # --- 手牌區 ---
    st.subheader(f"✋ 手牌 ({len(pl['hand'])})")
    if pl['hand']:
        rows = [pl['hand'][i:i+6] for i in range(0, len(pl['hand']), 6)]
        for r_idx, row in enumerate(rows):
            cols = st.columns(6)
            for c_idx, card in enumerate(row):
                idx = r_idx * 6 + c_idx
                with cols[c_idx]:
                    render_card_with_info(card, 110)
                    
                    # 操作按鈕
                    c1, c2 = st.columns(2)
                    with c1:
                        if card['cat'] == 'Pokemon' and card.get('stage') == 'Basic':
                            if st.button("⬆️", key=f"p_{idx}"): action_play_basic(idx); st.rerun()
                        elif card['cat'] == 'Trainer':
                            if st.button("✨", key=f"t_{idx}"): action_play_trainer(idx)
                        elif card['cat'] == 'Energy':
                            if st.button("⚡", key=f"e_{idx}"): action_attach_energy(idx, 'active')
                    with c2:
                        if st.button("🗑️", key=f"d_{idx}"):
                            pl['discard'].append(pl['hand'].pop(idx)); st.rerun()