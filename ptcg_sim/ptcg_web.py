import streamlit as st
import random
import uuid
import time
import os

st.set_page_config(page_title="PTCG 完整數據戰鬥模擬", layout="wide", page_icon="📖")

# ==========================================
# 1. 工具函式：能量圖示與檔名搜尋
# ==========================================

def get_energy_icon(etype):
    """將文字屬性轉換為圖示"""
    icons = {
        "Darkness": "🌑", "Water": "💧", "Grass": "🌿", 
        "Psychic": "🔮", "Fighting": "👊", "Fire": "🔥",
        "Lightning": "⚡", "Metal": "⚙️", "Dragon": "🐉",
        "Colorless": "⚪", "Any": "⚪"
    }
    return icons.get(etype, "⚪")

def get_smart_image_path(base_name):
    """自動搜尋各種大小寫副檔名"""
    exts = [".jpg", ".JPG", ".png", ".PNG", ".jpeg", ".JPEG"]
    if os.path.exists(base_name): return base_name
    for ext in exts:
        if os.path.exists(f"{base_name}{ext}"): return f"{base_name}{ext}"
    return None

# ==========================================
# 2. 詳細卡片資料庫 (在此輸入你的卡片數值)
# ==========================================

CARD_DB = {
    # ------ 寶可夢 (Pokemon) ------
    "瑪俐的長毛巨魔 ex": {
        "cat": "Pokemon", "stage": "Stage 2", "type": "Darkness", "hp": 320,
        "img_base": "grimmsnarl_ex",
        "ability": None,
        "moves": [
            {"n": "暗影子彈", "cost": ["Darkness"], "d": 180, "eff": "對手的1隻備戰寶可夢也受到60點傷害。"},
            {"n": "極巨毛髮", "cost": ["Darkness", "Darkness", "Colorless"], "d": 240, "eff": "下個對手回合，這隻寶可夢受到的傷害「-30」。"}
        ],
        "weakness": "Grass", "retreat": 2
    },
    "瑪俐的詐唬魔": {
        "cat": "Pokemon", "stage": "Stage 1", "type": "Darkness", "hp": 100,
        "img_base": "morgrem",
        "moves": [
            {"n": "推擊", "cost": ["Darkness"], "d": 40, "eff": "擲一次硬幣若為正面，增加20點傷害。"}
        ],
        "weakness": "Grass", "retreat": 1
    },
    "瑪俐的搗蛋小妖": {
        "cat": "Pokemon", "stage": "Basic", "type": "Darkness", "hp": 70,
        "img_base": "impidimp",
        "moves": [
            {"n": "偷盜", "cost": ["Colorless"], "d": 0, "eff": "查看對手手牌，選擇其中1張丟棄。"},
            {"n": "推擊", "cost": ["Darkness", "Colorless"], "d": 20, "eff": ""}
        ],
        "weakness": "Grass", "retreat": 1
    },
    "願增猿": {
        "cat": "Pokemon", "stage": "Basic", "type": "Psychic", "hp": 110,
        "img_base": "munkidori",
        "ability": {"n": "腎上腺素腦", "desc": "若這隻寶可夢身上附有惡能量，則這隻寶可夢撤退所需的能量全部消除。"},
        "moves": [
            {"n": "精神歪曲", "cost": ["Psychic", "Colorless"], "d": 60, "eff": "對手的戰鬥寶可夢混亂。"}
        ],
        "weakness": "Darkness", "retreat": 1
    },
    "雪妖女": {
        "cat": "Pokemon", "stage": "Stage 1", "type": "Water", "hp": 90,
        "img_base": "froslass",
        "ability": {"n": "凍結幕簾", "desc": "只要這隻寶可夢在場上，對手無法從手牌使出物品卡。"},
        "moves": [
            {"n": "冰霜粉碎", "cost": ["Water", "Colorless"], "d": 60, "eff": ""}
        ],
        "weakness": "Metal", "retreat": 1
    },
    "雪童子": {
        "cat": "Pokemon", "stage": "Basic", "type": "Water", "hp": 60,
        "img_base": "snorunt",
        "moves": [{"n": "寒意", "cost": ["Water"], "d": 10, "eff": "對手下個回合無法撤退。"}],
        "weakness": "Metal", "retreat": 1
    },
    "月月熊 赫月 ex": {
        "cat": "Pokemon", "stage": "Basic", "type": "Colorless", "hp": 260,
        "img_base": "bloodmoon_ursaluna",
        "ability": {"n": "老練技藝", "desc": "這隻寶可夢使用招式所需的無能量，減少對手已經拿取的獎賞卡的張數數量。"},
        "moves": [
            {"n": "血月", "cost": ["Colorless", "Colorless", "Colorless", "Colorless", "Colorless"], "d": 240, "eff": "下個自己的回合，這隻寶可夢無法使用招式。"}
        ],
        "weakness": "Fighting", "retreat": 3
    },
    "含羞苞": {
        "cat": "Pokemon", "stage": "Basic", "type": "Grass", "hp": 30,
        "img_base": "budew",
        "moves": [{"n": "進化花粉", "cost": [], "d": 0, "eff": "從牌庫找一張進化卡進化。"}],
        "weakness": "Fire", "retreat": 0
    },
    "可達鴨": {
        "cat": "Pokemon", "stage": "Basic", "type": "Water", "hp": 70,
        "img_base": "psyduck",
        "moves": [{"n": "頭痛", "cost": ["Colorless"], "d": 10, "eff": "對手下回合不能使用訓練家卡。"}],
        "weakness": "Lightning", "retreat": 1
    },
    "米立龍": {
        "cat": "Pokemon", "stage": "Basic", "type": "Dragon", "hp": 70,
        "img_base": "tatsugiri",
        "ability": {"n": "藏身", "desc": "只要這隻寶可夢在備戰區，不會受到招式的傷害。"},
        "moves": [{"n": "噴水", "cost": ["Water", "Fighting"], "d": 50, "eff": ""}],
        "weakness": None, "retreat": 1
    },

    # ------ 訓練家 (Trainer) ------
    "寶可平板": {"cat": "Trainer", "sub": "物品", "img_base": "poke_tablet", "desc": "翻轉自己的1張獎賞卡，若為寶可夢則加入手牌。"},
    "好友寶芬": {"cat": "Trainer", "sub": "物品", "img_base": "buddy_poffin", "desc": "從自己的牌庫選擇最多2張HP「70」以下的基礎寶可夢，放置於備戰區。"},
    "夜間擔架": {"cat": "Trainer", "sub": "物品", "img_base": "night_stretcher", "desc": "從自己的棄牌區選擇1張寶可夢卡或者基本能量卡，在給對手看過後加入手牌。"},
    "神奇糖果": {"cat": "Trainer", "sub": "物品", "img_base": "rare_candy", "desc": "選擇自己的1隻場上的基礎寶可夢，從手牌使出1張由那隻寶可夢進化而來的2階進化寶可夢卡，放置於身上完成進化。"},
    "高級球": {"cat": "Trainer", "sub": "物品", "img_base": "ultra_ball", "desc": "必須將自己的2張手牌丟棄才可使用。從自己的牌庫選擇1張寶可夢卡，在給對手看過後加入手牌。"},
    "能量轉移": {"cat": "Trainer", "sub": "物品", "img_base": "energy_switch", "desc": "選擇1個自己的場上寶可夢身上附加的基本能量，改附於自己的其他寶可夢身上。"},
    "不公印章": {"cat": "Trainer", "sub": "ACE SPEC", "img_base": "unfair_stamp", "desc": "若在上個對手的回合，自己的寶可夢氣絕了才可使用。雙方玩家將手牌全部放回牌庫洗牌。那之後，自己從牌庫抽出5張，對手抽出2張。"},
    "氣球": {"cat": "Trainer", "sub": "道具", "img_base": "air_balloon", "desc": "附有這張卡的寶可夢，撤退所需的能量減少2個。"},
    "莉莉艾的決意": {"cat": "Trainer", "sub": "支援者", "img_base": "lillie_resolve", "desc": "自己的手牌有6張為止。若在上個對手的回合，自己的寶可夢氣絕了，則改為抽到8張為止。"},
    "火箭隊的拉姆達": {"cat": "Trainer", "sub": "支援者", "img_base": "rocket_lambda", "desc": "從牌庫選擇最多2張「火箭隊」的卡片加入手牌。"},
    "老大的指令": {"cat": "Trainer", "sub": "支援者", "img_base": "boss_orders", "desc": "選擇1隻對手的備戰寶可夢，與戰鬥寶可夢互換。"},
    "丹瑜": {"cat": "Trainer", "sub": "支援者", "img_base": "carmine", "desc": "若為先攻玩家的最初回合也可使用。將自己的手牌全部丟棄，從牌庫抽出5張卡。"},
    "尖釘鎮道館": {"cat": "Trainer", "sub": "競技場", "img_base": "spikemuth_gym", "desc": "雙方玩家在每次自己的回合結束時，若將自己的戰鬥寶可夢換到備戰區，則在那隻寶可夢身上放置2個傷害指示物。"},

    # ------ 能量 (Energy) ------
    "基本惡能量": {"cat": "Energy", "sub": "基本", "img_base": "dark_energy", "desc": "提供1個惡能量。"}
}

# 牌組定義
DECK_LIST = {
    "瑪俐的長毛巨魔 ex": 2, "瑪俐的詐唬魔": 2, "瑪俐的搗蛋小妖": 3, "願增猿": 4,
    "含羞苞": 1, "可達鴨": 1, "雪童子": 2, "雪妖女": 2, "月月熊 赫月 ex": 1,
    "米立龍": 1, "寶可平板": 3, "好友寶芬": 3, "夜間擔架": 3, "神奇糖果": 2,
    "能量轉移": 1, "高級球": 1, "不公印章": 1, "氣球": 1, "莉莉艾的決意": 4,
    "老大的指令": 3, "火箭隊的拉姆達": 4, "丹瑜": 3, "尖釘鎮道館": 3, "基本惡能量": 9
}

# ==========================================
# 3. 核心邏輯 (加入更多狀態變數)
# ==========================================
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

def init_game():
    def build():
        d = []
        for n, c in DECK_LIST.items():
            for _ in range(c): 
                inst = create_card_instance(n)
                if inst: d.append(inst)
        random.shuffle(d)
        return d
    
    st.session_state.game = {
        "phase": "setup",
        "log": ["遊戲開始，請擲硬幣。"],
        "player": {"deck": build(), "hand": [], "active": None, "bench": [], "discard": [], "prizes": []},
        "opponent": {"deck": build(), "hand": [], "active": None, "bench": [], "discard": [], "prizes": []}
    }
    # 抽牌與設置
    for who in ['player', 'opponent']:
        for _ in range(7): st.session_state.game[who]['hand'].append(st.session_state.game[who]['deck'].pop(0))
        for _ in range(6): st.session_state.game[who]['prizes'].append(st.session_state.game[who]['deck'].pop(0))

def render_rich_card(card, key_id, width=150, actions=None):
    """
    v8.0 核心顯示函式：顯示完整資料
    """
    if not card: return

    # 1. 圖片
    img_path = get_smart_image_path(card.get('img_base', ''))
    if img_path:
        st.image(img_path, width=width)
    else:
        st.error(f"缺圖: {card['name']}")

    # 2. 寶可夢詳細數據 (使用 Expander 收納，避免畫面太長)
    if card['cat'] == 'Pokemon':
        # 血量條
        hp_now = card['hp'] - card.get('damage', 0)
        hp_color = "green" if hp_now > card['hp']/2 else "red"
        st.markdown(f"**HP :{hp_color}[{hp_now}/{card['hp']}]**")
        
        # 貼能顯示
        if card['attached_energy']:
            ens = "".join([get_energy_icon(e.get('type', 'Darkness')) for e in card['attached_energy']])
            st.caption(f"已填能: {ens}")

        # 詳細資料區 (點開看招式與效果)
        with st.expander(f"📊 詳細資料 & 招式"):
            st.caption(f"**屬性**: {get_energy_icon(card['type'])} | **弱點**: {get_energy_icon(card['weakness'])} | **撤退**: {card['retreat']}⚪")
            
            # 特性
            if card.get('ability'):
                st.markdown(f"**🔷 特性：{card['ability']['n']}**")
                st.caption(card['ability']['desc'])
                st.divider()

            # 招式
            for move in card.get('moves', []):
                cost_icons = "".join([get_energy_icon(c) for c in move['cost']])
                st.markdown(f"**{cost_icons} {move['n']} {move['d']}**")
                if move['eff']:
                    st.caption(f"*{move['eff']}*")
                st.divider()
    
    # 3. 訓練家/能量詳細數據
    else:
        with st.expander("📄 卡片效果"):
            st.write(card.get('desc', '無敘述'))

    # 4. 互動按鈕
    if actions:
        act = st.selectbox("動作", actions, key=f"act_{key_id}_{card['id']}", label_visibility="collapsed")
        if act and act != "選擇": return act
    return None

# ==========================================
# 4. 介面流程
# ==========================================
if 'game' not in st.session_state: init_game()
game = st.session_state.game
pl = game['player']
op = game['opponent']

# 側邊欄：搜尋牌庫功能
with st.sidebar:
    st.title("🧰 工具箱")
    if st.button("🔄 重置遊戲"):
        init_game()
        st.rerun()
    
    st.divider()
    st.subheader("🔍 搜尋牌庫")
    if st.button("查看牌庫並拿牌"):
        st.session_state.searching = True
    
    if st.session_state.get('searching'):
        st.write("--- 牌庫清單 ---")
        # 顯示牌庫中所有卡片，點擊可加入手牌
        for i, card in enumerate(pl['deck']):
            if st.button(f"拿取: {card['name']}", key=f"search_{i}"):
                pl['hand'].append(pl['deck'].pop(i))
                game['log'].append(f"你從牌庫搜尋了 {card['name']}")
                st.session_state.searching = False
                st.rerun()
        if st.button("關閉搜尋"):
            st.session_state.searching = False
            st.rerun()

# 遊戲畫面
if game['phase'] == 'setup':
    st.title("🪙 擲硬幣階段")
    if st.button("擲硬幣"):
        res = random.choice(["heads", "tails"])
        game['log'].append(f"結果: {res}")
        st.image(get_smart_image_path(f"coin_{res}"), width=150) if get_smart_image_path(f"coin_{res}") else st.info(res)
        time.sleep(1)
        game['phase'] = 'battle'
        st.rerun()

elif game['phase'] == 'battle':
    # 對手區
    st.subheader("🤖 對手")
    c1, c2, c3 = st.columns([2,5,2])
    with c1: 
        st.write(f"🏆 獎賞: {len(op['prizes'])}")
        st.write(f"📚 牌庫: {len(op['deck'])}")
        st.write(f"✋ 手牌: {len(op['hand'])}")
    with c2: # 備戰
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                if i < len(op['bench']): render_rich_card(op['bench'][i], f"ob_{i}", 100)
    with c3: # 戰鬥
        if op['active']: render_rich_card(op['active'], "oa", 120)
        else: st.info("空")

    st.markdown("---")

    # 玩家區
    st.subheader("👤 你的回合")
    c1, c2, c3 = st.columns([2,5,2])
    
    # 戰鬥場
    with c1:
        if pl['active']:
            render_rich_card(pl['active'], "pa", 150)
            
            # 攻擊選單
            moves = pl['active'].get('moves', [])
            move_names = [f"{m['n']} ({m['d']})" for m in moves]
            atk_choice = st.selectbox("選擇招式", move_names, key="atk_sel")
            
            c_a, c_b = st.columns(2)
            if c_a.button("⚔️ 攻擊"):
                dmg = 0
                for m in moves:
                    if m['n'] in atk_choice: dmg = m['d']
                
                if op['active']:
                    op['active']['damage'] += dmg
                    game['log'].append(f"你造成 {dmg} 傷害")
                    if op['active']['damage'] >= op['active']['hp']:
                        game['log'].append("對手氣絕！")
                        op['discard'].append(op['active'])
                        op['active'] = None
                        if pl['prizes']: pl['hand'].append(pl['prizes'].pop(0))
                st.rerun()
                
            if c_b.button("🏳️ 撤退"):
                pl['discard'].append(pl['active'])
                pl['active'] = None
                st.rerun()
        else:
            st.warning("請派人上場")
            
    # 備戰區
    with c2:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                if i < len(pl['bench']):
                    if st.button("⬆", key=f"up_{i}"):
                        if not pl['active']:
                            pl['active'] = pl['bench'].pop(i)
                            st.rerun()
                    render_rich_card(pl['bench'][i], f"pb_{i}", 100)

    # 資源區
    with c3:
        if st.button("📚 抽牌"):
            if pl['deck']: pl['hand'].append(pl['deck'].pop(0))
            st.rerun()
        st.write(f"棄牌區: {len(pl['discard'])}")
        if pl['prizes'] and st.button("🏆 拿獎賞"):
            pl['hand'].append(pl['prizes'].pop(0))
            st.rerun()

    # 手牌區
    st.markdown("---")
    st.write("✋ 手牌")
    if pl['hand']:
        rows = [pl['hand'][i:i+6] for i in range(0, len(pl['hand']), 6)]
        for r_idx, row in enumerate(rows):
            cols = st.columns(6)
            for c_idx, card in enumerate(row):
                with cols[c_idx]:
                    # 動作邏輯
                    opts = ["選擇", "丟棄"]
                    if card['cat'] == 'Pokemon': opts += ["打到備戰", "打到戰鬥"]
                    if card['cat'] == 'Energy': opts += ["貼給戰鬥"]
                    if card['cat'] == 'Trainer': opts += ["使用"]
                    
                    act = render_rich_card(card, f"h_{r_idx}_{c_idx}", 110, opts)
                    
                    idx = r_idx * 6 + c_idx
                    if act == "打到備戰": pl['bench'].append(pl['hand'].pop(idx)); st.rerun()
                    elif act == "打到戰鬥": pl['active'] = pl['hand'].pop(idx); st.rerun()
                    elif act == "貼給戰鬥" and pl['active']: pl['active']['attached_energy'].append(card); pl['hand'].pop(idx); st.rerun()
                    elif act == "使用" or act == "丟棄": pl['discard'].append(pl['hand'].pop(idx)); st.rerun()
    
    st.markdown("---")
    if st.button("🛑 結束回合"):
        # AI 簡易回合
        game['log'].append("--- 對手回合 ---")
        if op['deck']: op['hand'].append(op['deck'].pop(0))
        if not op['active']:
             pks = [c for c in op['hand'] if c['cat']=='Pokemon']
             if pks: op['active']=pks[0]; op['hand'].remove(pks[0])
        if op['active'] and pl['active']:
            dmg = op['active']['moves'][0]['d'] if op['active']['moves'] else 20
            pl['active']['damage'] += dmg
            game['log'].append(f"對手攻擊造成 {dmg}")
            if pl['active']['damage'] >= pl['active']['hp']:
                pl['discard'].append(pl['active'])
                pl['active'] = None
                if op['prizes']: op['hand'].append(op['prizes'].pop(0))
        st.rerun()