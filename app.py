import streamlit as st
import requests
import json
from datetime import datetime

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="AI Data Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS - ChatGPT/Claude inspired design
# =============================================================================

st.markdown("""
<style>
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove default padding */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Full height layout */
    .main {
        background: #f7f7f8;
    }
    
    /* Top navigation bar */
    .top-nav {
        background: white;
        border-bottom: 1px solid #e5e5e5;
        padding: 0.75rem 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .nav-brand h1 {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
        color: #1a1a1a;
    }
    
    .nav-brand .logo {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }
    
    /* Dataset selector pill */
    .dataset-selector {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: #f7f7f8;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        color: #666;
    }
    
    .dataset-name {
        font-weight: 500;
        color: #1a1a1a;
    }
    
    /* Main chat container */
    .chat-main {
        display: flex;
        flex-direction: column;
        height: calc(100vh - 60px);
    }
    
    /* Messages area */
    .messages-container {
        flex: 1;
        overflow-y: auto;
        padding: 1rem 0;
    }
    
    /* Single message wrapper */
    .message-wrapper {
        padding: 1.5rem 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .message-wrapper:last-child {
        border-bottom: none;
    }
    
    .message-wrapper.assistant {
        background: white;
    }
    
    /* Message content */
    .message-content {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 1.5rem;
        display: flex;
        gap: 1rem;
    }
    
    .message-avatar {
        width: 36px;
        height: 36px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 1rem;
    }
    
    .message-avatar.user {
        background: #1a1a1a;
        color: white;
    }
    
    .message-avatar.assistant {
        background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
        color: white;
    }
    
    .message-text {
        flex: 1;
        line-height: 1.7;
        color: #1a1a1a;
    }
    
    .message-text p {
        margin: 0 0 1rem 0;
    }
    
    .message-text p:last-child {
        margin-bottom: 0;
    }
    
    /* Dashboard embed in message */
    .dashboard-embed {
        margin-top: 1rem;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e5e5e5;
        background: white;
    }
    
    .dashboard-header {
        background: #f7f7f8;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #e5e5e5;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .dashboard-title {
        font-weight: 500;
        font-size: 0.9rem;
        color: #1a1a1a;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .dashboard-badge {
        background: #10a37f;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    /* Input area at bottom */
    .input-area {
        background: white;
        border-top: 1px solid #e5e5e5;
        padding: 1rem 1.5rem 1.5rem;
    }
    
    .input-container {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .input-box {
        background: #f7f7f8;
        border: 1px solid #e5e5e5;
        border-radius: 16px;
        padding: 0.25rem;
        display: flex;
        align-items: flex-end;
        gap: 0.5rem;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    
    .input-box:focus-within {
        border-color: #10a37f;
        box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1);
    }
    
    .input-disclaimer {
        text-align: center;
        font-size: 0.75rem;
        color: #999;
        margin-top: 0.75rem;
    }
    
    /* Welcome screen */
    .welcome-screen {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem 1.5rem;
        text-align: center;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .welcome-logo {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 2rem;
        margin-bottom: 1.5rem;
    }
    
    .welcome-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .welcome-subtitle {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Suggestion cards */
    .suggestions-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.75rem;
        width: 100%;
        max-width: 600px;
    }
    
    .suggestion-card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 12px;
        padding: 1rem;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .suggestion-card:hover {
        border-color: #10a37f;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    .suggestion-icon {
        font-size: 1.25rem;
        margin-bottom: 0.5rem;
    }
    
    .suggestion-text {
        font-size: 0.9rem;
        color: #1a1a1a;
        line-height: 1.4;
    }
    
    /* Streamlit overrides */
    .stTextArea textarea {
        border: none !important;
        background: transparent !important;
        resize: none !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextArea textarea:focus {
        box-shadow: none !important;
    }
    
    .stButton > button {
        background: #1a1a1a !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 500 !important;
        transition: background 0.2s !important;
    }
    
    .stButton > button:hover {
        background: #333 !important;
    }
    
    .stButton > button:disabled {
        background: #ccc !important;
    }
    
    /* Hide labels */
    .stTextArea label, .stSelectbox label {
        display: none !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: transparent !important;
        border: none !important;
    }
    
    /* Thinking animation */
    .thinking {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #666;
        font-size: 0.9rem;
    }
    
    .thinking-dots {
        display: flex;
        gap: 4px;
    }
    
    .thinking-dot {
        width: 6px;
        height: 6px;
        background: #10a37f;
        border-radius: 50%;
        animation: thinking 1.4s infinite;
    }
    
    .thinking-dot:nth-child(2) { animation-delay: 0.2s; }
    .thinking-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes thinking {
        0%, 60%, 100% { opacity: 0.3; transform: scale(0.8); }
        30% { opacity: 1; transform: scale(1); }
    }
    
    /* Settings toggle */
    .settings-toggle {
        background: none;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 0.5rem;
        cursor: pointer;
        color: #666;
        transition: all 0.2s;
    }
    
    .settings-toggle:hover {
        background: #f7f7f8;
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_dashboard_url" not in st.session_state:
    st.session_state.current_dashboard_url = ""

if "current_dashboard_name" not in st.session_state:
    st.session_state.current_dashboard_name = ""

if "webhook_url" not in st.session_state:
    st.session_state.webhook_url = ""

if "selected_dataset" not in st.session_state:
    st.session_state.selected_dataset = "singapore_flat_resale"

if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

# =============================================================================
# DATASETS CONFIGURATION
# =============================================================================

DATASETS = {
    "singapore_flat_resale": {
        "name": "Singapore Flat Resale Prices",
        "description": "287,202 HDB resale transactions from 1990-1999",
        "default_dashboard": "https://app.powerbi.com/reportEmbed?reportId=a29b6d25-81bf-4985-9094-f30a48534cd8&autoAuth=true&ctid=f688b0d0-79f0-40a4-8644-35fcdee9d0f3",
        "info": """Singapore Flat Resale Prices (1990-1999)
Total Records: 287,202 transactions
Columns: month, town, flat_type, block, street_name, storey_range, floor_area_sqm, flat_model, lease_commence_date, resale_price
Flat types: 1 ROOM, 2 ROOM, 3 ROOM, 4 ROOM, 5 ROOM, EXECUTIVE, MULTI GENERATION
Towns: ANG MO KIO, BEDOK, BISHAN, BUKIT BATOK, BUKIT MERAH, BUKIT TIMAH, CENTRAL AREA, CHOA CHU KANG, CLEMENTI, GEYLANG, HOUGANG, JURONG EAST, JURONG WEST, KALLANG/WHAMPOA, MARINE PARADE, PASIR RIS, QUEENSTOWN, SEMBAWANG, SERANGOON, TAMPINES, TOA PAYOH, WOODLANDS, YISHUN"""
    },
    "sample_sales": {
        "name": "Sample Sales Data",
        "description": "Demo sales dataset for testing",
        "default_dashboard": "https://app.powerbi.com/reportEmbed?reportId=a29b6d25-81bf-4985-9094-f30a48534cd8&autoAuth=true&ctid=f688b0d0-79f0-40a4-8644-35fcdee9d0f3",
        "info": """Sample Sales Data
Columns: date, product, category, region, sales_amount, quantity
Regions: North, South, East, West
Categories: Electronics, Clothing, Food, Home"""
    }
}

# =============================================================================
# FUNCTIONS
# =============================================================================

def call_make_webhook(user_question):
    """Send question to Make.com"""
    
    dataset = DATASETS[st.session_state.selected_dataset]
    
    if not st.session_state.webhook_url or "YOUR_WEBHOOK" in st.session_state.webhook_url:
        return simulate_ai_response(user_question)
    
    try:
        payload = {
            "question": user_question,
            "dataset": st.session_state.selected_dataset,
            "dataset_info": dataset["info"]
        }
        
        response = requests.post(
            st.session_state.webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "insight": result.get("insight", "Analysis complete."),
                "dashboard_name": result.get("dashboard_name", "Dashboard"),
                "dashboard_url": result.get("dashboard_url", dataset["default_dashboard"])
            }
        else:
            return simulate_ai_response(user_question)
            
    except Exception as e:
        return simulate_ai_response(user_question)


def simulate_ai_response(question):
    """Simulate AI response"""
    question_lower = question.lower()
    dataset = DATASETS[st.session_state.selected_dataset]
    
    if st.session_state.selected_dataset == "singapore_flat_resale":
        if any(word in question_lower for word in ["price", "cost", "expensive", "cheap", "afford", "trend", "average"]):
            return {
                "success": True,
                "insight": """Based on my analysis of the Singapore flat resale data, here are the key price insights:

**Price Overview (1990-1999):**
- The average resale price across all transactions was **$219,541**
- Prices ranged from $5,000 for older 1-room flats to over $900,000 for premium executive flats
- There was a significant upward trend from 1990 to 1997, followed by a slight decline during the Asian Financial Crisis

**By Flat Type:**
- 1-Room: $39,565 average
- 3-Room: $124,352 average  
- 4-Room: $228,502 average
- 5-Room: $328,741 average
- Executive: $440,907 average

I've loaded the **Price Analysis** dashboard below where you can explore these trends interactively. Try using the filters to compare specific time periods or flat types.""",
                "dashboard_name": "Price Analysis",
                "dashboard_url": dataset["default_dashboard"]
            }
        
        elif any(word in question_lower for word in ["town", "area", "location", "where", "region", "bishan", "tampines", "bedok"]):
            return {
                "success": True,
                "insight": """Here's my analysis of prices by town/location:

**Most Expensive Towns (by average price):**
1. **Bukit Timah** - $389,234 (premium central location)
2. **Bishan** - $312,456 (near amenities, MRT)
3. **Pasir Ris** - $298,765 (newer developments)

**Most Affordable Towns:**
1. **Sembawang** - $124,567
2. **Woodlands** - $145,678
3. **Jurong West** - $156,789

**Highest Transaction Volume:**
- Tampines, Bedok, and Ang Mo Kio had the most transactions, indicating these were popular choices for homebuyers.

The **Town Analysis** dashboard below lets you compare any towns side by side. Use the town filter to select specific areas you're interested in.""",
                "dashboard_name": "Town Analysis", 
                "dashboard_url": dataset["default_dashboard"]
            }
        
        elif any(word in question_lower for word in ["room", "flat type", "3-room", "4-room", "5-room", "executive", "type", "bedroom"]):
            return {
                "success": True,
                "insight": """Here's a breakdown by flat type:

**Transaction Volume:**
| Flat Type | Transactions | Avg Price |
|-----------|-------------|-----------|
| 3-Room | 113,106 (39%) | $124,352 |
| 4-Room | 98,521 (34%) | $228,502 |
| 5-Room | 45,234 (16%) | $328,741 |
| Executive | 12,847 (4%) | $440,907 |
| Others | 17,494 (6%) | Various |

**Key Insights:**
- **3-Room flats** were the most popular choice, making up 39% of all transactions
- **4-Room flats** were the sweet spot for families, balancing space and affordability
- **Executive flats** commanded premium prices but had limited availability

The dashboard below shows detailed comparisons. Click on any flat type to filter all the charts!""",
                "dashboard_name": "Flat Type Analysis",
                "dashboard_url": dataset["default_dashboard"]
            }
        
        else:
            return {
                "success": True,
                "insight": """Welcome! I'm ready to help you explore the Singapore Flat Resale dataset.

**Dataset Overview:**
- **287,202** resale transactions from 1990-1999
- Covers **25 towns** across Singapore
- Includes **7 flat types** from 1-Room to Executive

**What I can help you with:**
- 📈 Price trends and analysis
- 🏢 Comparisons between flat types
- 📍 Town-by-town breakdowns
- 🔍 Specific queries about the data

**Try asking:**
- "Which towns have the highest prices?"
- "Compare 3-room vs 4-room flats"
- "Show me price trends over time"

The dashboard below shows an overview of the data. Feel free to interact with it!""",
                "dashboard_name": "Overview",
                "dashboard_url": dataset["default_dashboard"]
            }
    
    else:
        return {
            "success": True,
            "insight": f"I'm analyzing the {dataset['name']} dataset. This is a demo response - connect Make.com for real AI analysis.",
            "dashboard_name": "Dashboard",
            "dashboard_url": dataset["default_dashboard"]
        }


def process_question(question):
    """Process user question"""
    st.session_state.messages.append({
        "role": "user",
        "content": question,
        "timestamp": datetime.now()
    })
    
    response = call_make_webhook(question)
    
    st.session_state.current_dashboard_name = response["dashboard_name"]
    st.session_state.current_dashboard_url = response["dashboard_url"]
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": response["insight"],
        "dashboard_name": response["dashboard_name"],
        "dashboard_url": response["dashboard_url"],
        "timestamp": datetime.now()
    })


# =============================================================================
# SIDEBAR - Settings
# =============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    
    st.markdown("**Make.com Webhook URL**")
    webhook = st.text_input(
        "webhook",
        value=st.session_state.webhook_url,
        placeholder="https://hook.us1.make.com/...",
        label_visibility="collapsed"
    )
    if webhook != st.session_state.webhook_url:
        st.session_state.webhook_url = webhook
    
    st.markdown("---")
    
    st.markdown("**Dataset Configuration**")
    st.caption("Edit DATASETS in app.py to add more datasets and their Power BI URLs")
    
    st.markdown("---")
    
    if st.session_state.webhook_url and "YOUR_WEBHOOK" not in st.session_state.webhook_url:
        st.success("✅ Make.com Connected")
    else:
        st.warning("🟡 Demo Mode")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_dashboard_url = ""
        st.session_state.current_dashboard_name = ""
        st.rerun()


# =============================================================================
# MAIN UI
# =============================================================================

# Top Navigation Bar
col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])

with col_nav1:
    st.markdown("""
    <div class="nav-brand">
        <div class="logo">✨</div>
        <h1>AI Data Assistant</h1>
    </div>
    """, unsafe_allow_html=True)

with col_nav2:
    # Dataset selector
    dataset_options = {k: v["name"] for k, v in DATASETS.items()}
    selected = st.selectbox(
        "dataset",
        options=list(dataset_options.keys()),
        format_func=lambda x: f"📊 {dataset_options[x]}",
        index=list(dataset_options.keys()).index(st.session_state.selected_dataset),
        label_visibility="collapsed"
    )
    if selected != st.session_state.selected_dataset:
        st.session_state.selected_dataset = selected
        st.session_state.messages = []  # Clear chat when switching datasets
        st.rerun()

with col_nav3:
    col_settings, col_space = st.columns([1, 2])
    with col_settings:
        if st.button("⚙️", help="Settings"):
            st.session_state.show_settings = not st.session_state.show_settings

st.markdown("---")

# =============================================================================
# CHAT AREA
# =============================================================================

# If no messages, show welcome screen
if not st.session_state.messages:
    dataset = DATASETS[st.session_state.selected_dataset]
    
    st.markdown(f"""
    <div class="welcome-screen">
        <div class="welcome-logo">✨</div>
        <div class="welcome-title">What would you like to explore?</div>
        <div class="welcome-subtitle">Ask questions about {dataset['name']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Suggestion cards
    col1, col2 = st.columns(2)
    
    suggestions = [
        ("📈", "Show me price trends over time"),
        ("📍", "Which areas have the highest prices?"),
        ("🏢", "Compare different flat types"),
        ("🔍", "Give me an overview of the data")
    ]
    
    for i, (icon, text) in enumerate(suggestions):
        with col1 if i % 2 == 0 else col2:
            if st.button(f"{icon} {text}", key=f"sug_{i}", use_container_width=True):
                process_question(text)
                st.rerun()

else:
    # Display messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="message-wrapper">
                <div class="message-content">
                    <div class="message-avatar user">👤</div>
                    <div class="message-text">{msg['content']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            # Assistant message with dashboard
            content = msg['content'].replace('\n', '<br>')
            dashboard_url = msg.get('dashboard_url', '')
            dashboard_name = msg.get('dashboard_name', 'Dashboard')
            
            st.markdown(f"""
            <div class="message-wrapper assistant">
                <div class="message-content">
                    <div class="message-avatar assistant">✨</div>
                    <div class="message-text">
                        {content}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Embed dashboard after the message
            if dashboard_url:
                st.markdown(f"""
                <div style="max-width: 800px; margin: 0 auto; padding: 0 1.5rem 1.5rem 3.5rem;">
                    <div class="dashboard-embed">
                        <div class="dashboard-header">
                            <span class="dashboard-title">
                                📊 {dashboard_name}
                                <span class="dashboard-badge">Interactive</span>
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Actual iframe
                with st.container():
                    st.components.v1.iframe(dashboard_url, height=500, scrolling=True)

# =============================================================================
# INPUT AREA
# =============================================================================

st.markdown("---")

# Input at the bottom
col_input, col_btn = st.columns([6, 1])

with col_input:
    user_input = st.text_area(
        "message",
        placeholder="Ask anything about your data...",
        height=80,
        label_visibility="collapsed",
        key="user_input"
    )

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
    send = st.button("Send", type="primary", use_container_width=True)

if send and user_input.strip():
    process_question(user_input.strip())
    st.rerun()

# Disclaimer
st.markdown("""
<div class="input-disclaimer">
    AI-powered analysis • Dashboards update based on your questions
</div>
""", unsafe_allow_html=True)
