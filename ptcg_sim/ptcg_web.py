import streamlit as st
import random
import uuid
import time
import os

st.set_page_config(page_title="PTCG 擬真對戰模擬 v10", layout="wide", page_icon="⚔️")

# ==========================================
# 1. 核心工具與資料庫
# ==========================================

def get_smart_image_path(base_name):
    """讀取圖片，支援大小寫"""
    exts = [".jpg", ".JPG", ".png", ".PNG", ".jpeg", ".JPEG"]
    if os.path.exists(base_name): return base_name
    for ext in exts:
        path = f"{base_name}{ext}"
        if os.path.exists(path): return path
    return None # 這裡回傳 None 代表缺圖

# 卡片資料庫 (請注意 stage: "Basic" 是程式判斷基礎寶可夢的關鍵)
CARD_DB = {
    # --- 寶可夢 ---
    "瑪俐的長毛巨魔 ex": {"cat": "Pokemon", "stage": "Stage 2", "hp": 320, "img_base": "grimmsnarl_ex", "type": "Darkness", "retreat": 2, "moves": [{"n":"暗影子彈","d":180}]},
    "瑪俐的詐唬魔": {"cat": "Pokemon", "stage": "Stage 1", "hp": 100, "img_base": "morgrem", "type": "Darkness", "retreat": 1, "moves": [{"n":"推擊","d":40}]},
    "瑪俐的搗蛋小妖": {"cat": "Pokemon", "stage": "Basic", "hp": 70, "img_base": "impidimp", "type": "Darkness", "retreat": 1, "moves": [{"n":"偷盜","d":0}]},
    
    "願增猿": {"cat": "Pokemon", "stage": "Basic", "hp": 110, "img_base": "munkidori", "type": "Psychic", "retreat": 1, "moves": [{"n":"精神歪曲","d":60}]},
    "雪妖女": {"cat": "Pokemon", "stage": "Stage 1", "hp": 90, "img_base": "froslass", "type": "Water", "retreat": 1, "moves": [{"n":"冰霜粉碎","d":60}]},
    "雪童子": {"cat": "Pokemon", "stage": "Basic", "hp": 60, "img_base": "snorunt", "type": "Water", "retreat": 1, "moves": [{"n":"寒意","d":10}]},
    "月月熊 赫月 ex": {"cat": "Pokemon", "stage": "Basic", "hp": 260, "img_base": "bloodmoon_ursaluna", "type": "Colorless", "retreat": 3, "moves": [{"n":"血月","d":240}]},
    "含羞苞": {"cat": "Pokemon", "stage": "Basic", "hp": 30, "img_base": "budew", "type": "Grass", "retreat": 0, "moves": [{"n":"進化花粉","d":0}]},
    "可達鴨": {"cat": "Pokemon", "stage": "Basic", "hp": 70, "img_base": "psyduck", "type": "Water", "retreat": 1, "moves": [{"n":"頭痛","d":10}]},
    "米立龍": {"cat": "Pokemon", "stage": "Basic", "hp": 70, "img_base": "tatsugiri", "type": "Dragon", "retreat": 1, "moves": [{"n":"噴水","d":50}]},

    # --- 訓練家 ---
    "寶可平板": {"cat": "Trainer", "sub": "Item", "img_base": "poke_tablet"},
    "好友寶芬": {"cat": "Trainer", "sub": "Item", "img_base": "buddy_poffin"},
    "夜間擔架": {"cat": "Trainer", "sub": "Item", "img_base": "night_stretcher"},
    "神奇糖果": {"cat": "Trainer", "sub": "Item", "img_base": "rare_candy"},
    "高級球": {"cat": "Trainer", "sub": "Item", "img_base": "ultra_ball"},
    "能量轉移": {"cat": "Trainer", "sub": "Item", "img_base": "energy_switch"},
    "不公印章": {"cat": "Trainer", "sub": "Item", "img_base": "unfair_stamp"},
    "氣球": {"cat": "Trainer", "sub": "Tool", "img_base": "air_balloon"},
    "莉莉艾的決意": {"cat": "Trainer", "sub": "Supporter", "img_base": "lillie_resolve"},
    "火箭隊的拉姆達": {"cat": "Trainer", "sub": "Supporter", "img_base": "rocket_lambda"},
    "老大的指令": {"cat": "Trainer", "sub": "Supporter", "img_base": "boss_orders"},
    "丹瑜": {"cat": "Trainer", "sub": "Supporter", "img_base": "carmine"},
    "尖釘鎮道館": {"cat": "Trainer", "sub": "Stadium", "img_base": "spikemuth_gym"},

    # --- 能量 ---
    "基本惡能量": {"cat": "Energy", "sub": "Basic", "img_base": "dark_energy"}
}

# 預設兩套牌組供選擇
ALL_DECKS = {
    "惡系強攻牌組 (預設)": {
        "瑪俐的長毛巨魔 ex": 2, "瑪俐的詐唬魔": 2, "瑪俐的搗蛋小妖": 3, "願增猿": 4,
        "含羞苞": 1, "可達鴨": 1, "雪童子": 2, "雪妖女": 2, "月月熊 赫月 ex": 1,
        "米立龍": 1, "寶可平板": 3, "好友寶芬": 3, "夜間擔架": 3, "神奇糖果": 2,
        "能量轉移": 1, "高級球": 1, "不公印章": 1, "氣球": 1, "莉莉艾的決意": 4,
        "老大的指令": 3, "火箭隊的拉姆達": 4, "丹瑜": 3, "尖釘鎮道館": 3, "基本惡能量": 9
    },
    "測試用牌組 (全基礎怪)": {
        "瑪俐的搗蛋小妖": 20, "基本惡能量": 20, "丹瑜": 20
    }
}

# ==========================================
# 2. 狀態管理與初始化
# ==========================================

if 'phase' not in st.session_state:
    st.session_state.phase = 'deck_selection' # 初始狀態：選牌組
    st.session_state.log = []
    st.session_state.p_deck_name = "惡系強攻牌組 (預設)"
    st.session_state.o_deck_name = "惡系強攻牌組 (預設)"

def create_card_instance(name):
    base = CARD_DB.get(name)
    if not base: return None
    card = base.copy()
    card['id'] = str(uuid.uuid4())
    card['name'] = name
    if card['cat'] == 'Pokemon':
        card['damage'] = 0
        card['attached_energy'] = []
    return card

def build_deck(deck_dict):
    cards = []
    for name, count in deck_dict.items():
        for _ in range(count):
            c = create_card_instance(name)
            if c: cards.append(c)
    return cards

def check_basic(hand):
    """檢查手牌是否有基礎寶可夢"""
    for c in hand:
        if c.get('stage') == 'Basic':
            return True
    return False

# ==========================================
# 3. 渲染函式 (負責顯示圖片)
# ==========================================

def render_card_img(card, width=120):
    if not card: return
    path = get_smart_image_path(card['img_base'])
    if path:
        st.image(path, width=width)
    else:
        st.error(f"缺圖: {card['name']}")

# ==========================================
# 4. 遊戲流程控制 (Step-by-Step)
# ==========================================

# --- 階段 1: 選擇牌組 ---
if st.session_state.phase == 'deck_selection':
    st.title("🎴 準備階段：選擇牌組")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 玩家 (你)")
        st.session_state.p_deck_name = st.selectbox("選擇你的牌組", list(ALL_DECKS.keys()), index=0)
    with col2:
        st.subheader("🤖 電腦 (對手)")
        st.session_state.o_deck_name = st.selectbox("選擇對手牌組", list(ALL_DECKS.keys()), index=0)
    
    if st.button("確認並預覽牌組", type="primary"):
        st.session_state.player_deck_list = build_deck(ALL_DECKS[st.session_state.p_deck_name])
        st.session_state.opponent_deck_list = build_deck(ALL_DECKS[st.session_state.o_deck_name])
        st.session_state.phase = 'deck_preview'
        st.rerun()

# --- 階段 2: 預覽 60 張卡片 ---
elif st.session_state.phase == 'deck_preview':
    st.title("👀 牌組確認 (60張)")
    st.write(f"目前使用的牌組: **{st.session_state.p_deck_name}**")
    
    # 顯示所有卡片圖片
    cards = st.session_state.player_deck_list
    cols_per_row = 8
    rows = [cards[i:i+cols_per_row] for i in range(0, len(cards), cols_per_row)]
    
    for row in rows:
        cols = st.columns(cols_per_row)
        for idx, card in enumerate(row):
            with cols[idx]:
                render_card_img(card, width=100)
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 重選牌組"):
            st.session_state.phase = 'deck_selection'
            st.rerun()
    with col2:
        if st.button("✅ 雙方準備完成，前往擲硬幣"):
            st.session_state.phase = 'coin_flip'
            st.rerun()

# --- 階段 3: 擲硬幣 ---
elif st.session_state.phase == 'coin_flip':
    st.title("🪙 擲硬幣決定先攻")
    
    if 'coin_result' not in st.session_state:
        if st.button("擲硬幣 (點擊)"):
            res = random.choice(["heads", "tails"])
            st.session_state.coin_result = res
            st.rerun()
    else:
        res = st.session_state.coin_result
        # 顯示硬幣圖片
        img = get_smart_image_path(f"coin_{res}")
        if img:
            st.image(img, width=200)
        else:
            st.header("正面" if res == "heads" else "反面")
            
        st.subheader("你先攻！" if res == "heads" else "對手先攻！")
        
        if st.button("開始洗牌"):
            del st.session_state.coin_result
            st.session_state.game = {
                "player": {"deck": st.session_state.player_deck_list, "hand": [], "prizes": [], "bench": [], "active": None, "discard": []},
                "opponent": {"deck": st.session_state.opponent_deck_list, "hand": [], "prizes": [], "bench": [], "active": None, "discard": []},
                "log": [],
                "mulligan_done": False # 標記是否完成調度
            }
            st.session_state.phase = 'shuffling'
            st.rerun()

# --- 階段 4: 手動洗牌 ---
elif st.session_state.phase == 'shuffling':
    st.title("🔀 洗牌階段")
    
    c1, c2 = st.columns(2)
    with c1:
        st.write("你的牌庫 (尚未洗牌)")
        if st.button("手動洗牌 (Player)"):
            random.shuffle(st.session_state.game['player']['deck'])
            st.success("你的牌庫已洗牌！")
            st.session_state.p_shuffled = True
    
    with c2:
        st.write("對手牌庫")
        if st.session_state.get('p_shuffled'):
             st.info("對手正在洗牌...")
             random.shuffle(st.session_state.game['opponent']['deck'])
             st.success("對手牌庫已洗牌！")
    
    if st.session_state.get('p_shuffled'):
        st.divider()
        if st.button("雙方洗牌完成，開始抽牌"):
            st.session_state.phase = 'draw_initial'
            st.rerun()

# --- 階段 5: 抽初始 7 張 ---
elif st.session_state.phase == 'draw_initial':
    st.title("✋ 抽取起始手牌")
    pl = st.session_state.game['player']
    op = st.session_state.game['opponent']
    
    st.write(f"目前手牌數: {len(pl['hand'])}")
    
    if len(pl['hand']) == 0:
        if st.button("從牌庫頂抽取 7 張"):
            for _ in range(7):
                pl['hand'].append(pl['deck'].pop(0))
                op['hand'].append(op['deck'].pop(0)) # 對手同步抽
            st.rerun()
    else:
        # 顯示抽到的牌
        cols = st.columns(7)
        for i, card in enumerate(pl['hand']):
            with cols[i]:
                render_card_img(card, width=100)
        
        st.markdown("### 檢查基礎寶可夢")
        st.info("請確認手牌中是否有「基礎 (Basic)」寶可夢。對手也在確認中...")
        
        if st.button("確認手牌"):
            st.session_state.phase = 'check_mulligan'
            st.rerun()

# --- 階段 6: 基礎寶可夢檢測 (Mulligan 邏輯) ---
elif st.session_state.phase == 'check_mulligan':
    st.title("🔍 基礎寶可夢判定")
    
    pl = st.session_state.game['player']
    op = st.session_state.game['opponent']
    
    p_has_basic = check_basic(pl['hand'])
    o_has_basic = check_basic(op['hand'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("你的狀態")
        if p_has_basic:
            st.success("✅ 有基礎寶可夢")
        else:
            st.error("❌ 無基礎寶可夢 (需重抽)")
            
    with c2:
        st.subheader("對手狀態")
        if o_has_basic:
            st.success("✅ 對手有基礎寶可夢")
        else:
            st.error("❌ 對手無基礎寶可夢")

    st.divider()
    
    # --- 邏輯判斷區 ---
    
    # 情況 A: 雙方都有 -> 進下一步
    if p_has_basic and o_has_basic:
        st.success("雙方手牌皆成立！")
        if st.button("設置獎賞卡 (下一步)"):
            st.session_state.phase = 'setup_prizes'
            st.rerun()
            
    # 情況 B: 雙方都沒有 -> 雙方重抽 (無懲罰)
    elif not p_has_basic and not o_has_basic:
        st.warning("雙方都沒有基礎寶可夢，雙方重抽！")
        if st.button("將手牌洗回牌庫並重抽 7 張"):
            # 玩家重洗
            pl['deck'].extend(pl['hand'])
            pl['hand'] = []
            random.shuffle(pl['deck'])
            # 對手重洗
            op['deck'].extend(op['hand'])
            op['hand'] = []
            random.shuffle(op['deck'])
            # 回到抽牌階段
            st.session_state.phase = 'draw_initial'
            st.rerun()
            
    # 情況 C: 只有玩家沒有 -> 玩家重抽，對手可多抽
    elif not p_has_basic and o_has_basic:
        st.warning("你沒有基礎寶可夢，必須重抽。對手可以多抽 1 張。")
        if st.button("執行重抽 (Mulligan)"):
            # 對手多抽一張 (這裡簡化為自動抽，實際上對手可以選擇)
            op['hand'].append(op['deck'].pop(0))
            st.session_state.game['log'].append("對手因你重抽而多抽了1張卡。")
            
            # 玩家重洗
            pl['deck'].extend(pl['hand'])
            pl['hand'] = []
            random.shuffle(pl['deck'])
            st.session_state.phase = 'draw_initial'
            st.rerun()
            
    # 情況 D: 只有對手沒有 -> 對手重抽，玩家可多抽
    elif p_has_basic and not o_has_basic:
        st.warning("對手沒有基礎寶可夢，對手正在重抽...")
        st.info("你可以選擇是否多抽 1 張卡。")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("我要多抽 1 張"):
                pl['hand'].append(pl['deck'].pop(0))
                st.session_state.game['log'].append("你選擇多抽1張卡。")
                # 對手重洗
                op['deck'].extend(op['hand'])
                op['hand'] = []
                random.shuffle(op['deck'])
                # 因為對手重洗了，必須回到判定階段(雖然玩家不用重抽，但要等對手抽完確認)
                # 這裡為了流程順暢，直接讓對手補滿7張再判定
                for _ in range(7): op['hand'].append(op['deck'].pop(0))
                st.rerun()
        
        with col_b:
            if st.button("我不抽，直接讓對手重抽"):
                # 對手重洗
                op['deck'].extend(op['hand'])
                op['hand'] = []
                random.shuffle(op['deck'])
                for _ in range(7): op['hand'].append(op['deck'].pop(0))
                st.rerun()

# --- 階段 7: 設置獎賞卡 ---
elif st.session_state.phase == 'setup_prizes':
    st.title("🏆 設置獎賞卡")
    pl = st.session_state.game['player']
    op = st.session_state.game['opponent']
    
    st.write("雙方手牌確認完畢。現在從牌庫頂設置 6 張獎賞卡。")
    
    if len(pl['prizes']) == 0:
        if st.button("設置獎賞卡"):
            for _ in range(6):
                pl['prizes'].append(pl['deck'].pop(0))
                op['prizes'].append(op['deck'].pop(0))
            st.rerun()
    else:
        st.success("獎賞卡設置完成！")
        # 顯示獎賞卡背面 (這裡用文字或背面圖示意)
        st.write(f"你的獎賞卡: {len(pl['prizes'])} 張")
        st.write(f"對手獎賞卡: {len(op['prizes'])} 張")
        
        if st.button("⚔️ 開始戰鬥！"):
            st.session_state.phase = 'battle'
            st.rerun()

# --- 階段 8: 正式戰鬥 (主要介面) ---
elif st.session_state.phase == 'battle':
    game = st.session_state.game
    pl = game['player']
    op = game['opponent']

    # 側邊欄紀錄
    with st.sidebar:
        st.title("戰鬥紀錄")
        if st.button("重置遊戲"):
            del st.session_state.phase
            st.rerun()
        for l in game['log']: st.text(l)

    # 對手區
    st.subheader(f"🤖 對手 (手牌:{len(op['hand'])} | 牌庫:{len(op['deck'])})")
    c1, c2 = st.columns([1, 4])
    with c1:
        st.write(f"🏆 獎賞: {len(op['prizes'])}")
        # 這裡未來可以加入對手自動放置基礎寶可夢到場上的邏輯
        if not op['active']:
             # 簡單自動派出一隻
             basics = [c for c in op['hand'] if c.get('stage')=='Basic']
             if basics:
                 op['active'] = basics[0]
                 op['hand'].remove(basics[0])
        
        if op['active']:
            render_card_img(op['active'])
            st.caption(f"HP: {op['active']['hp']}")
        else:
            st.info("對手無戰鬥寶可夢")
            
    with c2:
        st.caption("備戰區")
        cols = st.columns(5)
        for i, card in enumerate(op['bench']):
            with cols[i]: render_card_img(card, 80)

    st.markdown("---")

    # 玩家區
    st.subheader(f"👤 你 (手牌:{len(pl['hand'])} | 牌庫:{len(pl['deck'])})")
    c1, c2 = st.columns([4, 1])
    
    with c1: # 備戰與戰鬥
        col_act, col_bench = st.columns([1, 3])
        with col_act:
            st.caption("戰鬥場")
            if pl['active']:
                render_card_img(pl['active'])
                st.caption(f"HP: {pl['active']['hp']}")
            else:
                st.warning("請從手牌打出基礎寶可夢")
        
        with col_bench:
            st.caption("備戰區")
            cols = st.columns(5)
            for i, card in enumerate(pl['bench']):
                with cols[i]: render_card_img(card, 80)
                
    with c2: # 獎賞
        st.write(f"🏆 獎賞: {len(pl['prizes'])}")
        if st.button("抽牌"):
            if pl['deck']: pl['hand'].append(pl['deck'].pop(0)); st.rerun()

    # 手牌區
    st.markdown("---")
    st.write("✋ 你的手牌")
    if pl['hand']:
        cols = st.columns(8)
        for i, card in enumerate(pl['hand']):
            with cols[i]:
                render_card_img(card, 100)
                # 簡單操作
                if st.button("派至戰鬥", key=f"bat_{i}"):
                    if not pl['active'] and card.get('stage')=='Basic':
                        pl['active'] = pl['hand'].pop(i)
                        st.rerun()
                if st.button("派至備戰", key=f"ben_{i}"):
                     if len(pl['bench']) < 5 and card.get('stage')=='Basic':
                        pl['bench'].append(pl['hand'].pop(i))
                        st.rerun()