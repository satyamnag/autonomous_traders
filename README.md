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

###        Trader                                  Strategy Style
###        Warren                                  Long-term value investing
###        George                                  Macro & trend-based trading
###        Ray                                     Risk-parity & diversified allocation
###        Cathie                                  Innovation & growth-focused investing

### Each trader is paired with a dedicated Market Researcher agent that gathers, filters, and contextualizes market data before decisions are made.

## 🧩 MCP Architecture

### MCP Client (1)
### ◉ Accounts Client

### MCP Servers (8)
### ◉ Market MCP
### ◉ MAccounts MCP
### ◉ MPush MCP
### ◉ MYahoo Finance MCP
### ◉ MCoinCap MCP
### ◉ MFetch MCP
### ◉ MGoogle Search MCP
### ◉ MLibSQL Memory MCP

### MCP Tools (30+)


## 📊 Results
### ◉ All four autonomous traders generated profits within one week of simulation
### ◉ No manual intervention after initialization
### ◉ Fully agent-driven research → decision → execution loop


#-------------------------------SCREENSHOT-------------------------------
![autonomous_traders](https://github.com/satyamnag/autonomous_traders/blob/aa7add791f5269b0be29efb387a4ea3072f18ba8/assets/autonomous%20traders%20screenshot.png)
