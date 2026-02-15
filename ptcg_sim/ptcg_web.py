import streamlit as st
import random
import uuid
import os
import time

st.set_page_config(page_title="PTCG 戰鬥融合版 v14", layout="wide", page_icon="⚔️")

# ==========================================
# 1. 系統核心設定
# ==========================================
IMAGE_FOLDER = "images"

def get_smart_image_path(base_name):
    """讀取圖片路徑"""
    if not os.path.exists(IMAGE_FOLDER): return None
    exts = [".jpg", ".JPG", ".png", ".PNG", ".jpeg", ".JPEG"]
    for ext in exts:
        path = os.path.join(IMAGE_FOLDER, f"{base_name}{ext}")
        if os.path.exists(path): return path
    return None

# ==========================================
# 2. 完整資料庫 (數值 + 邏輯標籤)
# ==========================================
CARD_DB = {
    # --- 寶可夢 ---
    "瑪俐的長毛巨魔 ex": {
        "cat": "Pokemon", "stage": "Stage 2", "hp": 320, "type": "Darkness", "retreat": 2, 
        "weakness": "Grass", "resistance": None, "img_base": "grimmsnarl_ex",
        "moves": [{"n": "不知夜", "cost": 1, "d": 0}, {"n": "暗影子彈", "cost": 3, "d": 180}]
    },
    "瑪俐的詐唬魔": {
        "cat": "Pokemon", "stage": "Stage 1", "hp": 100, "type": "Darkness", "retreat": 1, 
        "weakness": "Grass", "img_base": "morgrem",
        "moves": [{"n": "推擊", "cost": 1, "d": 40}]
    },
    "瑪俐的搗蛋小妖": {
        "cat": "Pokemon", "stage": "Basic", "hp": 70, "type": "Darkness", "retreat": 1, 
        "weakness": "Grass", "img_base": "impidimp",
        "moves": [{"n": "偷盜", "cost": 1, "d": 0}]
    },
    "願增猿": {
        "cat": "Pokemon", "stage": "Basic", "hp": 110, "type": "Psychic", "retreat": 1, 
        "weakness": "Darkness", "resistance": "Fighting", "img_base": "munkidori",
        "moves": [{"n": "精神歪曲", "cost": 2, "d": 60}]
    },
    "雪妖女": {
        "cat": "Pokemon", "stage": "Stage 1", "hp": 90, "type": "Water", "retreat": 1, 
        "weakness": "Metal", "img_base": "froslass",
        "moves": [{"n": "冰霜粉碎", "cost": 2, "d": 60}]
    },
    "雪童子": {
        "cat": "Pokemon", "stage": "Basic", "hp": 60, "type": "Water", "retreat": 1, 
        "weakness": "Metal", "img_base": "snorunt",
        "moves": [{"n": "寒意", "cost": 1, "d": 10}]
    },
    "月月熊 赫月 ex": {
        "cat": "Pokemon", "stage": "Basic", "hp": 260, "type": "Colorless", "retreat": 3, 
        "weakness": "Fighting", "img_base": "bloodmoon_ursaluna",
        "moves": [{"n": "血月", "cost": 5, "d": 240}]
    },
    "含羞苞": {
        "cat": "Pokemon", "stage": "Basic", "hp": 30, "type": "Grass", "retreat": 0, 
        "weakness": "Fire", "img_base": "budew",
        "moves": [{"n": "發現寶藏", "cost": 0, "d": 0}]
    },
    "可達鴨": {
        "cat": "Pokemon", "stage": "Basic", "hp": 70, "type": "Water", "retreat": 1, 
        "weakness": "Lightning", "img_base": "psyduck",
        "moves": [{"n": "過度思考", "cost": 1, "d": 0}]
    },
    "米立龍": {
        "cat": "Pokemon", "stage": "Basic", "hp": 70, "type": "Dragon", "retreat": 1, 
        "img_base": "tatsugiri",
        "moves": [{"n": "衝浪", "cost": 2, "d": 50}]
    },

    # --- 訓練家 (加入 logic_type 以便程式判斷功能) ---
    "寶可平板": {"cat": "Trainer", "sub": "Item", "img_base": "poke_tablet", "logic": "search_prize"},
    "好友寶芬": {"cat": "Trainer", "sub": "Item", "img_base": "buddy_poffin", "logic": "search_deck"},
    "夜間擔架": {"cat": "Trainer", "sub": "Item", "img_base": "night_stretcher", "logic": "recover"},
    "神奇糖果": {"cat": "Trainer", "sub": "Item", "img_base": "rare_candy", "logic": "evolve"},
    "高級球": {"cat": "Trainer", "sub": "Item", "img_base": "ultra_ball", "logic": "search_deck"},
    "能量轉移": {"cat": "Trainer", "sub": "Item", "img_base": "energy_switch", "logic": "move_energy"},
    "不公印章": {"cat": "Trainer", "sub": "Item", "img_base": "unfair_stamp", "logic": "disrupt"},
    "氣球": {"cat": "Trainer", "sub": "Tool", "img_base": "air_balloon", "logic": "tool"},
    
    # 支援者 (Supporter) - 抽牌邏輯已實作
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
# 3. 遊戲狀態管理 (Game State)
# ==========================================

if 'game' not in st.session_state:
    st.session_state.game = None
    st.session_state.log = ["遊戲系統啟動。"]

def log_msg(msg):
    st.session_state.log.append(f"[{time.strftime('%H:%M')}] {msg}")

def create_card(name):
    base = CARD_DB.get(name)
    if not base: return None
    c = base.copy()
    c['id'] = str(uuid.uuid4())[:8]
    c['name'] = name
    # 初始化寶可夢數值
    if c['cat'] == 'Pokemon':
        c['damage'] = 0
        c['attached'] = [] # 這裡存能量卡
        c['conditions'] = [] # 異常狀態
    return c

def init_game():
    deck_list = []
    # 建構牌組
    for name, count in ALL_DECKS["惡系強攻牌組"].items():
        for _ in range(count):
            card = create_card(name)
            if card: deck_list.append(card)
    
    random.shuffle(deck_list)
    
    # 簡單發牌邏輯：抽7張，設獎賞，設對手
    p_hand = [deck_list.pop(0) for _ in range(7)]
    p_prizes = [deck_list.pop(0) for _ in range(6)]
    
    # 對手 (假資料，為了模擬)
    op_deck = deck_list.copy()
    random.shuffle(op_deck)
    op_active = create_card("瑪俐的搗蛋小妖")
    op_bench = [create_card("願增猿")]
    
    st.session_state.game = {
        "turn": 1,
        "supporter_used": False, # 判斷這回合用過支援者沒
        "player": {
            "deck": deck_list,
            "hand": p_hand,
            "prizes": p_prizes,
            "active": None,
            "bench": [],
            "discard": []
        },
        "opponent": {
            "deck": op_deck,
            "hand": [1]*5, # 只存數量
            "prizes": [1]*6,
            "active": op_active,
            "bench": op_bench,
            "discard": []
        }
    }
    log_msg("遊戲開始！手牌已抽取。")

# ==========================================
# 4. 動作邏輯 (Action Logic)
# ==========================================

def action_play_basic(card_idx):
    """打出基礎寶可夢"""
    pl = st.session_state.game['player']
    card = pl['hand'][card_idx]
    
    if not pl['active']:
        pl['active'] = card
        pl['hand'].pop(card_idx)
        log_msg(f"將 {card['name']} 放置於戰鬥場！")
    elif len(pl['bench']) < 5:
        pl['bench'].append(card)
        pl['hand'].pop(card_idx)
        log_msg(f"將 {card['name']} 放置於備戰區。")
    else:
        st.error("備戰區已滿！")

def action_attach_energy(card_idx, target_loc, target_idx=None):
    """
    貼能量
    target_loc: 'active' 或 'bench'
    target_idx: 如果是 bench，第幾隻
    """
    pl = st.session_state.game['player']
    energy_card = pl['hand'][card_idx]
    
    target_mon = None
    if target_loc == 'active':
        target_mon = pl['active']
    elif target_loc == 'bench':
        target_mon = pl['bench'][target_idx]
        
    if target_mon:
        target_mon['attached'].append(energy_card)
        pl['hand'].pop(card_idx)
        log_msg(f"將 {energy_card['name']} 附於 {target_mon['name']} 身上。")
        st.rerun()

def action_attack(move_idx):
    """攻擊邏輯"""
    game = st.session_state.game
    pl = game['player']
    op = game['opponent']
    
    if not pl['active']: return
    
    move = pl['active']['moves'][move_idx]
    cost = move['cost']
    current_energy = len(pl['active']['attached'])
    
    # 檢查能量
    if current_energy < cost:
        st.toast(f"❌ 能量不足！需要 {cost}，目前 {current_energy}", icon="⚠️")
        return

    # 計算傷害
    damage = move['d']
    
    # 處理弱點 (簡單版：只看屬性名稱)
    op_weakness = op['active'].get('weakness')
    my_type = pl['active'].get('type')
    
    is_weakness = False
    if op_weakness and my_type == op_weakness:
        damage *= 2
        is_weakness = True
        
    # 造成傷害
    op['active']['damage'] += damage
    
    log_msg(f"{pl['active']['name']} 使用「{move['n']}」！")
    if is_weakness: log_msg("擊中弱點！傷害加倍！")
    log_msg(f"對手 {op['active']['name']} 受到 {damage} 點傷害。")
    
    # 檢查氣絕
    if op['active']['damage'] >= op['active']['hp']:
        log_msg(f"對手的 {op['active']['name']} 氣絕了！")
        op['discard'].append(op['active'])
        op['active'] = None
        # 拿獎賞卡
        if pl['prizes']:
            prize = pl['prizes'].pop(0)
            pl['hand'].append(prize)
            log_msg(f"拿取一張獎賞卡：{prize['name']}")

def action_play_trainer(card_idx):
    """使用訓練家卡"""
    game = st.session_state.game
    pl = game['player']
    card = pl['hand'][card_idx]
    
    # 檢查支援者限制
    if card['sub'] == 'Supporter':
        if game['supporter_used']:
            st.toast("這回合已經用過支援者了！", icon="🚫")
            return
        game['supporter_used'] = True

    # --- 執行效果 ---
    logic = card.get('logic')
    
    # 1. 抽牌類 (丹瑜)
    if logic == 'discard_draw_5':
        pl['discard'].extend(pl['hand']) # 丟光手牌
        pl['hand'] = [] # 清空
        for _ in range(5): # 抽5張
            if pl['deck']: pl['hand'].append(pl['deck'].pop(0))
        log_msg(f"使用了 {card['name']}，重抽5張牌。")
        
    # 2. 抽牌類 (莉莉艾)
    elif logic == 'draw_to_6':
        draw_count = 6 - len(pl['hand']) + 1 # +1 是因為這張卡還沒丟掉
        if draw_count > 0:
            for _ in range(draw_count):
                if pl['deck']: pl['hand'].append(pl['deck'].pop(0))
        log_msg(f"使用了 {card['name']}，補滿手牌。")

    # 3. 通用類 (物品/無特定邏輯)
    else:
        log_msg(f"使用了 {card['name']} (效果請手動執行)。")

    # 移至棄牌區
    pl['discard'].append(pl['hand'].pop(card_idx))
    st.rerun()

def end_turn():
    """回合結束"""
    game = st.session_state.game
    game['turn'] += 1
    game['supporter_used'] = False
    
    # 模擬抽牌
    pl = game['player']
    if pl['deck']:
        card = pl['deck'].pop(0)
        pl['hand'].append(card)
        log_msg(f"回合開始，抽到了 {card['name']}。")
    
    st.rerun()

# ==========================================
# 5. UI 渲染組件
# ==========================================

def render_card(card, width=100, is_active=False):
    """顯示卡片圖片與資訊"""
    if not card: return
    
    path = get_smart_image_path(card['img_base'])
    if path:
        st.image(path, width=width)
    else:
        st.error(f"缺圖: {card['name']}")

    if is_active and card['cat'] == 'Pokemon':
        hp_rem = card['hp'] - card['damage']
        st.caption(f"❤️ {hp_rem}/{card['hp']}")
        st.caption(f"⚡ {len(card['attached'])}")

# ==========================================
# 6. 主程式介面
# ==========================================

# 初始化檢查
if not os.path.exists(IMAGE_FOLDER):
    st.error(f"❌ 找不到 '{IMAGE_FOLDER}' 資料夾！程式無法執行。")
    st.stop()

if st.session_state.game is None:
    st.title("PTCG 戰鬥模擬器 v14 (完整版)")
    if st.button("🚀 開始遊戲"):
        init_game()
        st.rerun()
else:
    game = st.session_state.game
    pl = game['player']
    op = game['opponent']

    # --- 側邊欄 ---
    with st.sidebar:
        st.header("⚙️ 控制台")
        st.write(f"第 {game['turn']} 回合")
        if st.button("🪙 擲硬幣"):
            res = random.choice(["正面", "反面"])
            log_msg(f"擲硬幣結果：{res}")
            st.info(res)
        
        st.divider()
        st.write("📜 戰鬥紀錄")
        for l in reversed(st.session_state.log[-8:]):
            st.caption(l)
        
        st.divider()
        if st.button("🔚 結束回合 (抽牌)"):
            end_turn()

        if st.button("🔄 重置遊戲"):
            st.session_state.game = None
            st.rerun()

    # --- 對手區域 (上方) ---
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("### 😈 對手")
        if op['active']:
            render_card(op['active'], 140, True)
        else:
            st.warning("對手前台無寶可夢")
            
    with col2:
        st.write(f"手牌: {len(op['hand'])} | 獎賞: {len(op['prizes'])} | 牌庫: {len(op['deck'])}")
        st.caption("對手備戰區")
        row = st.columns(5)
        for i, c in enumerate(op['bench']):
            with row[i]: render_card(c, 80, True)

    st.markdown("---")

    # --- 玩家區域 (下方) ---
    col1, col2 = st.columns([4, 1])
    
    # 玩家備戰區
    with col1:
        st.caption("你的備戰區")
        row = st.columns(5)
        for i, c in enumerate(pl['bench']):
            with row[i]: 
                render_card(c, 80, True)

    # 玩家戰鬥場
    with col2:
        st.markdown("### 👤 你")
        if pl['active']:
            render_card(pl['active'], 150, True)
            
            # 攻擊按鈕
            st.write("⚔️ 招式:")
            for idx, move in enumerate(pl['active']['moves']):
                cost_str = "⚡" * move['cost'] if move['cost'] > 0 else "🆓"
                if st.button(f"{cost_str} {move['n']} {move['d']}", key=f"atk_{idx}"):
                    action_attack(idx)
                    st.rerun()
                    
            if st.button("🏳️ 撤退"):
                pl['discard'].append(pl['active'])
                for e in pl['active']['attached']: pl['discard'].append(e) # 棄能量
                pl['active'] = None
                st.rerun()
        else:
            st.warning("請打出基礎寶可夢！")

    st.markdown("---")
    
    # --- 手牌操作區 (最重要！) ---
    st.subheader(f"✋ 你的手牌 ({len(pl['hand'])})")
    
    if pl['hand']:
        rows = [pl['hand'][i:i+6] for i in range(0, len(pl['hand']), 6)]
        for r_idx, row in enumerate(rows):
            cols = st.columns(6)
            for c_idx, card in enumerate(row):
                idx = r_idx * 6 + c_idx
                with cols[c_idx]:
                    render_card(card, 100)
                    
                    # 依卡片類型顯示按鈕
                    
                    # 1. 寶可夢: 上場
                    if card['cat'] == 'Pokemon' and card['stage'] == 'Basic':
                        if st.button("⬆️ 上場", key=f"pl_{idx}"):
                            action_play_basic(idx)
                            st.rerun()
                    
                    # 2. 能量: 貼能
                    elif card['cat'] == 'Energy':
                        with st.popover("⚡ 貼能"):
                            if pl['active'] and st.button("貼戰鬥場", key=f"en_act_{idx}"):
                                action_attach_energy(idx, 'active')
                            for b_i, b_mon in enumerate(pl['bench']):
                                if st.button(f"貼 {b_mon['name']}", key=f"en_ben_{idx}_{b_i}"):
                                    action_attach_energy(idx, 'bench', b_i)
                                    
                    # 3. 訓練家: 使用
                    elif card['cat'] == 'Trainer':
                        # 顯示支援者是否可用
                        disabled = (card['sub']=='Supporter' and game['supporter_used'])
                        if st.button("✨ 使用", key=f"tr_{idx}", disabled=disabled):
                            action_play_trainer(idx)

                    # 4. 丟棄 (通用)
                    if st.button("🗑️", key=f"dis_{idx}"):
                        pl['discard'].append(pl['hand'].pop(idx))
                        st.rerun()