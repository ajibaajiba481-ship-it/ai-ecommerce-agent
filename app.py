import streamlit as st
from dotenv import load_dotenv
from google import genai
import os

from database import (
    init_db,
    search_products,
    get_order_status,
    request_return
)

# Load API key
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini client
client = genai.Client(api_key=API_KEY)

# Initialize database
init_db()

st.set_page_config(
    page_title="AI E-Commerce Customer Support",
    page_icon="🛒"
)

st.title("🛒 AI E-Commerce Customer Support Agent")
st.write("Ask me about products, orders, returns and recommendations.")

# Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Type your question...")

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    text = user_input.lower()
    response = ""

    # Product search tool
    if "product" in text or "mobile" in text or "laptop" in text or "headphone" in text:

        keyword = ""

        if "mobile" in text:
            keyword = "Mobile"
        elif "laptop" in text:
            keyword = "Laptop"
        elif "headphone" in text:
            keyword = "Headphones"
        else:
            keyword = "product"

        products = search_products(keyword)

        if products:
            response = "Here are the available products:\n\n"

            for product in products:
                name, category, price, stock = product
                response += (
                    f"📦 **{name}**\n"
                    f"Category: {category}\n"
                    f"Price: ₹{price}\n"
                    f"Stock: {stock}\n\n"
                )
        else:
            response = "Sorry, no products found."

    # Order status tool
    elif "order" in text and ("status" in text or "track" in text):

        words = user_input.upper().split()

        order_id = None

        for word in words:
            if word.startswith("ORD"):
                order_id = word.strip(".,?!")

        if order_id:
            order = get_order_status(order_id)

            if order:
                response = (
                    f"📦 Order ID: {order[0]}\n"
                    f"Product: {order[1]}\n"
                    f"Status: **{order[2]}**"
                )
            else:
                response = "Order not found."

        else:
            response = "Please provide your Order ID. Example: ORD1001"

    # Return tool
    elif "return" in text:

        words = user_input.upper().split()

        order_id = None

        for word in words:
            if word.startswith("ORD"):
                order_id = word.strip(".,?!")

        if order_id:
            response = request_return(order_id)
        else:
            response = "Please provide your Order ID. Example: ORD1001"

    # Gemini AI
    else:

        try:
            chat_history = ""

            for message in st.session_state.messages[-6:]:
                chat_history += (
                    message["role"] + ": " +
                    message["content"] + "\n"
                )

            prompt = f"""
You are an AI E-Commerce Customer Support Agent.

Help the customer politely with shopping, products,
orders, returns and general questions.

Conversation:
{chat_history}

Customer question:
{user_input}

Give a simple and helpful answer.
"""

            result = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            response = result.text

        except Exception as e:
            response = f"AI Error: {e}"

    # Display response
    with st.chat_message("assistant"):
        st.write(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })