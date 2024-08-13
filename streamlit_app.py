import streamlit as st
from streamlit_modal import Modal
import google.generativeai as genai
import time
import os
import random
from supabase import create_client, Client

# Configure the Google Generative AI model
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

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

# Initialize Supabase client
supabase_url = os.environ("SUPABASE_URL")
supabase_key = os.environ("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

chat_session = model.start_chat(history=[])

c1, c2, c3, c4, c5 = st.columns([6,1,1,1,3])

with c5:
    try:
        with Modal("Sign Up", help=None, disabled=False, use_container_width=True):
            with st.form("Sign Up", border=False):
                name_input = st.text_input("Enter your name: ")
                email_input = st.text_input("Enter your email: ")
                password_input = st.text_input("Enter a password: ", type="password")
                submit_btn = st.form_submit_button("Sign Up")
            if submit_btn:
                # Pin:
                created_pin = random.randint(111111, 999999)
                # Database
                # Check if pin exists (unlikely)
                pin_found = supabase.from_('account_data').select('pin').eq('pin', created_pin).execute()
                if pin_found.data:
                    created_pin = random.randint(111111, 999999)
                # Check if email already exists
                email_found = supabase.from_('account_data').select('email').eq('email', email_input).execute()
                if email_found.data:
                    st.error("An account with this email already exists! Try again.")
                else:
                    # Insert new account data
                    query = {
                        "name": name_input,
                        "email": email_input,
                        "password": password_input,
                        "pin": created_pin
                    }
                    supabase.from_('account_data').insert(query).execute()
                    st.success("Account created successfully!")
                    st.info(f"Your pin is **{created_pin}**. Keep this safe as you will need it to sign in.")
    except Exception as e:
        st.error(f"Something went wrong: {e}")

with c1:
    st.title("Alex AI")
    st.write("Your AI Tutor. Powered by Google Generative AI.")

if "pin_entered" not in st.session_state:
    st.session_state.pin_entered = False
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.pin_entered:
    pin_input = st.text_input("Enter your Pin:")
    if pin_input:
        if pin_input == "459836": 
            st.session_state.pin_entered = True
            st.rerun()
        else:
            st.error("Invalid pin...")
    else:
        st.info("Enter your Tutor Pin to access your account")

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
