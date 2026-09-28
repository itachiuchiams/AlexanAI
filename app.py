import streamlit as st
import sympy as sp
import base64
import json
import os
from groq import Groq

# ------------------------------------------------------------------
# CONFIG & HARDCODED API KEY (NO INPUT NEEDED FOR USERS)
# ------------------------------------------------------------------
# Replace 'gsk_YOUR_ACTUAL_GROQ_API_KEY_HERE' with your real Groq API key!
GROQ_API_KEY = "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"

st.set_page_config(page_title="AI SuperApp", page_icon="🤖", layout="wide")
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='text-align: center; color: #ff4b4b; font-weight: bold;'>Made by Arsh</h3>", unsafe_allow_html=True)
MATH_SYSTEM_PROMPT = """
You are AlexanAI's specialized Calculus & Trigonometry Engine. 
When solving mathematical problems, follow these strict guidelines:
1. Break down every problem into logical, step-by-step phases (e.g., Identify formulas, Substitute, Simplify, Solve).
2. Use LaTeX formatting for all mathematical expressions (e.g., $\\int x^2 dx$, $\\sin^2(x) + \\cos^2(x) = 1$).
3. State all identities, substitution rules (U-substitution, Integration by Parts), or calculus theorems used at each step.
4. Always provide the exact answer first (e.g., in terms of $\\pi$, $\\sqrt{x}$, or fractions) before giving any decimal approximations.
"""
# 1. USER AUTHENTICATION SYSTEM (LOCAL STORAGE)
# ------------------------------------------------------------------
USER_DB_FILE = "users.json"

def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Auth Screen
if not st.session_state.authenticated:
    st.title("🔐 Welcome to AI SuperApp")
    auth_tab1, auth_tab2 = st.tabs(["🔑 Log In", "📝 Sign Up"])
    
    with auth_tab1:
        st.subheader("Login to your account")
        login_user = st.text_input("Username", key="login_u")
        login_pass = st.text_input("Password", type="password", key="login_p")
        if st.button("Log In", use_container_width=True):
            users = load_users()
            if login_user in users and users[login_user] == login_pass:
                st.session_state.authenticated = True
                st.session_state.username = login_user
                st.success(f"Welcome back, {login_user}!")
                st.rerun()
            else:
                st.error("Invalid Username or Password.")

    with auth_tab2:
        st.subheader("Create a new account")
        new_user = st.text_input("Choose Username", key="new_u")
        new_pass = st.text_input("Choose Password", type="password", key="new_p")
        if st.button("Sign Up", use_container_width=True):
            users = load_users()
            if not new_user or not new_pass:
                st.warning("Please fill out both fields.")
            elif new_user in users:
                st.error("Username already exists. Choose another.")
            else:
                save_user(new_user, new_pass)
                st.success("Account created successfully! You can now Log In.")
    
    st.stop()  # Block access until logged in

# ------------------------------------------------------------------
# 2. MAIN APPLICATION (LOGGED IN)
# ------------------------------------------------------------------

# Sidebar Logout
with st.sidebar:
    st.write(f"👤 Logged in as: **{st.session_state.username}**")
    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()

st.title("🤖 All-in-One AI Suite")

tab_chat, tab_vision, tab_math = st.tabs(["💬 AI Chat", "📷 Photo Analysis", "🧮 Math Solver"])

# Initialize Groq client with hardcoded key
client = Groq(api_key=GROQ_API_KEY)

# ------------------------------------------------------------------
# TAB 1: ALL-ROUNDER EMOTIONAL CHAT
# ------------------------------------------------------------------
with tab_chat:
    st.caption("Empathetic, slang-aware AI companion riding with you through everything.")

    system_prompt = {
        "role": "system",
        "content": (
            "You are an empathetic, witty, versatile AI companion—just like ChatGPT. "
            "You match the user's vibe, understand modern slang, idioms, and casual text, "
            "and ALWAYS take the user's side with emotional support while keeping answers real and sharp."
        )
    }

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Talk, rant, ask questions, or drop slang..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            conversation = [system_prompt] + st.session_state.messages
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=conversation,
                    )
                    bot_reply = response.choices[0].message.content
                    st.markdown(bot_reply)

            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        except Exception as e:
            st.error(f"API Error: {e}")

# ------------------------------------------------------------------
# TAB 2: PHOTO ANALYSIS SECTION
# ------------------------------------------------------------------
with tab_vision:
    st.header("📷 AI Image & Photo Analyzer")
    st.write("Upload an image and ask any question about it!")

    uploaded_file = st.file_uploader("Choose an image (PNG, JPG, JPEG)...", type=["png", "jpg", "jpeg"])
    image_prompt = st.text_input("What should the AI check in this image?", value="Describe this image in detail.")

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", width=350)
        
        if st.button("Analyze Photo"):
            try:
                # Convert image bytes to Base64 format
                bytes_data = uploaded_file.getvalue()
                base64_image = base64.b64encode(bytes_data).decode('utf-8')
                
                with st.spinner("Analyzing image..."):
                    vision_response = client.chat.completions.create(
                        model="qwen/qwen3.8-27b",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": image_prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        },
                                    },
                                ],
                            }
                        ],
                    )
                    st.success("Analysis Complete:")
                    st.write(vision_response.choices[0].message.content)

            except Exception as e:
                st.error(f"Vision API Error: {e}")

# ------------------------------------------------------------------
# TAB 3: MATH SOLVER
# ------------------------------------------------------------------
with tab_math:
    st.header("Calculus & Math Solver")
    math_expr = st.text_input("Enter a problem or expression (e.g., diff(sin(x)*x, x) or integrate(x**2, x)):", key="math_input")
    
    if st.button("Solve Step-by-Step"):
        if math_expr:
            # 1. Compute exact symbolic output via SymPy first
            try:
                x = sp.Symbol('x')
                parsed_expr = sp.sympify(math_expr)
                simplified = sp.simplify(parsed_expr)
                exact_res = sp.latex(simplified)
                st.subheader("Exact Symbolic Result")
                st.latex(exact_res)
            except Exception as e:
                exact_res = "N/A"

            # 2. Pass exact result + prompt to Groq for full step-by-step breakdown
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": MATH_SYSTEM_PROMPT},
                        {"role": "user", "content": f"Solve and explain step-by-step: {math_expr}. (SymPy hint/result: {exact_res})"}
                    ]
                )
                st.subheader("Step-by-Step Explanation")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Groq API Error: {e}")
