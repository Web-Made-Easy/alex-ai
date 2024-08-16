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
log_in_placeholder = st.empty()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = []

username = None
if st.session_state["logged_in"]:
    c1, c2, c3 = st.columns([7, 2, 2])

    chat_session = model.start_chat(history=st.session_state["messages"])

    with c1:
        st.title("Alex AI")
        st.write("Your AI Tutor. Powered by Google Generative AI.")
    
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("You:  "):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("Alex"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                response = chat_session.send_message(prompt)

                full_response = response.text  

                current_text = ""
                for letter in full_response:
                    current_text += letter
                    response_placeholder.markdown(current_text)
                    time.sleep(0.01)

            except Exception as e:
                response_placeholder.markdown("An error occurred: " + str(e))

        st.session_state["messages"].append({"role": "tutor", "content": full_response})
else:
    c1, c2, c3 = st.columns([7, 2, 2])
    with log_in_placeholder.container():
        with c2:
            with st.popover("Log In", help=None, disabled=False, use_container_width=True):
                with st.form("Log In", border=False):
                    email_input = st.text_input("Enter your email: ")
                    pin_input = st.text_input("Enter your pin: ", placeholder="eg. 123456")
                    submit_btn = st.form_submit_button("Log In")
                if submit_btn:
                    pin_input = int(pin_input)
                    ### Database ###
                    # Check if pin exists
                    pin_found = supabase.from_('account_data').select('pin').eq('pin', pin_input).execute()
                    email_found = supabase.from_('account_data').select('email').eq('email', email_input).execute()
                    if pin_found.data and email_found.data:
                        st.success("Successfully logged in!")
                        st.session_state["logged_in"] = True
                        userdata = supabase.from_('account_data').select('name').eq('pin', pin_input).execute()
                        username = userdata.data[0]['name'] if userdata.data else "User"
                        log_in_placeholder.empty()
                        with log_in_placeholder.container():
                            with c3:
                                with st.popover(f"{username}", help=None, disabled=False, use_container_width=True):
                                    st.button("Profile")
                    else:
                        st.error("Invalid email or pin.")
        
        with c3:
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
                        st.session_state["logged_in"] = True
                        userdata = supabase.from_('account_data').select('name').eq('pin', created_pin).execute()
                        username = userdata.data[0]['name'] if userdata.data else "User"
                        log_in_placeholder.empty()
                        with log_in_placeholder.container():
                            with c3:
                                with st.popover(f"{username}", help=None, disabled=False, use_container_width=True):
                                    st.button("Profile")

with c1:
    st.title("Alex AI")
    st.write("Your AI Tutor. Powered by Google Generative AI.")

if st.session_state["logged_in"]:
    log_in_placeholder.empty()
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("You:  "):
        st.session_state["messages"].append({"role": "user", "content": prompt})
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

        st.session_state["messages"].append({"role": "tutor", "content": full_response})
