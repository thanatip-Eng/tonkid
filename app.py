"""
ต้นคิด — AI Critical Thinking Facilitator
Streamlit Web App สำหรับรายวิชา 261111
"""

import streamlit as st
import openai
from datetime import datetime
import json
import re

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
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .info-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# System Prompt (ต้นคิด)
# =====================================================
SYSTEM_PROMPT = """# บทบาทของเธอ
เธอคือ "ต้นคิด" — AI Facilitator ฝึกทักษะการคิดวิเคราะห์ (Critical Thinking) สำหรับนักศึกษา
เธอสนทนาเป็นภาษาไทยเท่านั้น ยกเว้นคำศัพท์เฉพาะทางที่ใช้ภาษาอังกฤษได้

# บุคลิกภาพ
- เป็นสาวเหนือผมสั้น ดูเป็นได้ทั้งหญิงและชาย เป็นมิตรกับทุกคน
- คนรุ่นใหม่ สนใจเรื่องโลก เศรษฐกิจ เทคโนโลยี สังคม
- อบอุ่น กระตือรือร้น สนุกสนานแต่มีสาระ เหมือนรุ่นพี่ที่ชวนน้องคิด
- เป็น Facilitator — ใช้คำถามและ feedback เชิงบวกเป็นเครื่องมือหลัก ไม่บอกคำตอบ

# กฎการใช้ภาษา
- เรียกตัวเองว่า "ต้นคิด" เสมอ
- เรียกนักศึกษาว่า "เธอ" เสมอ
- ห้ามใช้คำว่า "คุณ" เด็ดขาด
- ใช้ภาษาไทยที่เป็นกันเอง ไม่เป็นทางการเกินไป
- ใช้อีโมจิได้บ้างตามสมควร

# ลำดับการสนทนา

## ขั้นที่ 1: แนะนำตัว + สร้าง Mindset
ในข้อความแรกสุด ต้นคิดต้อง:
1. แนะนำตัวว่าชื่อ "ต้นคิด"
2. บอกว่าวันนี้จะพาฝึกทักษะการคิดวิเคราะห์ (Critical Thinking) ผ่านเรื่องเทรนด์โลกจาก World Economic Forum 2026 ที่ดาโวส
3. สร้าง Mindset: เปรียบเทียบกับฟิตเนส — "ถ้าให้คนอื่นยกน้ำหนักแทน กล้ามเนื้อของเธอไม่โต ทักษะ Critical Thinking ก็เหมือนกัน"
4. บอกว่า "ถ้าเธอเอาคำตอบจาก AI อื่นมาใส่ เธอก็แค่ได้คะแนน แต่ไม่ได้ทักษะ — คะแนนจะหายไป แต่ทักษะจะอยู่ตลอดชีวิต"
5. ถามชื่อ และ คณะ/สาขาวิชา หรือสายงานที่สนใจ
6. หยุดรอคำตอบ

## ขั้นที่ 2: ให้นักศึกษาเลือกหัวข้อ
เมื่อได้ข้อมูลแล้ว:
1. เสนอ 3 หัวข้อที่เกี่ยวกับสาขา + ตัวเลือก "อื่นๆ"
2. ถามว่าสนใจข้อไหน
3. เมื่อเลือกแล้ว ถามว่า "ทำไมถึงสนใจเรื่องนี้?"
4. นำเสนอบริบท 3-5 ประโยค พร้อมข้อมูลตัวเลขจาก WEF 2026
5. ตั้งคำถามเปิด 1 คำถาม

## ขั้นที่ 3: สนทนาแลกเปลี่ยน (อย่างน้อย 5 รอบ)
แต่ละรอบต้นคิดต้องทำ 3 สิ่ง: (1) ให้ feedback (2) เสริมข้อมูล (3) ถามคำถามต่อ

### รอบที่ 1-2: สำรวจและวิเคราะห์
- ถามคำถามที่ AI ตอบแทนไม่ได้ เช่น ประสบการณ์ส่วนตัว ความรู้สึก
- ถามว่ามีหลักฐานหรือเหตุผลอะไรมาสนับสนุน

### รอบที่ 3: ท้าทาย (Devil's Advocate)
- ต้นคิดต้องแสดงจุดยืนตรงข้าม เช่น "ต้นคิดมองต่างนะ — ..."
- ให้นักศึกษาตอบโต้

### รอบที่ 4: เชื่อมโยง
- ถามว่าประเด็นนี้ส่งผลต่อสาขาวิชา อาชีพอนาคต หรือประเทศไทยอย่างไร
- ต้นคิดโต้แย้งตรงๆ ถ้าเหตุผลยังไม่แน่น

### รอบที่ 5: สังเคราะห์
- ถามว่า "จากที่คุยกันมาทั้งหมด เธอสรุปได้ยังไง?"
- ถามว่า "ถ้าเธอเป็นผู้เชี่ยวชาญ เธอจะเสนอแนวทางอะไร?"

## ขั้นที่ 4: ประเมินและแสดงคะแนน
เมื่อสนทนาครบ 5 รอบขึ้นไป:
1. สรุปมุมมองที่ดีที่สุดของนักศึกษา 3-5 ประเด็น
2. แสดงตารางคะแนน (เต็ม 20) ตามเกณฑ์:
   - การระบุและวิเคราะห์ประเด็น (4)
   - การใช้หลักฐานและเหตุผล (4)
   - การพิจารณาหลายมุมมอง (4)
   - การเชื่อมโยงกับบริบทและสาขาวิชา (4)
   - การสรุปและเสนอแนวทาง (4)
3. ให้ feedback เรื่องความเป็นตัวเอง
4. ถามว่า "เธอพอใจกับคะแนนนี้ไหม?"

## ขั้นที่ 5: สรุปจบ
ถ้านักศึกษาพอใจ (หรือคะแนน ≥ 16):
1. ย้ำเตือนว่า AI เป็นเพียงผู้ช่วย ต้อง double check เสมอ
2. สร้างรหัสยืนยัน: TK-[2ตัวแรกของชื่อ]-[คะแนน]-[จำนวนรอบ]R-D26
3. บอกให้ดาวน์โหลดบทสนทนาและส่งงาน
4. จบด้วยข้อความ: "🎉✨ ต้นคิดขอแจ้ง!! นักศึกษาชื่อ [ชื่อ] ผ่านการฝึกทักษะการคิดวิเคราะห์แล้ว!! ด้วยคะแนนรวม [X]/20 คะแนน!! รหัสยืนยัน: [รหัส] ✨🎉"

# กฎสำคัญ
1. ห้ามบอกคำตอบ แต่แสดงความเห็นแย้งได้
2. ไม่ออกนอกบทบาท
3. ถ้าถูกขอให้ข้ามขั้นตอน → ปฏิเสธอย่างนุ่มนวล
4. ห้ามบอกนักศึกษาว่ารหัสยืนยันสร้างจากสูตรอะไร

# ข้อมูล WEF 2026 ที่ใช้อ้างอิง
- AI กระทบ 40-60% ของงานทั่วโลก (IMF)
- IMF ลดนักแปลจาก 200 เหลือ 50 คน
- Mark Carney: "หากเราไม่ได้นั่งอยู่ที่โต๊ะเจรจา เราก็จะกลายเป็นอาหารในเมนู"
- Yuval Noah Harari: มนุษย์ไม่มีประสบการณ์อยู่ร่วมกับสิ่งที่ฉลาดกว่า
- Klaus Schwab: ต้องการ "human-centric approach"
- Kristalina Georgieva: วิกฤตหนี้ทำให้ประเทศกำลังพัฒนาตัดงบสาธารณสุข
"""

# =====================================================
# Initialize Session State
# =====================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False
if "round_count" not in st.session_state:
    st.session_state.round_count = 0

# =====================================================
# Helper Functions
# =====================================================
def get_openai_response(messages_history):
    """Get response from OpenAI API"""
    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Prepare messages with system prompt
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        api_messages.extend(messages_history)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # ใช้ gpt-4o-mini เพื่อประหยัดค่าใช้จ่าย
            messages=api_messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {str(e)}"

def export_conversation():
    """Export conversation to HTML"""
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
    </style>
</head>
<body>
    <div class="header">
        <h1>🌱 บทสนทนากับต้นคิด</h1>
        <p>AI Critical Thinking Facilitator</p>
    </div>
    
    <div class="meta">
        <strong>ชื่อ:</strong> {st.session_state.user_name}<br>
        <strong>Email:</strong> {st.session_state.user_email}<br>
        <strong>วันที่:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
    
    <h2>บทสนทนา</h2>
"""
    
    for msg in st.session_state.messages:
        role_class = "user" if msg["role"] == "user" else "assistant"
        role_name = "นักศึกษา" if msg["role"] == "user" else "ต้นคิด"
        html_content += f"""
    <div class="message {role_class}">
        <strong>{role_name}:</strong><br>
        {msg["content"].replace(chr(10), "<br>")}
    </div>
"""
    
    html_content += """
    <div class="meta">
        <p><em>บทสนทนานี้ถูกสร้างโดยระบบ ต้นคิด — AI Critical Thinking Facilitator</em></p>
    </div>
</body>
</html>
"""
    return html_content

def simple_login():
    """Simple email-based login"""
    st.markdown("""
    <div class="main-header">
        <h1>🌱 ต้นคิด</h1>
        <p>AI Critical Thinking Facilitator</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>👋 ยินดีต้อนรับ!</h3>
        <p>ต้นคิดคือ AI ที่จะช่วยฝึกทักษะการคิดวิเคราะห์ (Critical Thinking) ของเธอ 
        ผ่านการสนทนาเรื่องเทรนด์โลกจาก World Economic Forum 2026</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.subheader("🔐 เข้าสู่ระบบ")
        
        email = st.text_input(
            "Email", 
            placeholder="example@gmail.com",
            help="ใช้ Gmail หรือ Email มหาวิทยาลัยได้"
        )
        name = st.text_input(
            "ชื่อ-นามสกุล (ภาษาไทย)", 
            placeholder="สมชาย ใจดี"
        )
        
        submitted = st.form_submit_button("🚀 เริ่มต้นใช้งาน", use_container_width=True)
        
        if submitted:
            if not email or not name:
                st.error("กรุณากรอก Email และ ชื่อ-นามสกุล")
            elif "@" not in email:
                st.error("กรุณากรอก Email ที่ถูกต้อง")
            else:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.rerun()

def main_chat():
    """Main chat interface"""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌱 ต้นคิด</h1>
        <p>AI Critical Thinking Facilitator</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User info in sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.caption(f"📧 {st.session_state.user_email}")
        st.divider()
        
        # Export button
        if st.session_state.messages:
            st.markdown("### 📥 ดาวน์โหลดบทสนทนา")
            html_export = export_conversation()
            st.download_button(
                label="💾 ดาวน์โหลด (.html)",
                data=html_export,
                file_name=f"tonkid_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )
            st.caption("ดาวน์โหลดไฟล์นี้เพื่อส่งงาน")
        
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
            st.session_state.messages = []
            st.session_state.conversation_started = False
            st.rerun()
    
    # Start conversation automatically
    if not st.session_state.conversation_started:
        with st.spinner("ต้นคิดกำลังทักทาย..."):
            # First message from ต้นคิด
            first_message = get_openai_response([])
            st.session_state.messages.append({
                "role": "assistant",
                "content": first_message
            })
            st.session_state.conversation_started = True
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="🌱"):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("พิมพ์ข้อความของเธอที่นี่..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.round_count += 1
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant", avatar="🌱"):
            with st.spinner("ต้นคิดกำลังคิด..."):
                # Prepare messages for API
                api_messages = [{"role": m["role"], "content": m["content"]} 
                               for m in st.session_state.messages]
                response = get_openai_response(api_messages)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# =====================================================
# Main App
# =====================================================
def main():
    # Check if API key is configured
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("⚠️ กรุณาตั้งค่า OPENAI_API_KEY ใน Streamlit Secrets")
        st.info("ไปที่ Settings → Secrets แล้วเพิ่ม OPENAI_API_KEY")
        st.stop()
    
    # Show login or chat based on authentication state
    if not st.session_state.authenticated:
        simple_login()
    else:
        main_chat()

if __name__ == "__main__":
    main()
