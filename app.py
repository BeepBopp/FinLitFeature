import streamlit as st
import base64
from openai import OpenAI

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

    file_bytes = uploaded_file.read()
    encoded_file = base64.b64encode(file_bytes).decode("utf-8")

    st.info("Analyzing...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a financial literacy AI that analyzes receipts and purchases for young users. "
                        "If the uploaded image or text contains any personal, financial, or sensitive information such as Social Security Numbers, bank account numbers, credit card numbers, routing numbers, passwords, or home addresses, you must refuse to analyze that portion and tell the user to remove it. "
                        "Otherwise, evaluate whether the purchase is financially responsible, consider the user's context, explain reasoning, and provide friendly suggestions or cheaper alternatives when needed."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": user_prompt},
                        {"type": "input_image", "image_url": f"data:application/octet-stream;base64,{encoded_file}"}
                    ]
                }
            ]
        )

        result = response.choices[0].message["content"]
        st.subheader("📊 Analysis")
        st.write(result)

    except Exception as e:
        st.error(f"Error: {e}")
