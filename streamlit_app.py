import streamlit as st
import google.generativeai as genai
import time
import os
import random
from supabase import create_client, Client

# Configure the Google Generative AI model
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

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

@st.cache_resource
def init_supabase_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase_connection()

chat_session = model.start_chat(history=[])

c1, c2, c3, c4, c5 = st.columns([6,1,1,3,3])

def check_if_logged_in():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.info("Hey there, please sign up or log in to the start chatting!")
    else:
        st.session_state.logged_in = True
        log_in_placeholder.empty()
    if "messages" not in st.session_state:
        st.session_state.messages = []

check_if_logged_in()

log_in_placeholder = st.empty()
with log_in_placeholder.container():
    with c4:
        try:
            with st.popover("Log In", help=None, disabled=False, use_container_width=True):
                with st.form("Log In", border=False):
                    email_input = st.text_input("Enter your email: ")
                    pin_input = st.number_input("Enter your pin: ", min_value=111111, max_value=999999, disabled=False)
                    submit_btn = st.form_submit_button("Sign Up")
                if submit_btn:
                    ### Database ###
                    # Check if pin exists
                    pin_found = supabase.from_('account_data').select('pin').eq('pin', created_pin).execute()
                    email_found = supabase.from_('account_data').select('email').eq('email', email_input).execute()
                    if pin_found.data and email_found.data:
                        st.success("Successfully logged in!")
                        st.session_state.logged_in = True
                        check_if_logged_in()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
    with c5:
        try:
            with st.popover("Sign Up", help=None, disabled=False, use_container_width=True):
                with st.form("Sign Up", border=False):
                    name_input = st.text_input("Enter your name: ")
                    email_input = st.text_input("Enter your email: ")
                    password_input = st.text_input("Enter a password: ", type="password")
                    submit_btn = st.form_submit_button("Sign Up")
                if submit_btn:
                    # Create Pin:
                    created_pin = random.randint(111111, 999999)
                    ### Database ###
                    # Check if pin exists (unlikely)
                    pin_found = supabase.from_('account_data').select('pin').eq('pin', created_pin).execute()
                    if pin_found.data:
                        created_pin = random.randint(111111, 999999)
                    # Check if email already exists
                    email_found = supabase.from_('account_data').select('email').eq('email', email_input).execute()
                    if email_found.data:
                        st.error("An account with this email already exists! Try again.")
                    else:
                    # Insert new account data: 
                        query = {
                            "name": name_input,
                            "email": email_input,
                            "password": password_input,
                            "pin": created_pin
                        }
                        supabase.from_('account_data').insert(query).execute()
                        st.success("Account created successfully!")
                        st.info(f"Your pin is **{created_pin}**. Keep this safe as you will need it to sign in.")
                        st.session_state.logged_in = True
                        check_if_logged_in()
        except Exception as e:
            st.error(f"Something went wrong: {e}")

with c1:
    st.title("Alex AI")
    st.write("Your AI Tutor. Powered by Google Generative AI.")

if st.session_state.logged_in: 
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
