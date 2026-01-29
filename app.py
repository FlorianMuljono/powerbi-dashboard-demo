import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

if "page" not in st.session_state:
    st.session_state.page = "main"

if "ai_provider" not in st.session_state:
    st.session_state.ai_provider = "groq"  # Default to Groq

# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    
    .main .block-container {
        padding: 1.5rem 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .stApp {
        background: linear-gradient(180deg, #fafafa 0%, #f5f5f7 100%);
    }
    
    .welcome-container {
        text-align: center;
        padding: 3rem 2rem 2rem;
    }
    
    .welcome-title {
        font-size: 2.25rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }
    
    .welcome-subtitle {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    
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
    
    .assistant-message-box {
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
    
    .section-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 1.5rem 0 0.75rem;
    }
    
    .input-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #64748b;
        margin-bottom: 0.5rem;
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
    
    .stDeployButton {display: none;}
    div[data-testid="stToolbar"] {display: none;}
    div[data-testid="stDecoration"] {display: none;}
    
    .admin-link {
        position: fixed;
        bottom: 10px;
        right: 20px;
        font-size: 0.75rem;
        color: #94a3b8;
        cursor: pointer;
        z-index: 1000;
    }
    
    .admin-link:hover {
        color: #6366f1;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);
        border: 1px solid #c7d2fe;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 0.75rem;
    }
    
    .stat-box-icon {
        font-size: 1.5rem;
        margin-bottom: 0.25rem;
    }
    
    .stat-box-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #4f46e5;
        margin-bottom: 0.1rem;
    }
    
    .stat-box-label {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .provider-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .provider-card:hover {
        border-color: #6366f1;
    }
    
    .provider-card.selected {
        border-color: #6366f1;
        background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);
    }
    
    .provider-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0.25rem;
    }
    
    .provider-desc {
        font-size: 0.85rem;
        color: #64748b;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-active {
        background: #dcfce7;
        color: #166534;
    }
    
    .status-inactive {
        background: #f3f4f6;
        color: #6b7280;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# GOOGLE SHEETS FUNCTIONS
# =============================================================================

@st.cache_data(ttl=300)
def load_google_sheet_data(sheet_id, tab_name):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={tab_name}"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading {tab_name}: {e}")
        return None

def get_datasets():
    try:
        sheet_id = st.secrets["GOOGLE_SHEET_ID"]
        df = load_google_sheet_data(sheet_id, "Datasets")
        if df is not None:
            return df.to_dict('records')
    except Exception as e:
        st.error(f"Error loading datasets: {e}")
    return []

def get_stats(dataset_id):
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
# AI API FUNCTIONS
# =============================================================================

def call_groq(messages, system_prompt):
    """Call Groq API - Fast inference"""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error calling Groq: {str(e)}"

def call_deepseek(messages, system_prompt):
    """Call DeepSeek API - Cheaper but slower"""
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

def call_ai(messages, system_prompt):
    """Call the selected AI provider"""
    if st.session_state.ai_provider == "groq":
        return call_groq(messages, system_prompt)
    else:
        return call_deepseek(messages, system_prompt)

def format_stats_for_prompt(stats):
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
    stats_text = format_stats_for_prompt(stats)
    
    system_prompt = f"""You are an expert data analyst assistant helping users understand the "{dataset_name}" dataset.

## Available Statistics:
{stats_text}

## Your Role:
1. Answer questions using ONLY the statistics provided above
2. Be specific - use actual numbers from the stats
3. Provide actionable insights, not just facts

## Response Format Rules:
- Do NOT use markdown formatting like **bold** or *italic* - just use plain text
- Use clear headings like "Key Insights:" on their own line
- Use bullet points with "•" character for lists
- Keep responses clear and readable without special formatting
- If asked to create a chart, respond with a JSON code block

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

IMPORTANT FOR CHARTS:
- Include ALL data points
- Make sure labels and values arrays have the same length

## At the end of EVERY response, include exactly 3 follow-up questions like this:
Follow-up questions:
1. [question]
2. [question]
3. [question]

Keep responses concise but informative."""

    messages = [{"role": "user", "content": user_question}]
    return call_ai(messages, system_prompt)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def parse_chart_from_response(response):
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
    chart_type = chart_data.get("chart_type", "bar")
    title = chart_data.get("title", "Chart")
    data = chart_data.get("data", {})
    labels = data.get("labels", [])
    values = data.get("values", [])
    x_label = chart_data.get("x_label", "")
    y_label = chart_data.get("y_label", "")
    
    if not labels or not values:
        return None
    
    if chart_type == "bar":
        fig = px.bar(x=labels, y=values, title=title)
        fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
    elif chart_type == "line":
        fig = px.line(x=labels, y=values, title=title, markers=True)
        fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
    elif chart_type == "pie":
        fig = px.pie(names=labels, values=values, title=title)
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
    questions = []
    lines = response.split('\n')
    
    in_followup_section = False
    for line in lines:
        line = line.strip()
        
        if 'follow-up' in line.lower() or 'follow up' in line.lower():
            in_followup_section = True
            continue
        
        if in_followup_section:
            clean_line = re.sub(r'^[\d\.\)\-\*\•]+\s*', '', line).strip()
            if len(clean_line) > 10 and '?' in clean_line:
                questions.append(clean_line)
    
    if not questions:
        for line in lines:
            line = line.strip()
            if line.endswith('?') and len(line) > 15:
                clean = re.sub(r'^[\d\.\-\*\•\)]+\s*', '', line).strip()
                if clean not in questions:
                    questions.append(clean)
    
    return questions[:3]

def clean_response_for_display(response):
    cleaned = re.sub(r'```json\s*.*?\s*```', '', response, flags=re.DOTALL)
    cleaned = re.sub(r'Follow-up questions:.*', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'Suggested follow-up.*', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    return cleaned.strip()

def extract_key_stats(summary, dataset_id):
    key_stats = {}
    
    total_match = re.search(r'([\d,]+)\s*(transactions|listings|records)', summary, re.IGNORECASE)
    if total_match:
        key_stats['total'] = total_match.group(1)
        key_stats['total_label'] = total_match.group(2).title()
    
    avg_match = re.search(r'Average\s*(?:price)?:?\s*\$?([\d,]+(?:/night)?)', summary, re.IGNORECASE)
    if avg_match:
        key_stats['avg_price'] = '$' + avg_match.group(1)
    
    range_match = re.search(r'Price\s*range:?\s*\$?[\d,]+\s*-\s*\$?([\d,]+)', summary, re.IGNORECASE)
    if range_match:
        key_stats['max_price'] = '$' + range_match.group(1)
    
    return key_stats

def format_summary_as_bullets(summary):
    sentences = summary.split('.')
    bullets = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:
            bullets.append(sentence)
    return bullets

def get_initial_suggestions(dataset_id):
    if dataset_id == "sg_flat":
        return [
            "Which towns have the highest and lowest prices?",
            "How do prices vary by flat type?",
            "Show me the price trend from 1990 to 1999",
            "What floor levels command the highest prices?"
        ]
    elif dataset_id == "nz_airbnb":
        return [
            "Which regions have the highest prices?",
            "How do prices vary by room type?",
            "What's the difference between Auckland and Queenstown?",
            "Show me a chart of prices by region"
        ]
    else:
        return [
            "What are the key insights in this data?",
            "Which categories have the highest values?",
            "Show me a breakdown by category",
            "Create a chart of the main trends"
        ]

# =============================================================================
# ADMIN PAGE
# =============================================================================

def render_admin_page():
    st.markdown("## ⚙️ Admin Settings")
    st.markdown("---")
    
    # Back button
    if st.button("← Back to App"):
        st.session_state.page = "main"
        st.rerun()
    
    st.markdown("### AI Provider")
    st.markdown("Select which AI service to use for generating insights:")
    
    # Current status
    current = st.session_state.ai_provider
    
    # Groq option
    groq_selected = current == "groq"
    st.markdown(f"""
    <div class="provider-card {'selected' if groq_selected else ''}" style="{'border-color: #6366f1; background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);' if groq_selected else ''}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="provider-name">⚡ Groq (Llama 3.3 70B)</div>
                <div class="provider-desc">Fast responses (~1 second) • Recommended for demos</div>
            </div>
            <span class="status-badge {'status-active' if groq_selected else 'status-inactive'}">
                {'ACTIVE' if groq_selected else 'Inactive'}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Select Groq", key="select_groq", disabled=groq_selected):
        st.session_state.ai_provider = "groq"
        st.success("✅ Switched to Groq!")
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # DeepSeek option
    deepseek_selected = current == "deepseek"
    st.markdown(f"""
    <div class="provider-card {'selected' if deepseek_selected else ''}" style="{'border-color: #6366f1; background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);' if deepseek_selected else ''}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="provider-name">🧠 DeepSeek</div>
                <div class="provider-desc">Slower responses (~5-10 seconds) • Lower cost</div>
            </div>
            <span class="status-badge {'status-active' if deepseek_selected else 'status-inactive'}">
                {'ACTIVE' if deepseek_selected else 'Inactive'}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Select DeepSeek", key="select_deepseek", disabled=deepseek_selected):
        st.session_state.ai_provider = "deepseek"
        st.success("✅ Switched to DeepSeek!")
        st.rerun()
    
    st.markdown("---")
    
    # Connection test
    st.markdown("### Test Connection")
    if st.button("🔌 Test Current Provider"):
        with st.spinner(f"Testing {st.session_state.ai_provider}..."):
            test_messages = [{"role": "user", "content": "Say 'Connection successful!' in exactly those words."}]
            result = call_ai(test_messages, "You are a helpful assistant. Respond briefly.")
            
            if "error" in result.lower():
                st.error(f"❌ {result}")
            else:
                st.success(f"✅ {st.session_state.ai_provider.title()} is working!")
                st.info(f"Response: {result[:100]}...")

# =============================================================================
# MAIN APP PAGE
# =============================================================================

def render_main_app():
    datasets = get_datasets()
    
    # =========================================================================
    # SCREEN 1: Dataset Selection
    # =========================================================================
    if st.session_state.selected_dataset is None:
        st.markdown("""
        <div class="welcome-container">
            <div class="welcome-title">✨ What do you want to analyze today?</div>
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
    # SCREEN 2: Chat Interface
    # =========================================================================
    else:
        current_dataset = next(
            (d for d in datasets if d['dataset_id'] == st.session_state.selected_dataset),
            None
        )
        
        if not current_dataset:
            st.error("Dataset not found")
            return
        
        stats = get_stats(st.session_state.selected_dataset)
        key_stats = extract_key_stats(current_dataset['summary'], st.session_state.selected_dataset)
        summary_bullets = format_summary_as_bullets(current_dataset['summary'])
        initial_suggestions = get_initial_suggestions(st.session_state.selected_dataset)
        
        # Layout
        col_main, col_sidebar = st.columns([2, 1])
        
        # ---------------------------------------------------------------------
        # RIGHT SIDEBAR
        # ---------------------------------------------------------------------
        with col_sidebar:
            if st.button("← Back to datasets", key="back_btn"):
                st.session_state.selected_dataset = None
                st.session_state.messages = []
                st.session_state.pending_question = None
                st.rerun()
            
            st.markdown("---")
            
            # Dataset title
            st.markdown(f"### 📊 {current_dataset['dataset_name']}")
            
            # Three stat boxes
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-box-icon">📊</div>
                <div class="stat-box-value">{key_stats.get('total', 'N/A')}</div>
                <div class="stat-box-label">{key_stats.get('total_label', 'Records')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-box-icon">💰</div>
                <div class="stat-box-value">{key_stats.get('avg_price', 'N/A')}</div>
                <div class="stat-box-label">Average Price</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-box-icon">📈</div>
                <div class="stat-box-value">{key_stats.get('max_price', 'N/A')}</div>
                <div class="stat-box-label">Maximum Price</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Summary bullets
            st.markdown("**Key Facts:**")
            for bullet in summary_bullets[:5]:
                st.markdown(f"• {bullet}")
        
        # ---------------------------------------------------------------------
        # MAIN CHAT AREA
        # ---------------------------------------------------------------------
        with col_main:
            st.markdown("### 💬 Chat with your data")
            
            # Show current AI provider
            provider_emoji = "⚡" if st.session_state.ai_provider == "groq" else "🧠"
            provider_name = "Groq" if st.session_state.ai_provider == "groq" else "DeepSeek"
            st.caption(f"{provider_emoji} Powered by {provider_name}")
            
            # Initial suggestions
            if not st.session_state.messages:
                st.markdown("What insights are you looking for? Try one of these:")
                
                cols = st.columns(2)
                for i, sugg in enumerate(initial_suggestions):
                    with cols[i % 2]:
                        if st.button(sugg, key=f"init_sugg_{i}", use_container_width=True):
                            st.session_state.pending_question = sugg
                            st.rerun()
            
            # Chat messages
            for idx, msg in enumerate(st.session_state.messages):
                if msg["role"] == "user":
                    st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    cleaned_content = clean_response_for_display(msg["content"])
                    
                    # Check if response contains a dashboard embed
                    dashboard_match = re.search(r'\[DASHBOARD:(.*?)\]', msg["content"])
                    
                    if dashboard_match:
                        embed_url = dashboard_match.group(1)
                        display_content = re.sub(r'\[DASHBOARD:.*?\]', '', cleaned_content).strip()
                        
                        st.markdown('<div class="assistant-message-box">', unsafe_allow_html=True)
                        st.write(display_content.split('\n')[0])
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Render Power BI iframe
                        st.markdown(f"""
                        <iframe 
                            title="Power BI Dashboard" 
                            width="100%" 
                            height="500" 
                            src="{embed_url}" 
                            frameborder="0" 
                            allowFullScreen="true"
                            style="border: 1px solid #e2e8f0; border-radius: 12px; margin: 1rem 0;">
                        </iframe>
                        """, unsafe_allow_html=True)
                        
                        remaining_lines = '\n'.join(display_content.split('\n')[1:]).strip()
                        remaining_lines = re.sub(r'Follow-up questions:.*', '', remaining_lines, flags=re.DOTALL | re.IGNORECASE).strip()
                        if remaining_lines:
                            st.write(remaining_lines)
                    else:
                        st.markdown('<div class="assistant-message-box">', unsafe_allow_html=True)
                        st.write(cleaned_content)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Chart
                    chart_data = parse_chart_from_response(msg["content"])
                    if chart_data:
                        fig = create_chart(chart_data)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Follow-up questions
                    if idx == len(st.session_state.messages) - 1:
                        followups = extract_followup_questions(msg["content"])
                        
                        if followups:
                            st.markdown("**Suggested follow-up questions:**")
                            for i, q in enumerate(followups):
                                if st.button(q, key=f"followup_{idx}_{i}", use_container_width=True):
                                    st.session_state.pending_question = q
                                    st.rerun()
            
            # Input area
            st.markdown("---")
            st.markdown("**Ask your own question:**")
            
            col1, col2 = st.columns([5, 1])
            
            with col1:
                user_input = st.text_area(
                    "Question",
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
        # PROCESS QUESTION
        # ---------------------------------------------------------------------
        if st.session_state.pending_question:
            question = st.session_state.pending_question
            st.session_state.pending_question = None
            
            st.session_state.messages.append({"role": "user", "content": question})
            
            dashboard_keywords = ["dashboard", "interactive", "power bi", "powerbi", "show dashboard", "view dashboard"]
            if any(kw in question.lower() for kw in dashboard_keywords):
                dashboards = get_dashboards(st.session_state.selected_dataset)
                
                if dashboards and len(dashboards) > 0:
                    first_dashboard = dashboards[0]
                    embed_url = first_dashboard.get('embed_url', '')
                    dashboard_name = first_dashboard.get('dashboard_name', 'Dashboard')
                    
                    if embed_url and embed_url != 'REPLACE_WITH_YOUR_POWERBI_URL':
                        response = f"""Here's the {dashboard_name} dashboard:

[DASHBOARD:{embed_url}]

You can interact with the filters and visualizations above.

Follow-up questions:
1. What specific insights would you like from this view?
2. Would you like me to explain any of the charts?
3. Should I create a custom analysis based on what you see?"""
                    else:
                        response = """Dashboard URL not configured yet.

Please add your Power BI embed URL to the Google Sheet (Dashboards tab).

Follow-up questions:
1. What are the price trends over time?
2. Which categories have the highest values?
3. Can you create a comparison chart?"""
                else:
                    response = """No dashboards configured for this dataset yet.

Please add dashboard information to the Google Sheet (Dashboards tab).

Follow-up questions:
1. What are the price trends over time?
2. Which categories have the highest values?
3. Can you create a comparison chart?"""
            else:
                with st.spinner("Analyzing..."):
                    response = get_ai_response(question, current_dataset['dataset_name'], stats)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Admin link at bottom
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        if st.button("⚙️ Admin", key="admin_link"):
            st.session_state.page = "admin"
            st.rerun()

# =============================================================================
# MAIN
# =============================================================================

def main():
    if st.session_state.page == "admin":
        render_admin_page()
    else:
        render_main_app()

if __name__ == "__main__":
    main()
