from backend.chat_history.conversation import ConversationHistory

# 1) Initialize a ConversationHistory object
conv_history = ConversationHistory()

# 2) Insert some text
session_id = "session_1"
conv_history.add_to_conversation_history(session_id, "user", "Hello, how are you?")
conv_history.add_to_conversation_history(session_id, "bot", "I'm fine, thank you!")

# 3) Retrieve the text and print
initial_history = conv_history.get_conversation_history(session_id)
print("Initial Conversation History:")
for entry in initial_history:
    print(f"{entry['role']}: {entry['content']}")

# 4) Update the history
conv_history.add_to_conversation_history(session_id, "user", "What's your name?")
conv_history.add_to_conversation_history(session_id, "bot", "My name is bot.")

# 5) Retrieve the updated text and print
updated_history = conv_history.get_conversation_history(session_id)
print("\nUpdated Conversation History:")
for entry in updated_history:
    print(f"{entry['role']}: {entry['content']}")