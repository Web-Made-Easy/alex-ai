import streamlit as st
import google.generativeai as genai
import time
import os

st.title("Alex AI")
st.write("Your AI Tutor. Powered by Google Generative AI.")
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

if "pin_entered" not in st.session_state:
    st.session_state.pin_entered = False
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.pin_entered:
    pin_input = st.text_input("Enter your Tutor Pin:")
    if pin_input: 
        st.session_state.pin_entered = True 
        st.experimental_rerun() 

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

                # Simulate word-by-word output
                for letter in full_response:
                    response_placeholder += letter
                    response_placeholder.markdown(response_placeholder, end='', flush=True)
                    time.sleep(0.05)

            except Exception as e:
                response_placeholder.markdown("An error occurred: " + str(e))

        st.session_state.messages.append({"role": "tutor", "content": full_response})
