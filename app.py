import streamlit as st
import base64
from openai import OpenAI
import PyPDF2
from PIL import Image
import io

st.set_page_config(page_title="Financial Literacy Expense Analyzer")
st.title("💸 Financial Literacy Expense Analyzer")
st.warning(
    "Do NOT upload or include any personal or sensitive information such as Social Security Numbers, bank account numbers, routing numbers, passwords, or home address."
)

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Missing `OPENAI_API_KEY` in Streamlit secrets.")
    st.stop()

api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

uploaded_file = st.file_uploader(
    "Upload a bill, receipt, credit card statement, or payment screenshot (PNG/JPG/PDF)",
    type=["png", "jpg", "jpeg", "pdf"]
)

user_prompt = st.text_area(
    "Enter context or reasoning about the purchase.",
    placeholder="Why did you make this purchase? Is it essential? How does it relate to your financial goals?"
)

if st.button("Analyze Expense"):
    if not uploaded_file:
        st.error("Please upload a file!")
        st.stop()
    
    if not user_prompt.strip():
        st.error("Please enter your context or reasoning!")
        st.stop()
    
    bytes_data = uploaded_file.read()
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    st.info("Analyzing...")
    
    try:
        if file_extension in ["png", "jpg", "jpeg"]:
            mime_type = f"image/{file_extension}" if file_extension != "jpg" else "image/jpeg"
            encoded_file = base64.b64encode(bytes_data).decode("utf-8")
            data_url = f"data:{mime_type};base64,{encoded_file}"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "GENERAL GUIDELINES:"
                            "You are a financial literacy AI that analyzes receipts and purchases for young users. "
                            "If the uploaded image or text contains any personal, financial, or sensitive information such as Social Security Numbers, bank account numbers, credit card numbers, routing numbers, passwords, or home addresses, you must refuse to analyze that portion and tell the user to remove it. "
                            "Otherwise, evaluate whether the purchase is financially responsible, consider the user's context, explain reasoning, and provide friendly suggestions or cheaper alternatives when needed."
                            "OUTPUT REQUIREMENTS:"
                            "DO NOT FORGET: AT THE TOP PUT A SENTENCE OR SO on whether this may or may not be financially literate (or something saying it is in a grey area."
                            "A paragraph explaining a summary of the image and context under the header 'Summary'"
                            "A paragraph explaining your reasoning under the header 'Reasoning'"
                            "A paragraph explaining future steps and alternatives to consider under the header 'Future Steps'"
                            "ALSO: DO NOT USE $$ OR LATEX IN YOUR RESPONSE AT ANY POINT."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {"type": "image_url", "image_url": {"url": data_url}}
                        ]
                    }
                ]
            )

        elif file_extension == "pdf":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(bytes_data))
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a financial literacy AI that analyzes receipts and purchases for young users. "
                            "If the text contains any personal, financial, or sensitive information such as Social Security Numbers, bank account numbers, credit card numbers, routing numbers, passwords, or home addresses, you must refuse to analyze that portion and tell the user to remove it. "
                            "Otherwise, evaluate whether the purchase is financially responsible, consider the user's context, explain reasoning, and provide friendly suggestions or cheaper alternatives when needed."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"{user_prompt}\n\n---\nDocument Content:\n{pdf_text}"
                    }
                ]
            )
        
        result = response.choices[0].message.content
        st.subheader("📊 Analysis")
        st.write(result)
    
    except Exception as e:
        st.error(f"Error: {e}")
