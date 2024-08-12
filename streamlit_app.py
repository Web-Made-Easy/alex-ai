import streamlit as st
import google.generativeai as genai
import time
import os
import random
import supabase

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="Your name is Alex. You are a friendly AI Tutor.",
)

chat_session = model.start_chat(history=[])

c1, c2, c3, c4, c5 = st.columns([6,1,1,1,3])

with c5:
    with st.popover("Sign Up", help=None, disabled=False, use_container_width=True):
        with st.form("Sign Up", border=False):
            name_input = st.text_input("Enter your name: ")
            email_input = st.text_input("Enter your email: ")
            password_input = st.text_input("Enter a password: ", type="password")
            submit_btn = st.form_submit_button("Sign Up")
        if submit_btn:
            # Initialize database connection.
            conn = st.connection("supabase",type=SupabaseConnection)
            conn.query("INSERT INTO ", table="account_data", ttl="10m").execute()
with c1:
    st.title("Alex AI")
    st.write("Your AI Tutor. Powered by Google Generative AI.")

if "pin_entered" not in st.session_state:
    st.session_state.pin_entered = False
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.pin_entered:
    pin_input = st.text_input("Enter your Tutor Pin:")
    if pin_input:
        if pin_input=="459836": 
            st.session_state.pin_entered = True
            st.rerun()
        else:
            st.error("Invalid Pin")
    else:
        st.info("Enter your Tutor Pin to access the site")

if st.session_state.pin_entered: 
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("You:  "):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("tutor"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                response = chat_session.send_message(prompt)

                # Get the full text response directly
                full_response = response.text  

                current_text = ""
                for letter in full_response:
                    current_text += letter
                    response_placeholder.markdown(current_text)
                    time.sleep(0.01)

            except Exception as e:
                response_placeholder.markdown("An error occurred: " + str(e))

        st.session_state.messages.append({"role": "tutor", "content": full_response})
