import httpx

import streamlit as st

st.title('Wikiチャット')

# 会話履歴の保持と画面への再描画
if "messages" not in st.session_state:
  st.session_state.messages = []

for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])

# ユーザー入力 ➔ 検索 ➔ AI回答の実行
if user_input := st.chat_input("質問してください..."):
  # ユーザーの発言を表示
  with st.chat_message("user"):
    st.markdown(user_input)
  st.session_state.messages.append({"role": "user", "content": user_input})
  # AIの回答を表示
  with st.chat_message("assistant"):
    try:
      def stream_chat_response():
        with httpx.Client() as client:
          with client.stream("POST", "http://backend:3000/api/chat", json={"question": user_input}, timeout=305.0) as res:
            res.raise_for_status()
            for chunk in res.iter_text():
              yield chunk
      ai_response = st.write_stream(stream_chat_response())
      st.session_state.messages.append({"role": "assistant", "content": ai_response})
    except httpx.ReadTimeout:
      st.error("タイムアウトしました。")
    except Exception as e:
      st.error(f"エラーが発生しました: {e}")
    
