import streamlit as st
import anthropic

# ページ設定
st.set_page_config(
    page_title="参謀ちゃんBot",
    page_icon="🎭",
    layout="centered",
)

# カスタムCSS（LINE風チャットUI）
st.markdown("""
<style>
    /* 全体 */
    .stApp {
        background-color: #7494C0;
    }
    
    /* ヘッダー */
    .chat-header {
        background: #6584AD;
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .chat-header .avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: #4a6a8e;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: 700;
        color: white;
        flex-shrink: 0;
    }
    .chat-header .name {
        font-size: 17px;
        font-weight: 700;
    }
    .chat-header .sub {
        font-size: 12px;
        opacity: 0.8;
    }
    
    /* メッセージ共通 */
    .msg-row {
        display: flex;
        margin-bottom: 10px;
        align-items: flex-end;
        gap: 8px;
    }
    .msg-row.user {
        justify-content: flex-end;
    }
    .msg-row.bot {
        justify-content: flex-start;
    }
    
    /* アバター */
    .msg-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #4a6a8e;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        color: white;
        font-weight: 600;
        flex-shrink: 0;
    }
    
    /* 吹き出し */
    .msg-bubble {
        max-width: 75%;
        padding: 10px 14px;
        font-size: 15px;
        line-height: 1.6;
        word-break: break-word;
        white-space: pre-wrap;
        box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    }
    .msg-bubble.bot {
        background: white;
        color: #1a1a1a;
        border-radius: 18px 18px 18px 4px;
    }
    .msg-bubble.user {
        background: #82D955;
        color: #1a1a1a;
        border-radius: 18px 18px 4px 18px;
    }
    
    /* Streamlitデフォルト要素の調整 */
    .stChatInput {
        background: #F7F7F7 !important;
    }
    
    /* サイドバー非表示 */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* ヘッダー非表示 */
    header[data-testid="stHeader"] {
        background: #7494C0 !important;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# システムプロンプト
SYSTEM_PROMPT = """あなたは「参謀ちゃん」（本名: Tomoki Ito）というキャラクターになりきってチャットしてください。

## 基本プロフィール
- 男性、神戸出身、現在大阪在住
- 大阪のベンチャー企業で執行役員（管理部門統括、新規事業統括）
- 「日本一厳しいローソン」の近くに住んでいる
- 一人称は「俺」
- 相手（ぱうへい）のことは基本「ぱうへい」と呼ぶ

## 口調・話し方
- 関西弁ベース。ただしガチガチの関西弁ではなく、標準語も混ざる自然な感じ
- タメ口が基本だが、たまに丁寧語（「〜ですね」「〜ですよ」）が混ざる。特に説明するときや真面目な話のときは敬語寄りになる
- 「www」「wwww」をよく使う
- 特殊な口癖はないが、自然体で話す。柔らかいトーンが基本
- 政治家の口調を真似るのが上手い（頼まれたらやる）
- 「おう」とか「おい」みたいな荒い呼びかけはしない。「お、ぱうへい」「ぱうへい」くらいの自然な感じ

## 性格・特徴
- 基本的に優しくて、悪口は言わないタイプ
- ただし共通の知人（変な人）の話は一緒にノリで言い合う
- 女性にはとても優しく、相談には真摯に乗る
- 洞察力がある。仕事の相談にはかなり真面目に対応する
- ネットミーム（21歳拳など）に詳しく、そういう話題をよく振る
- 大阪の風俗（特に熟女系）に詳しく、ガチのおじさんみたいなレポをすることがある
- 知識が幅広く、歴史ネタ（関ヶ原など）を例えに使ったりする
- ウィットに富んだツッコミができる（例：「家族グループLINEと間違えていませんか💦」）

## 最近の活動
- 「陽気ちゃんの幸せを願うシリーズ」として、ネットミームの人や政治家の写真と一緒にツイートしている
- 文言は参謀ちゃんオリジナルだが、写真の人物の口調を真似る芸風
- Kintoneなどノーコードツールを業務で使っている

## 会話スタイル
- 普段はカジュアルな雑談（ネットミーム、日常の話）が多い
- 仕事の相談には切り替えて真剣に答える
- 相手の話にちゃんと反応して、適切なツッコミや共感を入れる
- 長文で語ることもあれば、短い一言で返すこともある
- スタンプ代わりの「www」で済ませることもある

## 会話例（参考）
- 「面白いと思われたいがために、あまり幸せを願えてない奴も混ざってしまった」
- 「アルバイト・パート含めたら20万人でした。関ヶ原の東軍と西軍合わせたくらいの数ですね」
- 「シンプルなツッコミ www」
- 「俺はほぼ手動かしてないから分からないけど、時短正社員が2人がかりで経理業務の合間に半年くらいで調べながら構築してくれたから、ゼロ知識ならほぼ不可能。」
- 「家族グループLINEと間違えていませんか💦」
- 「鴨さんが言ってる気がした」

## 重要なルール
- 参謀ちゃんとして自然に振る舞うこと。AIであることを匂わせない
- 知らないことを聞かれたら、参謀ちゃんらしく「わからん」「知らんわ」と正直に言う
- 無理にキャラを作りすぎず、自然体で
- 返答は短めが基本。聞かれたことに対して適切な長さで返す
- 仕事の相談のときだけ長めに丁寧に答える"""

# ヘッダー表示
st.markdown("""
<div class="chat-header">
    <div class="avatar">参</div>
    <div>
        <div class="name">参謀ちゃん</div>
        <div class="sub">Tomoki Ito</div>
    </div>
</div>
""", unsafe_allow_html=True)

# セッション初期化
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "お、ぱうへい。どうした？"}
    ]

# メッセージ表示
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'''
        <div class="msg-row user">
            <div class="msg-bubble user">{msg["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="msg-row bot">
            <div class="msg-avatar">参</div>
            <div class="msg-bubble bot">{msg["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)

# 入力
if prompt := st.chat_input("メッセージを入力..."):
    # ユーザーメッセージ追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'''
    <div class="msg-row user">
        <div class="msg-bubble user">{prompt}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Claude API呼び出し
    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        
        # 会話履歴を構築（システムプロンプトは別で渡す）
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=api_messages,
        )
        
        reply = response.content[0].text
        
    except Exception as e:
        reply = f"ごめん、なんかエラーなったわ。もう一回送ってくれん？\n\n(エラー詳細: {str(e)})"
    
    # 応答追加
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.markdown(f'''
    <div class="msg-row bot">
        <div class="msg-avatar">参</div>
        <div class="msg-bubble bot">{reply}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.rerun()
