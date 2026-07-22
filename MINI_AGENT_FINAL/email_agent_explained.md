# Email Sending Agent — Full Project Explanation

**Stack used:** Google Gemini 2.5 Flash + Gmail SMTP + LangChain Tools

This document walks through your `email_agent.ipynb` notebook cell by cell, explains *why* each piece exists, and ties it back to the core AI concept it's teaching: **tool calling** (a.k.a. function calling), which is the foundation of almost every "AI agent" you'll build after this.

---

## 1. The Big Picture — What Are You Actually Building?

Before diving into code, understand the core idea in one sentence:

> **You give the model a plain-English instruction. The model doesn't do the task itself — it tells you *which function to run* and *with what arguments*. Your code runs that function, and the result is fed back to the model so it can decide the next step or give you a final answer.**

This is fundamentally different from a normal chatbot interaction. A regular LLM call just returns text. Here, the LLM is given a *menu of tools* (Python functions) it's allowed to "order from." It reads your instruction, looks at the tool descriptions, and decides:
- Do I need to call a tool?
- Which one?
- What arguments does it need?

The model **never touches your Gmail account directly**. It only outputs a structured request like:
```
call send_email(recipient_email="x@gmail.com", subject="...", body="...")
```
Your Python code is the one that actually executes it, using real SMTP credentials. This separation is intentional and important for safety — the model proposes, your code disposes.

This pattern (LLM decides → code executes → result goes back to LLM) is called an **agent loop**, and it's the backbone of virtually every "AI agent" framework you'll encounter (LangChain agents, AutoGPT-style tools, OpenAI's function calling, MCP servers, etc.). Once you understand this notebook deeply, you understand the skeleton of *all* of them.

---

## 2. Step 1 — Install Dependencies

```python
!pip install -q langchain langchain-google-genai langchain-core python-dotenv
```

| Package | Why it's here |
|---|---|
| `langchain` | Core LangChain library — message types, agent utilities |
| `langchain-google-genai` | The adapter that lets LangChain talk to Google's Gemini models |
| `langchain-core` | Base abstractions (messages, tools) shared across LangChain integrations |
| `python-dotenv` | Loads secrets (API keys, passwords) from a `.env` file instead of hardcoding them |

**Why this matters:** LangChain is a framework that standardizes how you talk to *any* LLM provider (OpenAI, Gemini, Anthropic, etc.) using the same code patterns — messages, tools, and `.invoke()`. Learning it once means you can swap Gemini for another model later with minimal code changes.

---

## 3. Step 2 — Setup API Key & Credentials

```python
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ['SENDER_EMAIL'] = os.getenv("SENDER_EMAIL")
os.environ['SENDER_APP_PASSWORD'] = os.getenv("SENDER_APP_PASSWORD")
```

- `load_dotenv()` reads a `.env` file sitting next to your notebook and loads its key-value pairs as environment variables. This keeps secrets **out of your code** (and out of version control if you `.gitignore` the `.env` file).
- You need three secrets:
  1. `GEMINI_API_KEY` — from Google AI Studio, authenticates your calls to Gemini.
  2. `SENDER_EMAIL` — the Gmail address that will send the emails.
  3. `SENDER_APP_PASSWORD` — a **Gmail App Password**, not your normal password.

**Why an App Password?** Google blocks "less secure" direct password logins from scripts. An App Password is a 16-character token generated specifically for one app/script, tied to your account but revocable independently — so if it leaks, you just delete that one token instead of changing your whole Gmail password.

> ⚠️ Security tip: never commit your `.env` file to GitHub. Add it to `.gitignore` immediately.

---

## 4. Step 3 — Import Everything

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json, os
```

| Import | Purpose |
|---|---|
| `ChatGoogleGenerativeAI` | The LangChain wrapper class for calling Gemini models |
| `tool` | A **decorator** that turns a normal Python function into something the LLM can understand and call |
| `HumanMessage` | LangChain's data structure representing "a message the user sent" |
| `smtplib`, `MIMEText`, `MIMEMultipart` | Python's built-in email-sending toolkit (standard library, not LangChain) — used to actually connect to Gmail's SMTP server and send mail |
| `json` | Used to format a preview of the composed email as a string |

---

## 5. Step 4 — Define the Tools (the heart of "what the agent can do")

Three tools are defined using the `@tool` decorator:

### `compose_email(recipient_email, subject, body)`
```python
@tool
def compose_email(recipient_email: str, subject: str, body: str) -> str:
    """
    Compose an email given a recipient email address, a subject line, and a body message.
    Returns a confirmation string with the composed email details for review before sending.
    """
    composed = {"to": recipient_email, "subject": subject, "body": body}
    return json.dumps(composed)
```
A "dry-run" tool — it just packages the email into a JSON preview. No email is sent. Useful if you want the agent to *draft first, then ask for confirmation* before actually sending (a good practice pattern for anything with real-world side effects).

### `send_email(recipient_email, subject, body)`
```python
@tool
def send_email(recipient_email: str, subject: str, body: str) -> str:
    """
    Send an email to a given recipient email address with a given subject and body.
    Uses Gmail SMTP to deliver the email. Returns success or error message.
    """
    sender_email = os.environ['SENDER_EMAIL']
    app_password = os.environ['SENDER_APP_PASSWORD']
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return f'Email successfully sent to {recipient_email} with subject: {subject}'
    except smtplib.SMTPAuthenticationError:
        return 'Authentication failed. Make sure you are using a Gmail App Password, not your regular password.'
    except smtplib.SMTPRecipientsRefused:
        return f'Recipient {recipient_email} was refused. Check if the email address is correct.'
    except Exception as e:
        return f'Failed to send email: {str(e)}'
```
This is the **real** action tool. Breaking it down:
1. Builds a `MIMEMultipart` email object with sender, recipient, subject, and plain-text body.
2. Opens an **SSL-encrypted connection** to Gmail's SMTP server on port 465 (SMTP = Simple Mail Transfer Protocol, the standard way email gets sent between servers).
3. Logs in using your email + App Password.
4. Sends the email.
5. Wraps everything in `try/except` so specific failure types (wrong password, invalid recipient, or anything else) return a **human-readable string** instead of crashing.

**Why return strings, not raise exceptions?** Because the tool's return value goes straight back to the LLM as a `ToolMessage`. If it crashed instead, the whole agent loop would break. By catching errors and returning descriptive text, the *model itself* can read the failure and potentially explain it to the user, retry, or ask for clarification.

### `check_email_status(recipient_email)`
```python
@tool
def check_email_status(recipient_email: str) -> str:
    """
    Check and confirm the status of an email that was sent to a recipient email address.
    Returns a confirmation message.
    """
    return f'Confirmed: An email was dispatched to {recipient_email}. It should arrive within a few minutes.'
```
A simulated/mock tool — it doesn't actually check anything (Gmail SMTP doesn't give you real delivery confirmation this way), it just always returns a canned confirmation. It's included mainly to show the model can chain **multiple tools together** in sequence if it decides that's appropriate.

### The `@tool` decorator — how the LLM "sees" these functions
This is the most important concept in this whole file. When you write:
```python
@tool
def send_email(recipient_email: str, subject: str, body: str) -> str:
    """Send an email to..."""
```
LangChain automatically extracts:
- **`name`** → `"send_email"` (from the function name)
- **`description`** → the docstring text (`"Send an email to a given recipient..."`)
- **`args` schema** → built from the type hints (`recipient_email: str`, `subject: str`, `body: str`)

This metadata is what gets sent to Gemini alongside your instruction. The model reads the *description*, not the code, to decide when to use each tool — which is why writing clear, specific docstrings matters enormously in real projects. A vague description leads to the model picking the wrong tool or wrong arguments.

---

## 6. Step 5 — Initialize the Model and Bind Tools

```python
llm = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    google_api_key=os.environ['GEMINI_API_KEY']
)

tools = [compose_email, send_email, check_email_status]
tool_map = {t.name: t for t in tools}

llm_with_tools = llm.bind_tools(tools)
```

- `ChatGoogleGenerativeAI(...)` creates a handle to the Gemini 2.5 Flash model (a fast, cheaper Gemini variant well-suited for tool-calling tasks).
- `tools = [...]` is just a list of your three decorated functions.
- `tool_map = {t.name: t for t in tools}` builds a dictionary like `{"send_email": send_email, "compose_email": compose_email, ...}` — this lets you look up the *actual function* later by the *name string* the model returns (models can only output text/JSON, not real Python references).
- `llm.bind_tools(tools)` is the critical line: it returns a **new** model object that, on every call, automatically includes the tool schemas (name + description + args) in the request sent to Gemini. This is what makes the model "tool-aware."

From this point on, you always call `llm_with_tools`, never the raw `llm`, if you want tool-calling behavior.

---

## 7. Step 6 — The Agent Loop (the most important code in the notebook)

```python
def run_agent(user_instruction: str):
    print(f'User: {user_instruction.strip()}')
    print('-' * 60)

    messages = [HumanMessage(content=user_instruction)]
    step = 1

    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            print(f'\nAgent Final Answer:')
            print(response.content)
            break

        print(f'\nStep {step} — Model requested {len(response.tool_calls)} tool call(s):')

        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            print(f'  Calling: [{tool_name}]')
            print(f'  Args:    {tool_args}')

            tool_fn = tool_map[tool_name]
            tool_result = tool_fn.invoke(tool_call)
            messages.append(tool_result)
            print(f'  Result:  {tool_result.content}')

        step += 1

    return messages
```

Walk through this as a **loop with two possible outcomes each iteration**:

1. `messages = [HumanMessage(...)]` — start the conversation history with just the user's instruction. This `messages` list is the *entire memory* of the conversation — everything the model has said, every tool it called, every tool result — all get appended here and re-sent on every loop iteration (LLMs are stateless; they only know what's in the message list you send them each time).

2. `response = llm_with_tools.invoke(messages)` — send the whole conversation so far to Gemini. It replies with **either**:
   - Plain text (a final answer), **or**
   - A request to call one or more tools (`response.tool_calls` is a non-empty list).

3. `messages.append(response)` — whatever the model said (text or tool-call request) is added to history, so the model has full context of what it itself just did.

4. **`if not response.tool_calls: break`** — this is the loop's exit condition. If the model didn't ask for any tool, it means it's done — it's giving you its final answer, and the loop ends.

5. **If there ARE tool calls** — for each one:
   - Read `tool_name` (e.g. `"send_email"`) and `tool_args` (e.g. `{"recipient_email": "...", "subject": "...", "body": "..."}`) — this whole structure is what the model generated, essentially "fill in the blanks" based on your instruction.
   - `tool_fn = tool_map[tool_name]` — look up the *actual Python function* using the name string.
   - `tool_result = tool_fn.invoke(tool_call)` — **actually run the function** (this is the moment the real email gets sent!).
   - `messages.append(tool_result)` — the function's return value is wrapped in a `ToolMessage` and added to history, so the model can see what happened.

6. The loop goes back to step 2 — Gemini is called *again*, now with the tool's result included. It decides: "Do I need another tool, or can I now give a final answer?"

This `while True` loop is precisely what makes this an **agent** rather than a simple chatbot: it can take multiple actions, observe results, and decide on next steps autonomously, without you hardcoding "first do X, then do Y."

**Analogy:** think of it like a manager (you) giving an assistant (the model) a task. The assistant can't personally walk to the mailbox — it has to ask you: "please send this letter with this address and this content." You do it, tell the assistant "done," and the assistant decides whether more needs to happen or reports back to you that the task is complete.

---

## 8. Step 7–9 — Running It & Inspecting Results

The notebook then runs three real examples:

1. **Casual email** — "tell them I finished my LangChain course" → the model directly called `send_email` in one step with a subject and body it wrote itself, then confirmed back in plain English.
2. **Message history inspection** — printing out the full `messages` list shows the exact internal sequence: `HumanMessage → AIMessage (tool call) → ToolMessage (result) → AIMessage (final text)`. This is *extremely valuable* to study because it's the literal data structure every tool-calling framework passes around internally.
3. **Formal follow-up email** — interestingly, in this run the model **didn't** have enough information (it didn't know the user's name to sign the email) and instead of guessing, it asked a clarifying question back to the user. This shows good agent behavior: when required info is missing, it should ask rather than hallucinate a name.
4. **Thank-you email** — a third full run, again single tool call, straight to completion.

### Why message history inspection matters
```
[0] HumanMessage: (your instruction)
[1] AIMessage: [no text — tool call request]
      Tool: send_email | Args: {...}
[2] ToolMessage: Email successfully sent...
[3] AIMessage: (final natural-language confirmation)
```
This 4-message pattern (**ask → tool request → tool result → final answer**) is the *canonical shape* of a single-tool-call agent turn. More complex agents just repeat steps [1]-[2] multiple times before reaching a final [N] AIMessage.

---

## 9. Concept Map — Connecting Code to Theory

| Concept | Where it appears | What it means |
|---|---|---|
| `@tool` decorator | `compose_email`, `send_email`, `check_email_status` | Converts a plain function into an LLM-callable tool with auto-extracted name/description/schema |
| `tool.name` / `.description` / `.args` | Printed in Step 4 | The metadata the model actually reads to decide which tool fits the task |
| `bind_tools([...])` | Step 5 | Registers tools with the model so every request includes their schemas |
| `response.tool_calls` | Checked in the while loop | The model's structured "please run this function with these arguments" request |
| `tool_fn.invoke(tool_call)` | Step 6 | Executes the real Python code using model-provided arguments |
| `ToolMessage` | Appended after each tool runs | Feeds the tool's real-world result back into the model's context |
| Agent loop pattern | `while True` in `run_agent()` | The repeating "think → act → observe" cycle that defines an agent |

**The single most important sentence to remember from this whole project:**
> *The model never sends the email itself. It only says "call `send_email` with these args." You run it, give the result back, and the model confirms it's done. That back-and-forth **is** tool calling.*

---

## 10. Key Takeaways Before You Move to Bigger Projects

1. **Tools = functions + good docstrings.** The model's decision-making quality is only as good as your descriptions. Vague docstring → wrong tool picked, or wrong arguments guessed.
2. **The LLM is the planner, your code is the executor.** This separation is what makes agents safe and debuggable — you can always inspect and control exactly what runs.
3. **The message list is the agent's entire memory.** Nothing is remembered between calls except what's explicitly in that list — this is true of every agent framework you'll use later (LangGraph, CrewAI, OpenAI Assistants, MCP, etc.).
4. **Always handle tool errors gracefully** (return a string, don't crash) so the agent can react intelligently instead of the whole loop dying.
5. **A `while True` loop with a clean exit condition (`no tool_calls`) is the minimal recipe for any agent.** Everything more advanced (multi-agent systems, planning agents, ReAct agents) is a variation on this same loop with extra bells — memory stores, parallel tool execution, sub-agents, retries, guardrails.

### Natural next steps to build on this foundation
- Add a **confirmation step** before `send_email` actually fires (using `compose_email` as a preview, then a human types "yes, send it").
- Add more tools (e.g. `search_contacts`, `attach_file`, `schedule_email`) to see how the model juggles more choices.
- Swap Gemini for another model (OpenAI, Claude) using the same `bind_tools` pattern — LangChain makes this a near drop-in change, which is the whole point of learning the framework.
- Add persistent memory (e.g. saving `messages` to disk) so the agent can resume conversations across sessions.

---

*This explanation is meant as a reference you can revisit anytime you forget how the pieces fit together — bookmark it before moving to your next project.*
