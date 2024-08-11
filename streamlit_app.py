import streamlit as st
import google.generativeai as genai

# Show title and description.
st.title("Alex AI")
st.write(
    "This is an AI Tutor to help you with your learning, no matter your age. "
    "It is powered by Google Generative AI and Streamlit. "
)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Create the model
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

chat_session = model.start_chat(
  history=[
  ]
)


placeholder = st.empty()
pin = placeholder.text_input("", key="pin")
if pin:
    placeholder.empty()
    prompt = st.chat_input("Say something")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"])
        st.markdown(message["content"])
        
    if prompt := st.chat_input("What's up?"):
        st.write(f"You: {prompt}")
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        response = chat_session.send_message(prompt)
        with st.chat_message("tutor"):
            st.markdown(response)
        st.session_state.message.append({"role": "tutor", "content": response})
    
else:
    st.info("Enter your Tutor Pin to access your account.")
        
