import streamlit as st
from experta import Fact, Rule, KnowledgeEngine
from controller import converFact_to_string, response, get_book
from facts import knowledge_base, BookFact
from main import LibraryExpertSystem

# Streamlit app initialization
st.set_page_config(page_title="Library Expert System", layout="centered")

# Chatbot-like interface
st.title("📚  Expert Librarian System ")

# Define the questions for user input
questions = [
    "What type of category do you want?",
    "Who is the author you prefer?",
    "Tell me the topics related to the category you would like to refer. It will be helpful to find the most suitable books.",
    "How much book rating do you hope to find, like 4.1 or 4.5?",
    "How about the target audience, like teens or adults?",
    "Which type of book do you hope for, like a novel or hardcover?",
    "Which language do you prefer for the book?",
]

# Initialize session state for user inputs and steps
if "user_params" not in st.session_state:
    st.session_state.user_params = {
        "category": None,
        "author": None,
        "keywords": set(),
        "rating": None,
        "target_audience": None,
        "book_type": None,
        "language": None,
    }

if "step" not in st.session_state:
    st.session_state.step = 0

# Chatbot conversation flow
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I assist you with your book preferences today?"}]

# Display chat messages (previous responses from assistant)
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input and interaction
if st.session_state.step < len(questions):
    user_input = st.text_input(questions[st.session_state.step])
    if st.button("Next"):
        # Store user input based on the current step
        key = list(st.session_state.user_params.keys())[st.session_state.step]
        if key == "keywords":
            st.session_state.user_params[key] = set(user_input.split(",")) if user_input else set()
        elif key == "rating":
            try:
                st.session_state.user_params[key] = float(user_input) if user_input else None
            except ValueError:
                st.error("Please enter a valid rating (e.g., 4.5).")
                st.stop()
        else:
            st.session_state.user_params[key] = user_input.strip() if user_input else None

        # Append user input to chat history and move to the next step
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.step += 1
        st.rerun()

# Once all inputs are collected, run the expert system
if st.session_state.step == len(questions):
    st.success("Thank you for providing your preferences! Let's find the best recommendations for you.")
    st.write("📖 Here's what you shared:")
    st.json(st.session_state.user_params)

    # Convert session state to BookFact
    user_params_fact = BookFact(
        category=st.session_state.user_params["category"],
        author=st.session_state.user_params["author"],
        keywords=st.session_state.user_params["keywords"],
        rating=st.session_state.user_params["rating"] or 0,
        target_audience=st.session_state.user_params["target_audience"],
        language=st.session_state.user_params["language"],
        book_type=st.session_state.user_params["book_type"],
    )

    # Run the expert system
    engine = LibraryExpertSystem(knowledge_base)
    engine.reset()
    engine.declare(user_params_fact)
    engine.run()

    # Display results
    st.write("### 📚 Recommendations:")
    if response.get("response_messege"):
        st.info(response["response_messege"])
    if response.get("response_data"):
        for i, book in enumerate(response["response_data"], start=1):
            if isinstance(book, dict):
                st.write(f"### **{i}. {book.get('title', 'Unknown Title')}**")
                st.write(f"**Author**: {book.get('author', 'Unknown Author')}")
                st.write(f"**Category**: {book.get('category', 'Unknown Category')}")
                st.write(f"**Rating**: {book.get('rating', 'N/A')}")
                st.write(f"**Target Audience**: {book.get('target_audience', 'N/A')}")
                st.write(f"**Language**: {book.get('language', 'Unknown Language')}")
                st.write(f"**Book Type**: {book.get('book_type', 'N/A')}")
                st.write(f"**Keywords**: {', '.join(book.get('keywords', []))}")
                st.write("---")
            else:
                book_reference, score = book
                st.write(f"confidence level :{score}%")
                st.warning(get_book(book_reference))

    # Reset button to start over
    if st.button("Start Over"):
        st.session_state.step = 0
        st.session_state.user_params = {
            "category": None,
            "author": None,
            "keywords": set(),
            "rating": None,
            "target_audience": None,
            "book_type": None,
            "language": None,
        }
        st.rerun()
