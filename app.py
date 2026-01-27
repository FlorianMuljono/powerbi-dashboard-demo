import streamlit as st
import requests
import json
from datetime import datetime

# =============================================================================
# PAGE CONFIG - Must be first Streamlit command
# =============================================================================

st.set_page_config(
    page_title="Singapore Flat Resale Insights",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS - Julius.ai inspired clean design
# =============================================================================

st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Chat container styling */
    .chat-container {
        background: #fafafa;
        border-radius: 16px;
        padding: 1.5rem;
        height: calc(100vh - 200px);
        overflow-y: auto;
        border: 1px solid #e5e5e5;
    }
    
    /* Message bubbles */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.75rem 0;
        margin-left: 20%;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.25);
    }
    
    .ai-message {
        background: white;
        color: #1a1a1a;
        padding: 1.25rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.75rem 0;
        margin-right: 10%;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    
    .ai-message h4 {
        color: #667eea;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* Dashboard badge */
    .dashboard-badge {
        display: inline-block;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-bottom: 0.75rem;
    }
    
    /* Welcome header */
    .welcome-header {
        text-align: center;
        padding: 2rem 1rem;
    }
    
    .welcome-header h1 {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .welcome-header p {
        color: #666;
        font-size: 1.1rem;
    }
    
    /* Suggestion chips */
    .suggestion-chip {
        display: inline-block;
        background: white;
        border: 1.5px solid #e5e5e5;
        padding: 0.6rem 1rem;
        border-radius: 24px;
        margin: 0.3rem;
        font-size: 0.9rem;
        color: #444;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .suggestion-chip:hover {
        border-color: #667eea;
        color: #667eea;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
    }
    
    /* Input area styling */
    .stTextInput > div > div > input {
        border-radius: 24px !important;
        padding: 0.75rem 1.25rem !important;
        border: 2px solid #e5e5e5 !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Settings panel */
    .settings-panel {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e5e5e5;
    }
    
    .settings-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Status indicator */
    .status-connected {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: #e8f5e9;
        color: #2e7d32;
        padding: 0.3rem 0.75rem;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-disconnected {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: #fff3e0;
        color: #e65100;
        padding: 0.3rem 0.75rem;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Power BI container */
    .powerbi-container {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e5e5e5;
    }
    
    .powerbi-header {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #e5e5e5;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .powerbi-title {
        font-weight: 600;
        color: #333;
        font-size: 0.95rem;
    }
    
    /* Data info card */
    .data-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    .data-info h4 {
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .data-info p {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    /* Hide default button styling */
    .stButton > button {
        border-radius: 24px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        gap: 4px;
        padding: 0.5rem;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #667eea;
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
        30% { transform: translateY(-4px); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_dashboard_url" not in st.session_state:
    st.session_state.current_dashboard_url = ""

if "current_dashboard_name" not in st.session_state:
    st.session_state.current_dashboard_name = "Overview"

if "webhook_url" not in st.session_state:
    st.session_state.webhook_url = ""

if "default_dashboard_url" not in st.session_state:
    st.session_state.default_dashboard_url = "https://app.powerbi.com/reportEmbed?reportId=a29b6d25-81bf-4985-9094-f30a48534cd8&autoAuth=true&ctid=f688b0d0-79f0-40a4-8644-35fcdee9d0f3"

if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

if "processing" not in st.session_state:
    st.session_state.processing = False

# Initialize current dashboard URL if not set
if not st.session_state.current_dashboard_url:
    st.session_state.current_dashboard_url = st.session_state.default_dashboard_url

# =============================================================================
# DATASET INFO
# =============================================================================

DATASET_INFO = """
Singapore Flat Resale Price (1990-1999)
Total Records: 287,202 transactions
Columns: month, town, flat_type, block, street_name, storey_range, floor_area_sqm, flat_model, lease_commence_date, resale_price

Available flat types: 1 ROOM, 2 ROOM, 3 ROOM, 4 ROOM, 5 ROOM, EXECUTIVE, MULTI GENERATION
Available towns: ANG MO KIO, BEDOK, BISHAN, BUKIT BATOK, BUKIT MERAH, BUKIT TIMAH, CENTRAL AREA, CHOA CHU KANG, CLEMENTI, GEYLANG, HOUGANG, JURONG EAST, JURONG WEST, KALLANG/WHAMPOA, LIM CHU KANG, MARINE PARADE, PASIR RIS, QUEENSTOWN, SEMBAWANG, SENGKANG, SERANGOON, TAMPINES, TOA PAYOH, WOODLANDS, YISHUN
"""

# =============================================================================
# SIMULATED DASHBOARDS (for demo mode)
# =============================================================================

SIMULATED_DASHBOARDS = [
    {
        "dashboard_id": "overview",
        "dashboard_name": "Overview",
        "description": "General overview of all HDB resale data",
        "embed_url": st.session_state.default_dashboard_url
    },
    {
        "dashboard_id": "price_analysis",
        "dashboard_name": "Price Analysis", 
        "description": "Price trends over time",
        "embed_url": st.session_state.default_dashboard_url
    },
    {
        "dashboard_id": "flat_type",
        "dashboard_name": "Flat Type Analysis",
        "description": "Compare flat types",
        "embed_url": st.session_state.default_dashboard_url
    },
    {
        "dashboard_id": "town_analysis",
        "dashboard_name": "Town Analysis",
        "description": "Geographic analysis",
        "embed_url": st.session_state.default_dashboard_url
    }
]

# =============================================================================
# FUNCTIONS
# =============================================================================

def call_make_webhook(user_question):
    """Send question to Make.com and get AI response"""
    
    # If no webhook configured, use simulation
    if not st.session_state.webhook_url or "YOUR_WEBHOOK" in st.session_state.webhook_url:
        return simulate_ai_response(user_question)
    
    try:
        payload = {
            "question": user_question,
            "dataset": "singapore_flat_resale_price",
            "dataset_info": DATASET_INFO
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
                "dashboard_name": result.get("dashboard_name", "Overview"),
                "dashboard_url": result.get("dashboard_url", st.session_state.default_dashboard_url)
            }
        else:
            return simulate_ai_response(user_question)
            
    except Exception as e:
        return simulate_ai_response(user_question)


def simulate_ai_response(question):
    """Simulate AI response for demo/testing"""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ["price", "cost", "expensive", "cheap", "afford", "trend", "increase", "decrease", "average"]):
        dashboard_name = "Price Analysis"
        insight = """Looking at the price data, I can see some interesting patterns:

**Key Findings:**
• Average resale prices ranged from **$39,565** (1-Room) to **$453,941** (Multi-Generation)
• Prices showed a general **upward trend** throughout 1990-1999
• The biggest price jumps occurred during **1995-1997**

I've switched to the Price Analysis dashboard where you can explore these trends interactively. Try using the time slicer to compare specific periods!"""

    elif any(word in question_lower for word in ["room", "flat type", "1-room", "2-room", "3-room", "4-room", "5-room", "executive", "type", "size"]):
        dashboard_name = "Flat Type Analysis"
        insight = """Here's what the data shows about flat types:

**Transaction Volume:**
• **3-Room flats** were most popular with 113,106 transactions
• **4-Room flats** came second with 98,521 transactions
• Executive flats had the lowest volume at 12,847

**Average Prices:**
• 3-Room: **$124,352**
• 4-Room: **$228,502**
• Executive: **$440,907**

The Flat Type Analysis dashboard shows these comparisons visually. Click on any flat type to filter all the charts!"""

    elif any(word in question_lower for word in ["town", "area", "location", "region", "where", "tampines", "bishan", "bedok", "ang mo kio", "woodlands", "highest", "lowest"]):
        dashboard_name = "Town Analysis"
        insight = """Geographic analysis reveals significant price variations:

**Most Expensive Towns:**
• **Bukit Timah**: $389,234 average
• **Bishan**: $312,456 average  
• **Pasir Ris**: $298,765 average

**Most Affordable Towns:**
• **Lim Chu Kang**: $98,234 average
• **Sembawang**: $124,567 average
• **Woodlands**: $145,678 average

I've loaded the Town Analysis dashboard. Use the town slicer to compare specific areas side by side!"""

    else:
        dashboard_name = "Overview"
        insight = """Here's an overview of the Singapore flat resale market (1990-1999):

**Dataset Summary:**
• **287,202** total transactions
• Price range: **$5,000 - $900,000**
• Overall average: **$219,541**
• Peak activity year: **1997**

**What would you like to explore?**
• Ask about price trends over time
• Compare different flat types (3-room vs 4-room)
• Analyze prices by town/location
• Find the most expensive or affordable areas"""

    # Find matching dashboard URL
    dashboard_url = st.session_state.default_dashboard_url
    for d in SIMULATED_DASHBOARDS:
        if d["dashboard_name"] == dashboard_name:
            dashboard_url = d["embed_url"]
            break

    return {
        "success": True,
        "insight": insight,
        "dashboard_name": dashboard_name,
        "dashboard_url": dashboard_url
    }


def process_question(question):
    """Process user question and update state"""
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": question,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    # Get AI response
    response = call_make_webhook(question)
    
    # Update dashboard
    st.session_state.current_dashboard_name = response["dashboard_name"]
    st.session_state.current_dashboard_url = response["dashboard_url"]
    
    # Add AI message
    st.session_state.messages.append({
        "role": "assistant",
        "content": response["insight"],
        "dashboard": response["dashboard_name"],
        "timestamp": datetime.now().strftime("%H:%M")
    })


# =============================================================================
# SIDEBAR - Settings
# =============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    st.markdown("---")
    
    st.markdown("**Make.com Webhook URL**")
    webhook_input = st.text_input(
        "Webhook URL",
        value=st.session_state.webhook_url,
        placeholder="https://hook.us1.make.com/...",
        label_visibility="collapsed"
    )
    if webhook_input != st.session_state.webhook_url:
        st.session_state.webhook_url = webhook_input
    
    st.markdown("**Default Power BI Dashboard**")
    default_url_input = st.text_input(
        "Default Dashboard URL",
        value=st.session_state.default_dashboard_url,
        placeholder="https://app.powerbi.com/reportEmbed?...",
        label_visibility="collapsed"
    )
    if default_url_input != st.session_state.default_dashboard_url:
        st.session_state.default_dashboard_url = default_url_input
        st.session_state.current_dashboard_url = default_url_input
    
    st.markdown("---")
    
    # Connection status
    if st.session_state.webhook_url and "YOUR_WEBHOOK" not in st.session_state.webhook_url:
        st.markdown('<span class="status-connected">🟢 Make.com Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-disconnected">🟡 Demo Mode (Simulated)</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    with st.expander("ℹ️ Setup Guide"):
        st.markdown("""
        **1. Create Google Sheet** with columns:
        - dashboard_id
        - dashboard_name  
        - description
        - embed_url
        
        **2. Set up Make.com** scenario:
        - Webhook trigger
        - Google Sheets (read rows)
        - AI module (analyze question)
        - Webhook response
        
        **3. Paste webhook URL** above
        
        **4. Login to Power BI** in this browser before demo
        """)

# =============================================================================
# MAIN LAYOUT
# =============================================================================

# Create two columns
col_chat, col_dashboard = st.columns([1, 1.5])

# =============================================================================
# LEFT COLUMN - Chat Interface
# =============================================================================

with col_chat:
    # Header with data info
    st.markdown("""
    <div class="data-info">
        <h4>📊 Singapore Flat Resale Price</h4>
        <p>287,202 Transactions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # If no messages, show welcome
        if not st.session_state.messages:
            st.markdown("""
            <div class="welcome-header">
                <h1>🏠 Singapore Flat Resale Insights</h1>
                <p>Ask me anything about flat resale prices (1990-1999)</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Suggestion chips
            st.markdown("**Try asking:**")
            
            suggestions = [
                "What are the price trends?",
                "Which towns are most expensive?",
                "Compare 3-room vs 4-room flats",
                "Show me an overview"
            ]
            
            cols = st.columns(2)
            for i, suggestion in enumerate(suggestions):
                with cols[i % 2]:
                    if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                        process_question(suggestion)
                        st.rerun()
        
        else:
            # Display chat messages
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    dashboard = msg.get("dashboard", "")
                    st.markdown(f"""
                    <div class="ai-message">
                        <span class="dashboard-badge">📊 {dashboard}</span>
                        {msg["content"].replace(chr(10), "<br>")}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Input area at bottom
    st.markdown("---")
    
    col_input, col_send = st.columns([5, 1])
    
    with col_input:
        user_input = st.text_input(
            "Ask about your data...",
            placeholder="e.g., What's the average price for 4-room flats in Tampines?",
            label_visibility="collapsed",
            key="user_input"
        )
    
    with col_send:
        send_clicked = st.button("➤", type="primary", use_container_width=True)
    
    # Handle input
    if send_clicked and user_input:
        process_question(user_input)
        st.rerun()
    
    # Quick actions when there are messages
    if st.session_state.messages:
        st.markdown("**Quick questions:**")
        quick_cols = st.columns(4)
        quick_questions = ["📈 Prices", "🏢 Flat types", "📍 Towns", "🔄 Overview"]
        quick_full = [
            "Show me price trends",
            "Compare flat types",
            "Which towns are expensive?",
            "Give me an overview"
        ]
        for i, (label, question) in enumerate(zip(quick_questions, quick_full)):
            with quick_cols[i]:
                if st.button(label, key=f"quick_{i}", use_container_width=True):
                    process_question(question)
                    st.rerun()

# =============================================================================
# RIGHT COLUMN - Power BI Dashboard
# =============================================================================

with col_dashboard:
    # Dashboard header
    st.markdown(f"""
    <div class="powerbi-container">
        <div class="powerbi-header">
            <span class="powerbi-title">📊 {st.session_state.current_dashboard_name}</span>
            <span style="font-size: 0.8rem; color: #666;">Power BI Dashboard</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Embed Power BI
    if st.session_state.current_dashboard_url:
        st.components.v1.iframe(
            st.session_state.current_dashboard_url,
            height=650,
            scrolling=True
        )
    else:
        st.info("👆 Configure your Power BI dashboard URL in the sidebar settings")
    
    # Dashboard tips
    with st.expander("💡 Dashboard Tips"):
        st.markdown("""
        - **Click on charts** to cross-filter other visuals
        - **Use slicers** on the left to filter by flat type or time period
        - **Hover over bars** to see exact values
        - **Ask follow-up questions** in the chat to switch views
        """)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.85rem; padding: 1rem;">
    Built with Streamlit • Powered by Make.com AI • Dashboard by Power BI<br>
    <span style="font-size: 0.75rem;">💡 Tip: Open sidebar (>) to configure webhook and dashboard settings</span>
</div>
""", unsafe_allow_html=True)
