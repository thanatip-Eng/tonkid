"""
ต้นคิด — AI Critical Thinking Facilitator
Streamlit Web App สำหรับนักเรียนมัธยม
"""

import streamlit as st
import openai
import os
from datetime import datetime
from difflib import SequenceMatcher

# =====================================================
# Page Configuration
# =====================================================
st.set_page_config(
    page_title="ต้นคิด — AI Critical Thinking Facilitator",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =====================================================
# Custom CSS
# =====================================================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# Load Config Files
# =====================================================
def load_config(filepath):
    """Load text content from a config file"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filepath)
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read()

SYSTEM_PROMPT = load_config('config/system_prompt_highschool.txt')
KNOWLEDGE_BASE = load_config('config/knowledge_base.txt')
FULL_PROMPT = SYSTEM_PROMPT + "\n\n# ข้อมูลอ้างอิง\n" + KNOWLEDGE_BASE

# =====================================================
# Initialize Session State
# =====================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "sis_id" not in st.session_state:
    st.session_state.sis_id = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False
if "round_count" not in st.session_state:
    st.session_state.round_count = 0

# =====================================================
# Helper Functions
# =====================================================
def detect_echo(user_msg, last_assistant_msg):
    """ตรวจจับว่านักเรียนคัดลอกข้อความต้นคิดมาวางหรือไม่"""
    ratio = SequenceMatcher(None, user_msg.strip(), last_assistant_msg.strip()).ratio()
    if ratio > 0.5:
        return True
    for block in SequenceMatcher(None, user_msg, last_assistant_msg).get_matching_blocks():
        if block.size > 40:
            return True
    return False

def get_openai_response(messages_history):
    """Get response from OpenAI API"""
    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        api_messages = [{"role": "system", "content": FULL_PROMPT}]

        # ตรวจจับ echo: ถ้านักเรียนคัดลอกคำถามต้นคิดมาวาง ให้ inject คำเตือน
        if len(messages_history) >= 2:
            last_user = messages_history[-1]
            last_assistant = None
            for msg in reversed(messages_history[:-1]):
                if msg["role"] == "assistant":
                    last_assistant = msg
                    break
            if last_assistant and last_user["role"] == "user":
                if detect_echo(last_user["content"], last_assistant["content"]):
                    api_messages.append({
                        "role": "system",
                        "content": "[ระบบแจ้ง: ข้อความล่าสุดของนักเรียนมีเนื้อหาที่ซ้ำกับคำถามของต้นคิดอย่างมาก — อาจเป็นการคัดลอก ห้ามตอบคำถามนั้น ให้ขอให้นักเรียนตอบด้วยความคิดของตัวเอง]"
                    })

        api_messages.extend(messages_history)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=api_messages,
            temperature=0.7,
            max_tokens=1500
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {str(e)}"

def export_conversation_txt():
    """Export conversation to TXT format"""
    text_content = f"""═══════════════════════════════════════════════════════════════
ต้นคิด — บันทึกการสนทนา
Assignment #3 ฝึกทักษะการคิดวิเคราะห์กับ AI
═══════════════════════════════════════════════════════════════
ชื่อ: {st.session_state.user_name}
Email: {st.session_state.user_email}
SIS ID: {st.session_state.sis_id}
วันที่: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
═══════════════════════════════════════════════════════════════

"""
    
    for msg in st.session_state.messages:
        role_name = "นักเรียน" if msg["role"] == "user" else "ต้นคิด"
        text_content += f"【{role_name}】\n{msg['content']}\n\n---\n\n"
    
    text_content += """═══════════════════════════════════════════════════════════════
แหล่งอ้างอิง: World Economic Forum Annual Meeting 2026
https://www.weforum.org/meetings/world-economic-forum-annual-meeting-2026/
═══════════════════════════════════════════════════════════════
"""
    
    return text_content

def export_conversation_html():
    """Export conversation to HTML format"""
    html_content = f"""
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>บทสนทนากับต้นคิด - {st.session_state.user_name}</title>
    <style>
        body {{ font-family: 'Sarabun', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .message {{ padding: 15px; margin: 10px 0; border-radius: 10px; }}
        .user {{ background-color: #e3f2fd; border-left: 4px solid #2196f3; }}
        .assistant {{ background-color: #f5f5f5; border-left: 4px solid #4caf50; }}
        .meta {{ color: #666; font-size: 0.9em; margin-top: 20px; padding: 10px; background: #fafafa; border-radius: 5px; }}
        .reference {{ background-color: #fff3e0; padding: 15px; border-radius: 10px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌱 บทสนทนากับต้นคิด</h1>
        <p>Assignment #3 ฝึกทักษะการคิดวิเคราะห์กับ AI</p>
    </div>
    
    <div class="meta">
        <strong>ชื่อ:</strong> {st.session_state.user_name}<br>
        <strong>Email:</strong> {st.session_state.user_email}<br>
        <strong>SIS ID:</strong> {st.session_state.sis_id}<br>
        <strong>วันที่:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
    
    <h2>บทสนทนา</h2>
"""
    
    for msg in st.session_state.messages:
        role_class = "user" if msg["role"] == "user" else "assistant"
        role_name = "นักเรียน" if msg["role"] == "user" else "ต้นคิด"
        html_content += f"""
    <div class="message {role_class}">
        <strong>{role_name}:</strong><br>
        {msg["content"].replace(chr(10), "<br>")}
    </div>
"""
    
    html_content += """
    <div class="reference">
        <strong>📚 แหล่งอ้างอิง:</strong><br>
        World Economic Forum Annual Meeting 2026<br>
        <a href="https://www.weforum.org/meetings/world-economic-forum-annual-meeting-2026/" target="_blank">
            https://www.weforum.org/meetings/world-economic-forum-annual-meeting-2026/
        </a>
    </div>
</body>
</html>
"""
    return html_content

def simple_login():
    """Simple email-based login for high school students"""
    st.markdown("""
    <div class="main-header">
        <h1>🌱 ต้นคิด</h1>
        <p>AI Critical Thinking Facilitator</p>
        <p style="font-size: 0.9em;">สำหรับนักเรียนมัธยม</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>👋 ยินดีต้อนรับ!</h3>
        <p>ต้นคิดคือ AI ที่จะช่วยฝึกทักษะการคิดวิเคราะห์ (Critical Thinking) ของเธอ 
        ผ่านการสนทนาเรื่องเทรนด์โลกจาก World Economic Forum Annual Meeting 2026</p>
        <p>📚 <a href="https://www.weforum.org/meetings/world-economic-forum-annual-meeting-2026/" target="_blank">อ่านเพิ่มเติมเกี่ยวกับ WEF 2026</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.subheader("🔐 เข้าสู่ระบบ")
        
        email = st.text_input(
            "Email", 
            placeholder="example@gmail.com",
            help="ใช้ Gmail หรือ Email ใดก็ได้"
        )
        name = st.text_input(
            "ชื่อ-นามสกุล (ภาษาไทย)", 
            placeholder="สมชาย ใจดี"
        )
        sis_id = st.text_input(
            "SIS ID (รหัสในระบบ Canvas)",
            placeholder="เช่น 12345",
            help="รหัส SIS ID ของเธอในระบบ Canvas"
        )
        
        submitted = st.form_submit_button("🚀 เริ่มต้นใช้งาน", use_container_width=True)
        
        if submitted:
            if not email or not name or not sis_id:
                st.error("กรุณากรอกข้อมูลให้ครบทุกช่อง")
            elif "@" not in email:
                st.error("กรุณากรอก Email ที่ถูกต้อง")
            else:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.session_state.sis_id = sis_id
                st.rerun()

def main_chat():
    """Main chat interface"""
    st.markdown("""
    <div class="main-header">
        <h1>🌱 ต้นคิด</h1>
        <p>AI Critical Thinking Facilitator</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.caption(f"📧 {st.session_state.user_email}")
        st.caption(f"🆔 SIS ID: {st.session_state.sis_id}")
        st.divider()
        
        # Download buttons
        if st.session_state.messages:
            st.markdown("### 📥 ดาวน์โหลดบทสนทนา")
            
            # TXT Download (Primary)
            txt_export = export_conversation_txt()
            st.download_button(
                label="💾 ดาวน์โหลด (.txt) — ใช้ส่งงาน",
                data=txt_export,
                file_name=f"tonkid_{st.session_state.sis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary"
            )
            
            # HTML Download (Alternative)
            html_export = export_conversation_html()
            st.download_button(
                label="🌐 ดาวน์โหลด (.html) — อ่านสวย",
                data=html_export,
                file_name=f"tonkid_{st.session_state.sis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )
            
            st.caption("⚠️ กดดาวน์โหลด .txt เพื่อส่งงาน")
        
        st.divider()
        
        # Reset button
        if st.button("🔄 เริ่มบทสนทนาใหม่", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_started = False
            st.session_state.round_count = 0
            st.rerun()
        
        # Logout button
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = ""
            st.session_state.user_name = ""
            st.session_state.sis_id = ""
            st.session_state.messages = []
            st.session_state.conversation_started = False
            st.rerun()
        
        st.divider()
        st.markdown("""
        <div style="font-size: 0.8em; color: #666;">
            <p>📚 <a href="https://www.weforum.org/meetings/world-economic-forum-annual-meeting-2026/" target="_blank">แหล่งอ้างอิง WEF 2026</a></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Start conversation
    if not st.session_state.conversation_started:
        with st.spinner("ต้นคิดกำลังทักทาย..."):
            first_message = get_openai_response([])
            st.session_state.messages.append({
                "role": "assistant",
                "content": first_message
            })
            st.session_state.conversation_started = True
            st.rerun()
    
    # Display messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="🌱"):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("พิมพ์ข้อความของเธอที่นี่..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.round_count += 1
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        with st.chat_message("assistant", avatar="🌱"):
            with st.spinner("ต้นคิดกำลังคิด..."):
                api_messages = [{"role": m["role"], "content": m["content"]} 
                               for m in st.session_state.messages]
                response = get_openai_response(api_messages)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# =====================================================
# Main App
# =====================================================
def main():
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("⚠️ กรุณาตั้งค่า OPENAI_API_KEY ใน Streamlit Secrets")
        st.info("ไปที่ Settings → Secrets แล้วเพิ่ม OPENAI_API_KEY")
        st.stop()
    
    if not st.session_state.authenticated:
        simple_login()
    else:
        main_chat()

if __name__ == "__main__":
    main()
