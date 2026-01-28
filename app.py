import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

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
# CUSTOM CSS - Julius.ai inspired clean design
# =============================================================================

st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 900px;
        margin: 0 auto;
    }
    
    /* Background */
    .stApp {
        background: linear-gradient(180deg, #fafafa 0%, #f5f5f7 100%);
    }
    
    /* Welcome header */
    .welcome-container {
        text-align: center;
        padding: 4rem 2rem 3rem;
    }
    
    .welcome-icon {
        width: 72px;
        height: 72px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 36px;
        box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);
    }
    
    .welcome-title {
        font-size: 2.25rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .welcome-subtitle {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    
    /* Dataset selector cards */
    .dataset-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        max-width: 600px;
        margin: 0 auto 2rem;
    }
    
    .dataset-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
    }
    
    .dataset-card:hover {
        border-color: #6366f1;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
        transform: translateY(-2px);
    }
    
    .dataset-card.selected {
        border-color: #6366f1;
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
    }
    
    .dataset-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
    }
    
    .dataset-name {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0.25rem;
    }
    
    .dataset-desc {
        font-size: 0.85rem;
        color: #64748b;
    }
    
    /* Chat messages */
    .message-container {
        margin-bottom: 1.5rem;
    }
    
    .user-message {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 4px 18px;
        margin-left: 20%;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        line-height: 1.5;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
    }
    
    .assistant-message {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 1.25rem 1.5rem;
        border-radius: 18px 18px 18px 4px;
        margin-right: 10%;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        line-height: 1.7;
        color: #334155;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
    }
    
    .assistant-message strong {
        color: #1a1a2e;
    }
    
    /* Summary card */
    .summary-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
    }
    
    .summary-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .summary-icon {
        font-size: 1.5rem;
    }
    
    .summary-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
    }
    
    .summary-content {
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    
    /* Suggestion chips */
    .suggestions-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .suggestion-chip {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        color: #475569;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .suggestion-chip:hover {
        background: #f1f5f9;
        border-color: #6366f1;
        color: #6366f1;
    }
    
    /* Input area */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(0deg, #fafafa 80%, transparent 100%);
        padding: 1rem 2rem 2rem;
    }
    
    .input-box {
        max-width: 800px;
        margin: 0 auto;
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 0.5rem;
        display: flex;
        align-items: flex-end;
        gap: 0.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: border-color 0.2s;
    }
    
    .input-box:focus-within {
        border-color: #6366f1;
    }
    
    /* Streamlit overrides */
    .stTextArea textarea {
        font-family: 'DM Sans', sans-serif !important;
        border: none !important;
        background: transparent !important;
        font-size: 0.95rem !important;
        resize: none !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextArea textarea:focus {
        box-shadow: none !important;
    }
    
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Follow-up questions */
    .followup-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Thinking indicator */
    .thinking {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #64748b;
        font-size: 0.9rem;
        padding: 1rem;
    }
    
    .thinking-dot {
        width: 8px;
        height: 8px;
        background: #6366f1;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.4; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1); }
    }
    
    /* Dashboard placeholder */
    .dashboard-placeholder {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .dashboard-placeholder-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .dashboard-placeholder-text {
        color: #64748b;
        font-size: 0.95rem;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    
    /* Hide default streamlit elements */
    .stDeployButton {display: none;}
    div[data-testid="stToolbar"] {display: none;}
    div[data-testid="stDecoration"] {display: none;}
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    
    .stSelectbox > div > div:focus {
        border-color: #6366f1 !important;
    }
    
    /* Add bottom padding for fixed input */
    .main-content {
        padding-bottom: 120px;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_dataset" not in st.session_state:
    st.session_state.selected_dataset = None

if "dataset_summary" not in st.session_state:
    st.session_state.dataset_summary = None

if "stats_data" not in st.session_state:
    st.session_state.stats_data = None

if "datasets_info" not in st.session_state:
    st.session_state.datasets_info = None

# =============================================================================
# GOOGLE SHEETS FUNCTIONS
# =============================================================================

@st.cache_data(ttl=300)
def load_google_sheet_data(sheet_id, tab_name):
    """Load data from a public Google Sheet tab"""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={tab_name}"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading {tab_name}: {e}")
        return None

def get_datasets():
    """Get list of datasets from Google Sheet"""
    try:
        sheet_id = st.secrets["GOOGLE_SHEET_ID"]
        df = load_google_sheet_data(sheet_id, "Datasets")
        if df is not None:
            return df.to_dict('records')
    except Exception as e:
        st.error(f"Error loading datasets: {e}")
    return []

def get_stats(dataset_id):
    """Get stats for a specific dataset"""
    try:
        sheet_id = st.secrets["GOOGLE_SHEET_ID"]
        df = load_google_sheet_data(sheet_id, "Stats")
        if df is not None:
            filtered = df[df['dataset_id'] == dataset_id]
            return filtered.to_dict('records')
    except Exception as e:
        st.error(f"Error loading stats: {e}")
    return []

def get_dashboards(dataset_id):
    """Get dashboards for a specific dataset"""
    try:
        sheet_id = st.secrets["GOOGLE_SHEET_ID"]
        df = load_google_sheet_data(sheet_id, "Dashboards")
        if df is not None:
            filtered = df[df['dataset_id'] == dataset_id]
            return filtered.to_dict('records')
    except Exception as e:
        st.error(f"Error loading dashboards: {e}")
    return []

# =============================================================================
# DEEPSEEK API FUNCTIONS
# =============================================================================

def call_deepseek(messages, system_prompt):
    """Call DeepSeek API"""
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
        
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error calling DeepSeek: {str(e)}"

def format_stats_for_prompt(stats):
    """Format stats into a readable string for the AI prompt"""
    if not stats:
        return "No statistics available."
    
    formatted = []
    current_category = None
    
    for stat in stats:
        category = stat.get('stat_category', 'general')
        if category != current_category:
            current_category = category
            formatted.append(f"\n## {category.upper()}")
        formatted.append(f"- {stat.get('stat_name', 'N/A')}: {stat.get('stat_value', 'N/A')}")
    
    return "\n".join(formatted)

def get_ai_response(user_question, dataset_name, stats):
    """Get AI response for a user question"""
    
    stats_text = format_stats_for_prompt(stats)
    
    system_prompt = f"""You are an expert data analyst assistant helping users understand the "{dataset_name}" dataset.

## Available Statistics:
{stats_text}

## Your Role:
1. Answer questions using ONLY the statistics provided above
2. Be specific - use actual numbers from the stats
3. Provide actionable insights, not just facts
4. If asked to create a chart, respond with a JSON code block containing chart specifications

## Response Format:
- For text insights: Respond naturally with clear explanations
- For charts: Include a JSON block with chart type and data
- Always end with 2-3 suggested follow-up questions

## Chart JSON Format (when charts are requested):
```json
{{
    "chart_type": "bar|line|pie|scatter",
    "title": "Chart Title",
    "data": {{"labels": [...], "values": [...]}},
    "x_label": "X Axis Label",
    "y_label": "Y Axis Label"
}}
```

## Important:
- Be conversational and helpful
- Highlight key insights and patterns
- If you can't answer from the stats, say so
- Suggest visualizations when relevant"""

    messages = [{"role": "user", "content": user_question}]
    
    return call_deepseek(messages, system_prompt)

def parse_chart_from_response(response):
    """Extract chart JSON from AI response if present"""
    # Look for JSON code block
    json_pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(json_pattern, response, re.DOTALL)
    
    if matches:
        try:
            chart_data = json.loads(matches[0])
            return chart_data
        except json.JSONDecodeError:
            pass
    return None

def create_chart(chart_data):
    """Create a Plotly chart from chart data"""
    chart_type = chart_data.get("chart_type", "bar")
    title = chart_data.get("title", "Chart")
    data = chart_data.get("data", {})
    labels = data.get("labels", [])
    values = data.get("values", [])
    x_label = chart_data.get("x_label", "")
    y_label = chart_data.get("y_label", "")
    
    if chart_type == "bar":
        fig = px.bar(x=labels, y=values, title=title)
        fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
    elif chart_type == "line":
        fig = px.line(x=labels, y=values, title=title, markers=True)
        fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
    elif chart_type == "pie":
        fig = px.pie(names=labels, values=values, title=title)
    elif chart_type == "scatter":
        fig = px.scatter(x=labels, y=values, title=title)
        fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
    else:
        fig = px.bar(x=labels, y=values, title=title)
    
    # Apply consistent styling
    fig.update_layout(
        font_family="DM Sans",
        title_font_size=16,
        title_font_color="#1a1a2e",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=50, l=50, r=30, b=50)
    )
    fig.update_traces(marker_color="#6366f1")
    
    return fig

def extract_followup_questions(response):
    """Extract follow-up questions from AI response"""
    questions = []
    lines = response.split('\n')
    
    for line in lines:
        line = line.strip()
        # Look for numbered questions or bullet points
        if re.match(r'^[\d\.\-\*\•]\s*.*\?', line):
            # Clean up the question
            question = re.sub(r'^[\d\.\-\*\•]\s*', '', line).strip()
            if len(question) > 10:
                questions.append(question)
    
    return questions[:3]  # Return max 3 questions

# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_welcome_screen():
    """Render the welcome/dataset selection screen"""
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-icon">✨</div>
        <div class="welcome-title">What do you want to analyze today?</div>
        <div class="welcome-subtitle">Select a dataset to get started</div>
    </div>
    """, unsafe_allow_html=True)

def render_dataset_cards(datasets):
    """Render dataset selection cards"""
    icons = {"sg_flat": "🏠", "nz_airbnb": "🏡"}
    
    cols = st.columns(2)
    for i, dataset in enumerate(datasets):
        with cols[i % 2]:
            icon = icons.get(dataset['dataset_id'], '📊')
            if st.button(
                f"{icon} {dataset['dataset_name']}",
                key=f"dataset_{dataset['dataset_id']}",
                use_container_width=True
            ):
                st.session_state.selected_dataset = dataset['dataset_id']
                st.session_state.dataset_summary = dataset['summary']
                st.session_state.messages = []
                st.rerun()

def render_summary_card(dataset_name, summary):
    """Render the dataset summary card"""
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-header">
            <span class="summary-icon">📊</span>
            <span class="summary-title">{dataset_name}</span>
        </div>
        <div class="summary-content">{summary}</div>
    </div>
    """, unsafe_allow_html=True)

def render_message(role, content):
    """Render a chat message"""
    if role == "user":
        st.markdown(f'<div class="user-message">{content}</div>', unsafe_allow_html=True)
    else:
        # Remove JSON code blocks from display
        display_content = re.sub(r'```json\s*.*?\s*```', '', content, flags=re.DOTALL)
        display_content = display_content.strip()
        
        # Convert markdown-style formatting
        display_content = display_content.replace('\n', '<br>')
        
        st.markdown(f'<div class="assistant-message">{display_content}</div>', unsafe_allow_html=True)

def render_suggestions(questions):
    """Render follow-up question suggestions"""
    if questions:
        st.markdown('<div class="followup-title">Suggested questions</div>', unsafe_allow_html=True)
        cols = st.columns(len(questions))
        for i, q in enumerate(questions):
            with cols[i]:
                if st.button(q[:50] + "..." if len(q) > 50 else q, key=f"suggestion_{i}"):
                    return q
    return None

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    # Load datasets
    datasets = get_datasets()
    
    # Main content area
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # =========================================================================
    # SCREEN 1: Dataset Selection
    # =========================================================================
    if st.session_state.selected_dataset is None:
        render_welcome_screen()
        
        if datasets:
            render_dataset_cards(datasets)
        else:
            st.warning("Unable to load datasets. Please check your Google Sheet configuration.")
    
    # =========================================================================
    # SCREEN 2: Chat Interface
    # =========================================================================
    else:
        # Get current dataset info
        current_dataset = next(
            (d for d in datasets if d['dataset_id'] == st.session_state.selected_dataset),
            None
        )
        
        if current_dataset:
            # Header with dataset name and back button
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"### 📊 {current_dataset['dataset_name']}")
            with col2:
                if st.button("← Back"):
                    st.session_state.selected_dataset = None
                    st.session_state.messages = []
                    st.rerun()
            
            # Show summary if no messages yet
            if not st.session_state.messages:
                render_summary_card(
                    current_dataset['dataset_name'],
                    current_dataset['summary']
                )
                
                st.markdown("""
                <div style="text-align: center; color: #64748b; margin: 2rem 0;">
                    <p>What insights are you looking for?</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Initial suggestions
                suggestions = [
                    "What are the key trends in this data?",
                    "Show me a breakdown by category",
                    "What are the highest and lowest values?",
                    "Create a chart comparing the main segments"
                ]
                
                cols = st.columns(2)
                for i, sugg in enumerate(suggestions):
                    with cols[i % 2]:
                        if st.button(sugg, key=f"init_sugg_{i}", use_container_width=True):
                            st.session_state.messages.append({"role": "user", "content": sugg})
                            st.rerun()
            
            # Display chat messages
            for msg in st.session_state.messages:
                render_message(msg["role"], msg["content"])
                
                # If assistant message, check for chart
                if msg["role"] == "assistant":
                    chart_data = parse_chart_from_response(msg["content"])
                    if chart_data:
                        fig = create_chart(chart_data)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Show follow-up suggestions after last assistant message
                    if msg == st.session_state.messages[-1]:
                        followups = extract_followup_questions(msg["content"])
                        selected = render_suggestions(followups)
                        if selected:
                            st.session_state.messages.append({"role": "user", "content": selected})
                            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # INPUT AREA (Fixed at bottom)
    # =========================================================================
    if st.session_state.selected_dataset:
        st.markdown("---")
        
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_area(
                "Ask a question",
                placeholder="Ask about the data, request insights, or ask for a chart...",
                height=80,
                label_visibility="collapsed",
                key="user_input"
            )
        
        with col2:
            st.write("")  # Spacing
            send_button = st.button("Send ➤", use_container_width=True)
        
        # Process user input
        if send_button and user_input.strip():
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input.strip()})
            
            # Get stats for current dataset
            stats = get_stats(st.session_state.selected_dataset)
            
            # Get current dataset name
            current_dataset = next(
                (d for d in datasets if d['dataset_id'] == st.session_state.selected_dataset),
                {"dataset_name": "Dataset"}
            )
            
            # Check if user is asking for dashboard
            dashboard_keywords = ["dashboard", "interactive", "power bi", "powerbi", "full view", "explore data"]
            if any(kw in user_input.lower() for kw in dashboard_keywords):
                # Dashboard request - placeholder for Make.com integration
                response = """I'd love to show you the interactive dashboard! 

🚧 **Dashboard Feature Coming Soon**

The Power BI interactive dashboard integration is being set up. Once configured, you'll be able to:
- Explore the data with interactive filters
- Drill down into specific segments
- View multiple visualizations simultaneously

In the meantime, I can help you with:
1. What specific analysis would you like to see?
2. Would you like me to create a chart of any particular metric?
3. What questions do you have about the data?"""
            else:
                # Regular question - call DeepSeek
                with st.spinner("Analyzing..."):
                    response = get_ai_response(
                        user_input.strip(),
                        current_dataset['dataset_name'],
                        stats
                    )
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

if __name__ == "__main__":
    main()
