# Agents in LangChain (Gemini Version) — Detailed Explanation Notes

This file explains every single cell of `agents_in_langchain_gemini.ipynb` line by line.

---

## Step 1 — Install Dependencies

```python
!pip install -q langchain-google-genai langchain-community langchain-core langchain requests duckduckgo-search
```

`langchain-google-genai` is the package that gives you `ChatGoogleGenerativeAI` — this replaces `langchain-openai` from the original. `langchain-community` gives you `DuckDuckGoSearchRun`. `duckduckgo-search` is the underlying library that the search tool uses internally. `requests` is used inside the custom weather tool to make HTTP calls to the Weatherstack API.

---

## Step 2 — API Keys

```python
import os
os.environ['GEMINI_API_KEY'] = 'your_gemini_api_key_here'
```

Sets the Gemini API key as an environment variable. If you have a `.env` file, you can replace this with `load_dotenv()` and `os.getenv("GEMINI_API_KEY")` — the same pattern you've been using throughout this course. The key is passed explicitly to the model in Step 5 instead of being picked up automatically, so you must set it before initialising the model.

---

## Step 3 — Imports

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
import requests
```

`ChatGoogleGenerativeAI` is the Gemini chat model. `tool` is the decorator you use to turn a Python function into a LangChain tool. `DuckDuckGoSearchRun` is a ready-made built-in tool. `create_react_agent` and `AgentExecutor` are the two functions that build and run the ReAct agent. `hub` is used to pull the standard ReAct prompt template from LangChain's public prompt registry.

---

## Step 4 — Define Tools

```python
search_tool = DuckDuckGoSearchRun()
```

This creates an instance of the DuckDuckGo search tool. No API key needed — DuckDuckGo is free. The tool has `name="duckduckgo_search"`, and its description tells the model it can use this tool to search the web for current information. The model reads the description and decides when to call it.

```python
@tool
def get_weather_data(city: str) -> str:
    """
    This function fetches the current weather data for a given city
    """
    url = f'https://api.weatherstack.com/current?access_key=4d1d8ae207a8c845a52df8a67bf3623e&query={city}'
    response = requests.get(url)
    return str(response.json())
```

The `@tool` decorator turns this into a LangChain tool. The docstring becomes `tool.description` — the model reads this to understand what the tool does. The function takes a `city` string, builds a URL for the Weatherstack API, makes a GET request, and returns the full JSON response as a string. The model provides the city name as the argument when it decides to call this tool. `return str(response.json())` converts the dict to a string because tool results must be strings to be added to the message history as `ToolMessage` objects.

---

## Step 5 — Initialise Gemini Model

```python
llm = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    google_api_key=os.environ['GEMINI_API_KEY']
)
```

This is the direct replacement for `ChatOpenAI()` from the original notebook. `gemini-2.5-flash` is used because it is fast and handles the ReAct reasoning format well. `google_api_key` is passed explicitly rather than relying on an environment variable being auto-detected. The model itself is just a chat model — it becomes an agent only when combined with tools and a ReAct prompt in the next steps.

---

## Step 6 — Pull the ReAct Prompt from LangChain Hub

```python
prompt = hub.pull('hwchase17/react')
print(prompt.input_variables)
```

`hub.pull()` downloads a pre-built prompt template from LangChain's public prompt registry. `hwchase17/react` is the standard ReAct prompt created by Harrison Chase (the creator of LangChain). This prompt is what teaches the model to follow the Thought → Action → Action Input → Observation loop.

The `input_variables` are `['agent_scratchpad', 'input', 'tool_names', 'tools']`. These are filled automatically by `AgentExecutor` at runtime — you never fill them manually. `input` is the user's question, `tools` is the list of available tools, `tool_names` is their names, and `agent_scratchpad` is where the model's ongoing reasoning gets appended as the loop runs.

This is unchanged from the original — the same ReAct prompt works with any model, whether OpenAI or Gemini.

---

## Step 7 — Create the ReAct Agent

```python
agent = create_react_agent(
    llm=llm,
    tools=[search_tool, get_weather_data],
    prompt=prompt
)
```

`create_react_agent()` combines the model, the tools, and the ReAct prompt into an agent object. This agent object knows how to format tool descriptions into the prompt, parse the model's Thought/Action/Observation output, and decide when it has reached a final answer. But it does not run yet — it is just the agent logic. The actual execution loop is handled by `AgentExecutor` in the next step.

---

## Step 8 — Wrap with AgentExecutor

```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=[search_tool, get_weather_data],
    verbose=True,
    handle_parsing_errors=True
)
```

`AgentExecutor` is the runner that actually executes the agent loop. It takes the agent and the tools and keeps running the loop — model thinks → picks a tool → tool runs → result goes back to model → model thinks again — until the model outputs a Final Answer with no more tool calls.

`verbose=True` prints every step of the reasoning process — Thought, Action, Action Input, Observation — so you can see exactly what the agent is doing internally. This is what produced the coloured output you saw in the original notebook.

`handle_parsing_errors=True` is an important addition for Gemini. Gemini sometimes formats its ReAct output slightly differently than GPT-4, which can cause the parser to fail. This flag catches those parsing errors and tells the model to try again instead of crashing the whole chain.

---

## Step 9 — Run the Agent

```python
response = agent_executor.invoke({
    'input': 'Find the capital of Madhya Pradesh, then find its current weather condition'
})
print(response['output'])
```

`.invoke()` takes a dictionary with `'input'` as the key. This is the user's question. The agent executor runs the full loop internally and returns a dictionary with `'input'` (the original question) and `'output'` (the final answer). `response['output']` gives you just the final answer string.

What happens internally for this specific query:

```
Thought: I need to find the capital of Madhya Pradesh first
Action: duckduckgo_search
Action Input: capital of Madhya Pradesh
Observation: Bhopal is the capital...

Thought: Now I need the weather for Bhopal
Action: get_weather_data
Action Input: Bhopal
Observation: {temperature: 40, weather: partly cloudy, ...}

Thought: I have everything I need
Final Answer: The capital of Madhya Pradesh is Bhopal.
              Current weather: partly cloudy, 40°C.
```

The agent used two tools in sequence — first search to find the capital, then weather to check the conditions. It figured out this sequence on its own from a single natural language instruction.

---

## Step 10 — Try More Queries

```python
response2 = agent_executor.invoke({
    'input': 'What is the capital of Tamil Nadu and what is the weather there right now?'
})
```

Same pattern as Step 9 but with a different state. The agent will first search for the capital (Chennai), then call `get_weather_data("Chennai")`. The query structure is different but the agent figures out the same two-step plan on its own.

```python
response3 = agent_executor.invoke({
    'input': 'Which city hosted IPL 2024 finals and what is the current weather in that city?'
})
```

This is a harder query — the agent doesn't know from training which city hosted IPL 2024 finals (or shouldn't assume), so it must search for that first, extract the city name from the search result, then pass that city to the weather tool. Three implicit steps from one instruction.

---

## The ReAct Loop — How It All Fits Together

ReAct stands for **Reason + Act**. The model alternates between reasoning (Thought) and acting (Action) until it has enough information to give a Final Answer.

```
User Question
      ↓
[Thought] What do I need to do first?
      ↓
[Action] tool_name
[Action Input] argument
      ↓
[Observation] tool result
      ↓
[Thought] What do I know now? What do I still need?
      ↓
[Action] another_tool  ← if more info needed
[Action Input] argument
      ↓
[Observation] tool result
      ↓
[Thought] I have everything
[Final Answer] complete response to user
```

`AgentExecutor` manages this loop. Each Observation gets appended to `agent_scratchpad` which is injected back into the prompt on the next iteration, giving the model memory of what it has already done.

---

## What Changed from the Original

| Original (OpenAI) | Converted (Gemini) |
|---|---|
| `from langchain_openai import ChatOpenAI` | `from langchain_google_genai import ChatGoogleGenerativeAI` |
| `os.environ['OPENAI_API_KEY'] = ...` | `os.environ['GEMINI_API_KEY'] = ...` |
| `llm = ChatOpenAI()` | `llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', google_api_key=...)` |
| `!pip install langchain-openai` | `!pip install langchain-google-genai` |
| No `handle_parsing_errors` | Added `handle_parsing_errors=True` for Gemini stability |

Everything else — `create_react_agent`, `AgentExecutor`, `hub.pull("hwchase17/react")`, `@tool`, `DuckDuckGoSearchRun`, `AgentExecutor.invoke()` — is **identical**. The agent framework is model-agnostic. You can swap any LangChain-compatible model in and the rest of the code stays the same.

---

## Key Concepts to Remember

`create_react_agent` builds the agent logic — it combines the model, tools, and ReAct prompt but does not run anything yet.

`AgentExecutor` is what actually runs the loop. It keeps going until the model outputs a Final Answer.

`verbose=True` is your best friend while learning — always turn it on so you can see the Thought/Action/Observation chain and understand what the agent is doing at each step.

`handle_parsing_errors=True` is essential when using Gemini with ReAct — add it every time.

`hub.pull("hwchase17/react")` is a one-line way to get the standard ReAct prompt. You don't need to write it yourself.

The `agent_scratchpad` in the prompt is what gives the agent memory within a single run — it accumulates all previous Thoughts, Actions, and Observations so the model knows what it has already done.

The difference between this and the manual tool calling loop you built earlier is that `AgentExecutor` automates the loop. Instead of writing `while True` yourself, `AgentExecutor` handles it — but the underlying mechanism is exactly the same.

Install with: `pip install langchain langchain-google-genai langchain-community langchain-core requests duckduckgo-search`
