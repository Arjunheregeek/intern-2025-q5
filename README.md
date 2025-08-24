# CLI Chatbot with Conversation Memory

An interactive command-line chatbot powered by LangChain's ConversationBufferWindowMemory that remembers the last 4 conversation turns for contextual responses.

## Features

- 🧠 **Conversation Memory**: Remembers last 4 turns using LangChain
- 💬 **Interactive CLI**: Continuous conversation loop with commands
- 🔄 **Context Awareness**: Maintains context between messages
- 📊 **Memory Management**: Automatic sliding window and buffer status
- 🛠️ **Commands**: Built-in commands for history, status, and clearing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Usage

```bash
python main.py
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `quit` or `exit` | End the conversation |
| `clear` | Clear conversation history |
| `history` | Show conversation history |
| `status` | Show memory buffer status |

## Example Conversation

```
🤖 AI CHATBOT WITH MEMORY
============================================================
I can remember our last 4 conversation turns!

[Turn 1] You: Hi, my name is Alice
🤖 AI: Hello Alice! Nice to meet you. How can I help you today?

[Turn 2] You: What's my name?
🤖 AI: Your name is Alice, as you mentioned when we started talking.

[Turn 3] You: Tell me about AI
🤖 AI: AI, or Artificial Intelligence, refers to systems that can perform tasks typically requiring human intelligence...

[Turn 4] You: status
📊 Memory Status:
  • Current turn: 3
  • Messages in buffer: 6
  • Conversation turns: 3
  • Memory window: 4 turns
  • Buffer full: No
```

## Memory Management

### Sliding Window
- Keeps exactly **4 conversation turns** (8 messages total)
- Automatically removes oldest messages when buffer is full
- Maintains conversation continuity within the window

### Context Building
```python
# Example context passed to LLM:
User: Hi, my name is Alice
Assistant: Hello Alice! Nice to meet you.
User: What's my name?
Assistant: Your name is Alice.
User: Tell me about AI
```

## Architecture

```
src/
├── services/
│   ├── chatbot.py           # Main CLI interface
│   ├── memory_manager.py    # LangChain memory integration
│   └── api_client.py        # Gemini API client
tests/
├── test_memory.py           # Memory functionality tests
main.py                      # Entry point
```

## Testing

```bash
# Run memory tests
pytest tests/test_memory.py -v

# Run all tests
pytest tests/ -v
```

## Error Handling

- **API Failures**: Continues conversation after errors
- **Invalid Commands**: Helpful error messages
- **Memory Overflow**: Automatic pruning of old messages
- **Graceful Exit**: Ctrl+C handling

## Memory Buffer States

| State | Description | Buffer Size |
|-------|-------------|-------------|
| Empty | No messages | 0/8 messages |
| Partial | Some messages | 1-7/8 messages |
| Full | Buffer at capacity | 8/8 messages |
| Sliding | Removing old, adding new | Always 8/8 |
