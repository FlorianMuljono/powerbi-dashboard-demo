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
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    
    .main .block-container {
        padding: 1.5rem 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Background */
    .stApp {
        background: linear-gradient(180deg, #fafafa 0%, #f5f5f7 100%);
    }
    
    /* Welcome header */
    .welcome-container {
        text-align: center;
        padding: 3rem 2rem 2rem;
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
    
    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 4px 18px;
        margin-left: 15%;
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
        margin-right: 5%;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        line-height: 1.7;
        color: #334155;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
    }
    
    .assistant-message h1, .assistant-message h2, .assistant-message h3 {
        color: #1a1a2e;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .assistant-message strong {
        color: #1a1a2e;
        font-weight: 600;
    }
    
    .assistant-message ul, .assistant-message ol {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    .assistant-message li {
        margin-bottom: 0.25rem;
    }
    
    /* STICKY Summary sidebar */
    .summary-sidebar {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
        position: sticky;
        top: 1rem;
        max-height: calc(100vh - 2rem);
        overflow-y: auto;
    }
    
    .summary-sidebar-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Key stats boxes */
    .key-stat-box {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 0.75rem;
    }
    
    .key-stat-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #6366f1;
        margin-bottom: 0.25rem;
    }
    
    .key-stat-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    /* Summary bullets */
    .summary-bullets {
        font-size: 0.85rem;
        color: #475569;
        line-height: 1.7;
        margin-top: 1rem;
    }
    
    .summary-bullets ul {
        padding-left: 1.25rem;
        margin: 0;
    }
    
    .summary-bullets li {
        margin-bottom: 0.5rem;
    }
    
    /* Section title */
    .section-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 1.5rem 0 0.75rem;
    }
    
    /* Input label */
    .input-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #64748b;
        margin-bottom: 0.5rem;
    }
    
    /* Streamlit button overrides */
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
        white-space: normal !important;
        height: auto !important;
        min-height: 50px !important;
        text-align: left !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
    }
    
    /* Input styling */
    .stTextArea textarea {
        font-family: 'DM Sans', sans-serif !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        font-size: 0.95rem !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
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

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

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
- Use proper formatting: **bold** for emphasis, bullet points for lists
- For charts: Include a JSON block with chart type and data
- Always end with EXACTLY 3 suggested follow-up questions

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

## Follow-up Questions Format:
At the end of EVERY response, include:
---
**Suggested follow-up questions:**
1. [Full question here]
2. [Full question here]
3. [Full question here]

## Important:
- Be conversational and helpful
- Highlight key insights and patterns
- Keep responses concise but informative"""

    messages = [{"role": "user", "content": user_question}]
    
    return call_deepseek(messages, system_prompt)

def parse_chart_from_response(response):
    """Extract chart JSON from AI response if present"""
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
    """Extract follow-up questions from AI response - clean, no leading dots or numbers"""
    questions = []
    lines = response.split('\n')
    
    in_followup_section = False
    for line in lines:
        line = line.strip()
        
        # Detect start of follow-up section
        if 'follow-up' in line.lower() or 'suggested' in line.lower():
            in_followup_section = True
            continue
        
        # Extract numbered questions
        if in_followup_section:
            # Remove leading numbers, dots, dashes, etc.
            clean_line = re.sub(r'^[\d\.\)\-\*\•]+\s*', '', line).strip()
            if len(clean_line) > 10 and '?' in clean_line:
                questions.append(clean_line)
    
    # Fallback: look for any line ending with ?
    if not questions:
        for line in lines:
            line = line.strip()
            if line.endswith('?') and len(line) > 15:
                clean = re.sub(r'^[\d\.\-\*\•\)]+\s*', '', line).strip()
                if clean not in questions:
                    questions.append(clean)
    
    return questions[:3]

def clean_response_for_display(response):
    """Clean response: remove JSON blocks and follow-up section, keep for markdown rendering"""
    # Remove JSON code blocks
    cleaned = re.sub(r'```json\s*.*?\s*```', '', response, flags=re.DOTALL)
    
    # Remove the follow-up questions section (we'll show them as buttons)
    cleaned = re.sub(r'---\s*\*\*Suggested follow-up.*', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'\*\*Suggested follow-up.*', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'Suggested follow-up.*', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    
    return cleaned.strip()

def extract_key_stats(summary):
    """Extract key statistics from summary text"""
    key_stats = {}
    
    # Extract total records
    total_match = re.search(r'([\d,]+)\s*(transactions|listings|records)', summary, re.IGNORECASE)
    if total_match:
        key_stats['total'] = total_match.group(1)
        key_stats['total_label'] = total_match.group(2).title()
    
    # Extract average price
    avg_match = re.search(r'Average\s*(?:price)?:?\s*\$?([\d,]+(?:/night)?)', summary, re.IGNORECASE)
    if avg_match:
        key_stats['avg_price'] = '$' + avg_match.group(1)
    
    # Extract price range
    range_match = re.search(r'Price\s*range:?\s*\$?([\d,]+)\s*-\s*\$?([\d,]+)', summary, re.IGNORECASE)
    if range_match:
        key_stats['min_price'] = '$' + range_match.group(1)
        key_stats['max_price'] = '$' + range_match.group(2)
    
    return key_stats

def format_summary_as_bullets(summary):
    """Convert summary paragraph into bullet points"""
    # Split by periods and create bullet points
    sentences = summary.split('.')
    bullets = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:
            bullets.append(f"• {sentence}")
    
    return bullets

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    # Load datasets
    datasets = get_datasets()
    
    # =========================================================================
    # SCREEN 1: Dataset Selection
    # =========================================================================
    if st.session_state.selected_dataset is None:
        st.markdown("""
        <div class="welcome-container">
            <div class="welcome-icon">✨</div>
            <div class="welcome-title">What do you want to analyze today?</div>
            <div class="welcome-subtitle">Select a dataset to get started</div>
        </div>
        """, unsafe_allow_html=True)
        
        if datasets:
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
                        st.session_state.pending_question = None
                        st.rerun()
        else:
            st.warning("Unable to load datasets. Please check your Google Sheet configuration.")
    
    # =========================================================================
    # SCREEN 2: Chat Interface with Sidebar Summary
    # =========================================================================
    else:
        # Get current dataset info
        current_dataset = next(
            (d for d in datasets if d['dataset_id'] == st.session_state.selected_dataset),
            None
        )
        
        if not current_dataset:
            st.error("Dataset not found")
            return
        
        # Get stats
        stats = get_stats(st.session_state.selected_dataset)
        key_stats = extract_key_stats(current_dataset['summary'])
        summary_bullets = format_summary_as_bullets(current_dataset['summary'])
        
        # Layout: Main chat area + Summary sidebar
        col_main, col_sidebar = st.columns([2, 1])
        
        # ---------------------------------------------------------------------
        # RIGHT SIDEBAR: Summary (STICKY - follows scroll)
        # ---------------------------------------------------------------------
        with col_sidebar:
            # Back button
            if st.button("← Back to datasets", key="back_btn"):
                st.session_state.selected_dataset = None
                st.session_state.messages = []
                st.session_state.pending_question = None
                st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Sticky summary container
            st.markdown(f"""
            <div class="summary-sidebar">
                <div class="summary-sidebar-title">
                    📊 {current_dataset['dataset_name']}
                </div>
            """, unsafe_allow_html=True)
            
            # Key stats
            if key_stats.get('avg_price'):
                st.markdown(f"""
                <div class="key-stat-box">
                    <div class="key-stat-value">{key_stats['avg_price']}</div>
                    <div class="key-stat-label">Avg Price</div>
                </div>
                """, unsafe_allow_html=True)
            
            if key_stats.get('min_price'):
                st.markdown(f"""
                <div class="key-stat-box">
                    <div class="key-stat-value">{key_stats['min_price']}</div>
                    <div class="key-stat-label">Min Price</div>
                </div>
                """, unsafe_allow_html=True)
            
            if key_stats.get('max_price'):
                st.markdown(f"""
                <div class="key-stat-box">
                    <div class="key-stat-value">{key_stats['max_price']}</div>
                    <div class="key-stat-label">Max Price</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Summary as bullet points
            st.markdown('<div class="summary-bullets"><ul>', unsafe_allow_html=True)
            for bullet in summary_bullets[:8]:  # Limit to 8 bullets
                st.markdown(f"<li>{bullet[2:]}</li>", unsafe_allow_html=True)  # Remove "• " prefix
            st.markdown('</ul></div></div>', unsafe_allow_html=True)
        
        # ---------------------------------------------------------------------
        # MAIN AREA: Chat
        # ---------------------------------------------------------------------
        with col_main:
            st.markdown(f"### 💬 Chat with your data")
            
            # If no messages, show initial suggestions
            if not st.session_state.messages:
                st.markdown("""
                <div style="text-align: center; color: #64748b; margin: 2rem 0 1rem;">
                    <p>What insights are you looking for? Try one of these:</p>
                </div>
                """, unsafe_allow_html=True)
                
                suggestions = [
                    "What are the key trends in this data?",
                    "Which areas have the highest prices?",
                    "Show me a breakdown by category",
                    "Create a chart comparing the main segments"
                ]
                
                cols = st.columns(2)
                for i, sugg in enumerate(suggestions):
                    with cols[i % 2]:
                        if st.button(sugg, key=f"init_sugg_{i}", use_container_width=True):
                            st.session_state.pending_question = sugg
                            st.rerun()
            
            # Display chat messages
            for idx, msg in enumerate(st.session_state.messages):
                if msg["role"] == "user":
                    st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    # Clean and render with proper markdown
                    cleaned_content = clean_response_for_display(msg["content"])
                    
                    # Use st.markdown for proper formatting (converts **bold** etc)
                    st.markdown(f'<div class="assistant-message">', unsafe_allow_html=True)
                    st.markdown(cleaned_content)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Check for chart
                    chart_data = parse_chart_from_response(msg["content"])
                    if chart_data:
                        fig = create_chart(chart_data)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Show follow-up suggestions after last assistant message
                    if idx == len(st.session_state.messages) - 1:
                        followups = extract_followup_questions(msg["content"])
                        
                        if followups:
                            st.markdown('<div class="section-title">Suggested follow-up questions</div>', unsafe_allow_html=True)
                            
                            for i, q in enumerate(followups):
                                if st.button(q, key=f"followup_{idx}_{i}", use_container_width=True):
                                    st.session_state.pending_question = q
                                    st.rerun()
            
            # Input area with label
            st.markdown("---")
            st.markdown('<div class="input-label">Ask your own question</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([5, 1])
            
            with col1:
                user_input = st.text_area(
                    "Ask a question",
                    placeholder="Ask about the data, request insights, or ask for a chart...",
                    height=80,
                    label_visibility="collapsed",
                    key="user_input"
                )
            
            with col2:
                st.write("")
                if st.button("Send ➤", key="send_btn", use_container_width=True):
                    if user_input.strip():
                        st.session_state.pending_question = user_input.strip()
                        st.rerun()
        
        # ---------------------------------------------------------------------
        # PROCESS PENDING QUESTION (after UI renders)
        # ---------------------------------------------------------------------
        if st.session_state.pending_question:
            question = st.session_state.pending_question
            st.session_state.pending_question = None
            
            # Add user message
            st.session_state.messages.append({"role": "user", "content": question})
            
            # Check if user is asking for dashboard
            dashboard_keywords = ["dashboard", "interactive", "power bi", "powerbi", "full view", "explore data"]
            if any(kw in question.lower() for kw in dashboard_keywords):
                response = """I'd love to show you the interactive dashboard! 

🚧 **Dashboard Feature Coming Soon**

The Power BI interactive dashboard integration is being set up. Once configured, you'll be able to explore the data with interactive filters and visualizations.

In the meantime, I can help you with specific analysis or create charts for you.

---
**Suggested follow-up questions:**
1. What are the price trends over time?
2. Which categories have the highest values?
3. Can you create a comparison chart?"""
            else:
                response = get_ai_response(question, current_dataset['dataset_name'], stats)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

if __name__ == "__main__":
    main()
