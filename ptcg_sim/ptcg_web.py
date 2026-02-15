import streamlit as st
import json
import os
import random
import base64

# ==========================================
# 1. 初始設定與樣式
# ==========================================
st.set_page_config(page_title="PTCG 戰鬥模擬器", layout="wide", page_icon="🎴")

# 載入圖片並轉為 Base64 (用於背景)
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# 設定背景圖片
def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    if bin_str:
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .block-container {{
            background-color: rgba(0, 0, 0, 0.6); /* 半透明黑底讓文字更清楚 */
            padding: 2rem;
            border-radius: 10px;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)

# 設定背景 (請確保 background.jpg 存在)
set_background('background.jpg')

# 自訂 CSS 樣式
st.markdown("""
<style>
    .card-container {
        border: 2px solid #444;
        border-radius: 8px;
        padding: 5px;
        text-align: center;
        background-color: #222;
        color: white;
    }
    .stButton>button {
        width: 100%;
        font-weight: bold;
    }
    .big-stat {
        font-size: 1.2rem;
        font-weight: bold;
        color: #FFD700;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 資料庫與狀態管理
# ==========================================
DB_FILE = 'cards.json'

@st.cache_data
def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 初始化 Session State
if 'deck' not in st.session_state:
    st.session_state.deck = []
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'hand' not in st.session_state:
    st.session_state.hand = []
if 'active_spot' not in st.session_state:
    st.session_state.active_spot = None
if 'bench' not in st.session_state:
    st.session_state.bench = []
if 'discard_pile' not in st.session_state:
    st.session_state.discard_pile = []
if 'prizes' not in st.session_state:
    st.session_state.prizes = []
if 'coin_result' not in st.session_state:
    st.session_state.coin_result = None

db = load_db()

# ==========================================
# 3. 邏輯函式
# ==========================================

def start_game():
    if len(st.session_state.deck) != 60:
        st.error("牌組必須剛好 60 張才能開始！")
        return
    
    # 複製牌組並洗牌
    game_deck = st.session_state.deck.copy()
    random.shuffle(game_deck)
    
    # 重置盤面
    st.session_state.game_deck = game_deck
    st.session_state.hand = []
    st.session_state.active_spot = None
    st.session_state.bench = []
    st.session_state.discard_pile = []
    st.session_state.prizes = []
    st.session_state.coin_result = None
    
    # 抽 7 張手牌
    for _ in range(7):
        if st.session_state.game_deck:
            st.session_state.hand.append(st.session_state.game_deck.pop(0))
            
    # 設置 6 張獎賞卡
    for _ in range(6):
        if st.session_state.game_deck:
            st.session_state.prizes.append(st.session_state.game_deck.pop(0))
            
    st.session_state.game_started = True

def draw_card():
    if st.session_state.game_deck:
        card = st.session_state.game_deck.pop(0)
        st.session_state.hand.append(card)
    else:
        st.error("牌庫沒牌了！")

def flip_coin():
    result = random.choice(["HEADS", "TAILS"])
    st.session_state.coin_result = result

# ==========================================
# 4. 介面：模式選擇
# ==========================================

# 如果遊戲還沒開始，顯示組牌介面
if not st.session_state.game_started:
    st.title("🛠️ 牌組構築器")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("選擇卡片")
        category = st.radio("分類", ["全部", "Pokemon", "Trainer", "Energy"], horizontal=True)
        
        if category == "全部":
            filtered_cards = db
        else:
            filtered_cards = [c for c in db if c.get('category') == category]
            
        card_names = [c['name'] for c in filtered_cards]
        choice = st.selectbox("搜尋卡片", card_names)
        
        selected_card = next((c for c in db if c['name'] == choice), None)
        
        if selected_card:
            # 顯示預覽
            if os.path.exists(selected_card['image']):
                st.image(selected_card['image'], caption=selected_card['name'])
            else:
                st.warning(f"圖片遺失: {selected_card['image']}")
                
            # 規則檢查邏輯
            current_count = sum(1 for c in st.session_state.deck if c['name'] == selected_card['name'])
            has_ace_spec = any(c.get('sub_category') == 'ACE SPEC' for c in st.session_state.deck)
            is_ace_spec = selected_card.get('sub_category') == 'ACE SPEC'
            is_basic_energy = selected_card.get('category') == 'Energy' and selected_card.get('sub_category') == 'Basic'
            
            if st.button("➕ 加入牌組"):
                if len(st.session_state.deck) >= 60:
                    st.error("牌組已滿 60 張！")
                elif is_ace_spec and has_ace_spec:
                    st.error("ACE SPEC 只能放 1 張！")
                elif not is_basic_energy and current_count >= 4:
                    st.error("同名卡最多 4 張！")
                else:
                    st.session_state.deck.append(selected_card)
                    st.success(f"已加入 {selected_card['name']}")
                    st.rerun()

    with col2:
        st.subheader(f"目前牌組 ({len(st.session_state.deck)}/60)")
        
        # 顯示牌組清單 (群組化顯示)
        if st.session_state.deck:
            # 簡單統計
            unique_cards = {}
            for card in st.session_state.deck:
                name = card['name']
                if name in unique_cards:
                    unique_cards[name]['count'] += 1
                else:
                    unique_cards[name] = {'count': 1, 'type': card.get('category', 'Unknown')}
            
            for name, data in unique_cards.items():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{name}** ({data['type']})")
                c2.write(f"x {data['count']}")
                if c3.button("移除", key=f"del_{name}"):
                    # 移除一張該名稱的卡
                    for i, c in enumerate(st.session_state.deck):
                        if c['name'] == name:
                            st.session_state.deck.pop(i)
                            break
                    st.rerun()
        else:
            st.info("牌組是空的，請從左側加入卡片。")
            
        st.markdown("---")
        if len(st.session_state.deck) == 60:
            if st.button("🚀 開始對戰", type="primary", use_container_width=True):
                start_game()
                st.rerun()
        else:
            st.progress(len(st.session_state.deck) / 60, text=f"還差 {60 - len(st.session_state.deck)} 張")

# ==========================================
# 5. 介面：戰鬥模擬器
# ==========================================
else:
    st.title("⚔️ 對戰場地")
    
    # 頂部工具列 (返回、重置)
    top_col1, top_col2, top_col3 = st.columns([1, 2, 1])
    with top_col1:
        if st.button("⬅️ 回到組牌"):
            st.session_state.game_started = False
            st.rerun()
    with top_col3:
        if st.button("🔄 重洗開始"):
            start_game()
            st.rerun()

    st.markdown("---")

    # --- 戰鬥區域 ---
    # 左側：狀態資訊 & 擲硬幣
    # 中間：戰鬥場 & 備戰區
    # 右側：牌庫 & 棄牌區 & 獎賞卡
    
    layout_left, layout_center, layout_right = st.columns([1, 3, 1])
    
    with layout_left:
        st.info("工具區")
        if st.button("🟡 擲硬幣"):
            flip_coin()
        
        if st.session_state.coin_result:
            st.write("結果：")
            if st.session_state.coin_result == "HEADS":
                if os.path.exists("coin_heads.png"):
                    st.image("coin_heads.png", width=100, caption="正面")
                else:
                    st.write("正面 (圖片遺失)")
            else:
                if os.path.exists("coin_tails.png"):
                    st.image("coin_tails.png", width=100, caption="反面")
                else:
                    st.write("反面 (圖片遺失)")
    
    with layout_center:
        st.write("#### 🔥 戰鬥場 (Active)")
        if st.session_state.active_spot:
            card = st.session_state.active_spot
            try:
                st.image(card['image'], width=180)
            except:
                st.write(card['name'])
            
            if st.button("撤退/移除", key="retreat"):
                st.session_state.discard_pile.append(card)
                st.session_state.active_spot = None
                st.rerun()
        else:
            st.empty()
            st.write("*(空)*")

        st.write("#### 🏕️ 備戰區 (Bench)")
        bench_cols = st.columns(5)
        for i in range(5):
            with bench_cols[i]:
                if i < len(st.session_state.bench):
                    card = st.session_state.bench[i]
                    try:
                        st.image(card['image'], use_container_width=True)
                    except:
                        st.write(card['name'])
                    
                    # 備戰區操作
                    if st.button("上場", key=f"active_{i}"):
                        if st.session_state.active_spot is None:
                            st.session_state.active_spot = st.session_state.bench.pop(i)
                            st.rerun()
                        else:
                            st.error("戰鬥場已有寶可夢")
                    
                    if st.button("丟棄", key=f"disc_bench_{i}"):
                        st.session_state.discard_pile.append(st.session_state.bench.pop(i))
                        st.rerun()
                else:
                    st.write("*(空)*")

    with layout_right:
        st.write("#### 資訊區")
        st.write(f"📚 牌庫: **{len(st.session_state.game_deck)}** 張")
        if st.button("抽一張卡"):
            draw_card()
            st.rerun()
            
        st.write(f"🏆 獎賞卡: **{len(st.session_state.prizes)}** 張")
        if st.button("拿取獎賞"):
            if st.session_state.prizes:
                card = st.session_state.prizes.pop(0)
                st.session_state.hand.append(card)
                st.rerun()
        
        st.write(f"🗑️ 棄牌區: **{len(st.session_state.discard_pile)}** 張")
        with st.expander("查看棄牌"):
            for c in st.session_state.discard_pile:
                st.write(c['name'])

    st.markdown("---")
    
    # --- 手牌區域 ---
    st.subheader(f"✋ 手牌 ({len(st.session_state.hand)} 張)")
    
    if st.session_state.hand:
        # 每行顯示 8 張
        cols_per_row = 8
        for i in range(0, len(st.session_state.hand), cols_per_row):
            row_cards = st.session_state.hand[i:i + cols_per_row]
            cols = st.columns(cols_per_row)
            
            for idx, card in enumerate(row_cards):
                real_idx = i + idx
                with cols[idx]:
                    try:
                        st.image(card['image'], use_container_width=True)
                    except:
                        st.write(card['name'])
                    
                    # 手牌操作選項
                    action = st.selectbox("動作", ["...", "打出/貼能", "丟棄"], key=f"act_{real_idx}", label_visibility="collapsed")
                    
                    if action == "打出/貼能":
                        # 簡單邏輯：如果是寶可夢且戰鬥場空，優先上戰鬥場，否則去備戰
                        # 這裡為了自由度，全部預設先放備戰，除非備戰滿
                        if card['category'] == 'Pokemon':
                            if st.session_state.active_spot is None:
                                st.session_state.active_spot = st.session_state.hand.pop(real_idx)
                            elif len(st.session_state.bench) < 5:
                                st.session_state.bench.append(st.session_state.hand.pop(real_idx))
                            else:
                                st.error("場地滿了")
                        else:
                            # 訓練家或能量先丟棄區 (模擬使用)，玩家自己腦補效果
                            # 或者您可以修改邏輯讓能量貼在怪獸上 (程式會變很複雜，建議先這樣)
                            st.session_state.discard_pile.append(st.session_state.hand.pop(real_idx))
                            st.toast(f"使用了 {card['name']}")
                        st.rerun()
                        
                    elif action == "丟棄":
                        st.session_state.discard_pile.append(st.session_state.hand.pop(real_idx))
                        st.rerun()