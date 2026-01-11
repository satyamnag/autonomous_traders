# Autonomous Traders 🧠📈
### Autonomous Traders is a multi-agent trading simulation built in Python using the OpenAI Agents SDK and the Model Context Protocol (MCP) ecosystem.
### The system simulates fully autonomous stock traders that research markets, make decisions, and execute trades independently—resulting in net profits within one week of simulation.


## 🚀 Project Overview
### This project models a realistic, agent-driven trading environment where:
### ◉ Each trader operates independently
### ◉ Each trader is supported by a dedicated market researcher
### ◉ All communication, memory, data access, and execution are handled via MCP Clients, Servers, and Tools

### The project evolved from an earlier Trading Simulation Account Manager module originally generated and tested using CrewAI roles (Backend Engineer, Lead Engineer, Test Engineer), and was later extended with significant architectural improvements.


## 🤖 Autonomous Traders
### The system includes 4 unique stock traders, each following a distinct investment philosophy:

### ◉ Warren: Long-term value investing
### ◉ George: Macro & trend-based trading
### ◉ Ray: Risk-parity & diversified allocation
### ◉ Cathie: Innovation & growth-focused investing

### Each trader is paired with a dedicated Market Researcher agent that gathers, filters, and contextualizes market data before decisions are made.

# 🧩 MCP Architecture

## MCP Client (1)
### ◉ Accounts Client

## MCP Servers (8)
### ◉ Market MCP
### ◉ Accounts MCP
### ◉ Push MCP
### ◉ Yahoo Finance MCP
### ◉ CoinCap MCP
### ◉ Fetch MCP
### ◉ Google Search MCP
### ◉ LibSQL Memory MCP

## 30+ MCP Tools


## 📊 Results
### ◉ All four autonomous traders generated profits within one week of simulation
### ◉ No manual intervention after initialization
### ◉ Fully agent-driven research → decision → execution loop

# 🔐 Environment Variables
##### OPENAI_API_KEY=your openai api key
### SERPER_API_KEY=your serper api key
### MASSIVE_API_KEY=your massive api key
### DB_PATH=accounts.db
### GOOGLE_API_KEY=your google api key
### GOOGLE_SEARCH_ENGINE_ID=your google search engine ID
### PUSHOVER_USER=your pushover user ID
### PUSHOVER_TOKEN=your pushover token
### RUN_EVERY_N_MINUTES=60
### RUN_EVEN_WHEN_MARKET_IS_CLOSED=False
### TRADER_NAMES=["Warren", "George", "Ray", "Cathie"]
### INITIAL_DEPOSIT=10000.0
### PATH_TO_INDEX_DOT_JS=path to index.js inside mcp_google_custom_search_server
### COINCAP_API_KEY=your coincap api key

#-------------------------------SCREENSHOT-------------------------------

![autonomous_traders](https://github.com/satyamnag/autonomous_traders/blob/aa7add791f5269b0be29efb387a4ea3072f18ba8/assets/autonomous%20traders%20screenshot.png)




