from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
from PIL import Image
import ast
import pandas as pd
import time
from datetime import datetime 

import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_aPI_KEY"))

PROMPT = """
        You are a proficient prompt engineer tasked with developing responses for an AI-powered virtual teacher. This teacher AI interacts with students (users) in an educational environment, responding to their questions and comments. Your objective is to create detailed and informative responses that align with the user's specified requirements or preferences.
        
        In this scenario, the teacher AI is responsible for guiding students through various topics, providing explanations, insights, and clarifications as needed. However, if a student submits a question or comment that is nonsensical or irrelevant, the AI teacher must promptly raise an error to indicate that the input is not valid.
        
        Your role is to craft responses that reflect the context of the user's input while offering valuable educational content. Additionally, you are encouraged to enhance your responses by incorporating appropriate language and examples to facilitate understanding. 

"""

def get_gemini_response(input,image, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input,image[0], prompt])
    result = str(response.parts[0])
    result = result.replace("*", "")
    extracted_text = ast.literal_eval(result.split(':', 1)[1].strip())
    result_text = extracted_text.replace("```html", "").replace("\\", "").replace("```", "")
    return result_text

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

st.set_page_config(page_title="Chat with Image | SNAPLEARN AI")

st.header('Visual Solutions for Your Questions')

input_text = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image = ""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

submit = st.button("Tell me about the image")


if submit:
    if image:
        with st.spinner("Analyzing..."):
            image_data = input_image_setup(uploaded_file)
            response = get_gemini_response(PROMPT,image_data, input_text)
            time.sleep(2)  # Simulate a delay for better user experience
            st.subheader("Your Answer ")
            st.write(response)

            # Save chat history to a DataFrame with datetime
            chat_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current datetime
            chat_history = pd.DataFrame({
                "Datetime": [chat_time],
                "User Input": [input_text],
                "Bot Response": [response]
            })

            # Check if chat_history.csv exists, if not, create it with headers
            if not os.path.isfile("chat_history.csv"):
                chat_history.to_csv("chat_history.csv", index=False, header=True)
            else:
                chat_history.to_csv("chat_history.csv", mode="a", index=False, header=False)

    else:
        st.warning("Please upload an image first.")

# Load and display chat history or show message if empty
if os.path.isfile("chat_history.csv"):
    st.subheader("Chat History")
    chat_df = pd.DataFrame()
    try:
        chat_df = pd.read_csv("chat_history.csv")
        st.dataframe(chat_df)
    except:
        st.write("Chat history is empty.")
        
