import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
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
    st.session_state.ai_provider = "groq"

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
        line-height: 1.8;
        color: #334155;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
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
    
    /* Special style for admin button - small and subtle */
    .admin-button > button {
        background: transparent !important;
        color: #9ca3af !important;
        font-size: 0.7rem !important;
        font-weight: 400 !important;
        box-shadow: none !important;
        min-height: 20px !important;
        padding: 0.25rem 0.5rem !important;
        border: none !important;
    }
    
    .admin-button > button:hover {
        color: #6366f1 !important;
        text-decoration: underline !important;
        transform: none !important;
        box-shadow: none !important;
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
    
    .key-fact-item {
        font-size: 0.9rem;
        line-height: 1.6;
        color: #334155;
        margin-bottom: 0.5rem;
    }
    
    .provider-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .provider-card.selected {
        border-color: #6366f1;
        background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);
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
        return pd.read_csv(url)
    except:
        return None

def get_datasets():
    try:
        sheet_id = st.secrets["GOOGLE_SHEET_ID"]
        df = load_google_sheet_data(sheet_id, "Datasets")
        if df is not None:
            return df.to_dict('records')
    except:
        pass
    return []

def get_stats(dataset_id):
    try:
        sheet_id = st.secrets["GOOGLE_SHEET_ID"]
        df = load_google_sheet_data(sheet_id, "Stats")
        if df is not None:
            return df[df['dataset_id'] == dataset_id].to_dict('records')
    except:
        pass
    return []

def get_dashboards(dataset_id):
    try:
        sheet_id = st.secrets["GOOGLE_SHEET_ID"]
        df = load_google_sheet_data(sheet_id, "Dashboards")
        if df is not None:
            return df[df['dataset_id'] == dataset_id].to_dict('records')
    except:
        pass
    return []

# =============================================================================
# AI API FUNCTIONS
# =============================================================================

def call_groq(messages, system_prompt):
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system_prompt}, *messages],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def call_deepseek(messages, system_prompt):
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "system", "content": system_prompt}, *messages],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def call_ai(messages, system_prompt):
    if st.session_state.ai_provider == "groq":
        return call_groq(messages, system_prompt)
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
    
    system_prompt = f"""You are an expert data analyst helping users understand the "{dataset_name}" dataset.

AVAILABLE STATISTICS:
{stats_text}

CRITICAL FORMATTING RULES:
1. Use plain text only - absolutely NO markdown formatting like **bold**, *italic*, or any special characters
2. Each bullet point must be on a NEW LINE - this is critical for readability
3. Start bullet points with the bullet character •
4. Leave blank lines between sections

EXAMPLE OF CORRECT FORMAT:
The highest price town is Pasir Ris at $373,272 while the lowest is Sembawang at $69,683.

Key insights:

• Pasir Ris has the highest average price of $373,272
• Sembawang has the lowest average price of $69,683
• The price gap between highest and lowest is over $300,000

FOLLOW-UP QUESTIONS RULES:
- Provide exactly 3 follow-up questions at the end
- These must be questions the USER would ask YOU about the data
- NEVER ask what the user wants or prefers
- Questions should explore the data further

WRONG (asking user): "Are there any specific flat types you would like to focus on?"
CORRECT (exploring data): "Which flat types have seen the biggest price increases?"

Format follow-ups like this:
Follow-up questions:
1. [analytical question about the data]
2. [analytical question about the data]
3. [analytical question about the data]

If asked to create a chart, include:
```json
{{"chart_type": "bar", "title": "Title", "data": {{"labels": [...], "values": [...]}}, "x_label": "X", "y_label": "Y"}}
```"""

    return call_ai([{"role": "user", "content": user_question}], system_prompt)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def parse_chart_from_response(response):
    match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    return None

def create_chart(chart_data):
    labels = chart_data.get("data", {}).get("labels", [])
    values = chart_data.get("data", {}).get("values", [])
    if not labels or not values:
        return None
    
    chart_type = chart_data.get("chart_type", "bar")
    title = chart_data.get("title", "Chart")
    
    if chart_type == "bar":
        fig = px.bar(x=labels, y=values, title=title)
    elif chart_type == "line":
        fig = px.line(x=labels, y=values, title=title, markers=True)
    elif chart_type == "pie":
        fig = px.pie(names=labels, values=values, title=title)
    else:
        fig = px.bar(x=labels, y=values, title=title)
    
    fig.update_layout(font_family="DM Sans", paper_bgcolor="white", plot_bgcolor="white")
    fig.update_traces(marker_color="#6366f1")
    return fig

def extract_followup_questions(response):
    questions = []
    lines = response.split('\n')
    in_followup = False
    for line in lines:
        line = line.strip()
        if 'follow-up' in line.lower() or 'follow up' in line.lower():
            in_followup = True
            continue
        if in_followup:
            clean = re.sub(r'^[\d\.\)\-\*\•]+\s*', '', line).strip()
            if len(clean) > 10 and '?' in clean:
                # Filter out questions that ask the user for preferences
                bad_patterns = ['would you', 'do you', 'are there any', 'what would you', 'is there', 'can you tell me', 'would you like']
                is_bad = any(pattern in clean.lower() for pattern in bad_patterns)
                if not is_bad:
                    questions.append(clean)
    return questions[:3]

def clean_response_for_display(response):
    # Remove JSON code blocks
    cleaned = re.sub(r'```json\s*.*?\s*```', '', response, flags=re.DOTALL)
    # Remove follow-up section
    cleaned = re.sub(r'Follow-up questions:.*', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    return cleaned.strip()

def format_response_html(content):
    """Convert plain text response to HTML with proper line breaks and formatting"""
    # Escape any HTML characters first
    content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Convert **text** to <strong>text</strong> (bold)
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    
    # Convert __text__ to <strong>text</strong> (bold alternative)
    content = re.sub(r'__(.+?)__', r'<strong>\1</strong>', content)
    
    # Convert *text* to <em>text</em> (italic)
    content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
    
    # Convert _text_ to <em>text</em> (italic alternative)
    content = re.sub(r'_(.+?)_', r'<em>\1</em>', content)
    
    # Convert `code` to styled code
    content = re.sub(r'`(.+?)`', r'<code style="background:#f1f5f9;padding:2px 6px;border-radius:4px;">\1</code>', content)
    
    # Remove any remaining stray asterisks or underscores used for formatting
    content = re.sub(r'(?<!\w)\*(?!\w)', '', content)  # Remove standalone *
    content = re.sub(r'(?<!\w)_(?!\w)', '', content)   # Remove standalone _
    
    # Convert newlines to <br> tags
    lines = content.split('\n')
    html_lines = []
    for line in lines:
        line = line.strip()
        if line:
            html_lines.append(line)
        else:
            html_lines.append('<br>')
    
    return '<br>'.join(html_lines)

def format_plain_text(text):
    """Clean text of any markdown formatting - for Key Facts etc."""
    # Remove **bold**
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # Remove __bold__
    text = re.sub(r'__(.+?)__', r'\1', text)
    # Remove *italic*
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Remove _italic_
    text = re.sub(r'_(.+?)_', r'\1', text)
    # Remove `code`
    text = re.sub(r'`(.+?)`', r'\1', text)
    # Remove any stray formatting characters
    text = text.replace('*', '').replace('_', '').replace('`', '')
    return text

def extract_key_stats(summary):
    key_stats = {}
    
    # Extract total records - look for number followed by transactions/listings
    match = re.search(r'([\d,]+)\s*(?:HDB\s+)?(?:resale\s+)?(transactions|listings)', summary, re.IGNORECASE)
    if match:
        key_stats['total'] = match.group(1)
        key_stats['total_label'] = match.group(2).title()
    
    # Extract average price
    match = re.search(r'Average\s*price:?\s*\$?([\d,]+)', summary, re.IGNORECASE)
    if match:
        key_stats['avg_price'] = '$' + match.group(1)
    
    # Extract max price from range like "$5,000 - $900,000"
    match = re.search(r'\$?[\d,]+\s*-\s*\$?([\d,]+)', summary)
    if match:
        key_stats['max_price'] = '$' + match.group(1)
    
    return key_stats

def parse_summary_to_facts(summary):
    """Parse summary into clean fact sentences without any markdown"""
    # Split by period
    sentences = summary.split('.')
    facts = []
    for s in sentences:
        s = s.strip()
        if len(s) > 15:
            # Clean any markdown formatting
            s = format_plain_text(s)
            facts.append(s)
    return facts[:5]

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
            "Compare Auckland and Queenstown prices",
            "Show me a chart of prices by region"
        ]
    return ["What are the key insights?", "Show me a breakdown by category"]

# =============================================================================
# ADMIN PAGE
# =============================================================================

def render_admin_page():
    st.markdown("## ⚙️ Admin Settings")
    
    if st.button("← Back to App"):
        st.session_state.page = "main"
        st.rerun()
    
    st.markdown("---")
    st.markdown("### AI Provider")
    
    current = st.session_state.ai_provider
    
    # Groq option
    groq_class = "selected" if current == "groq" else ""
    st.markdown(f"""
    <div class="provider-card {groq_class}">
        <strong>⚡ Groq (Llama 3.3 70B)</strong><br>
        <span style="color: #64748b;">Fast (~1 second) • Recommended</span>
        {"<br><span style='color: #22c55e; font-weight: 600;'>✓ ACTIVE</span>" if current == "groq" else ""}
    </div>
    """, unsafe_allow_html=True)
    
    if current != "groq":
        if st.button("Select Groq"):
            st.session_state.ai_provider = "groq"
            st.rerun()
    
    # DeepSeek option
    ds_class = "selected" if current == "deepseek" else ""
    st.markdown(f"""
    <div class="provider-card {ds_class}">
        <strong>🧠 DeepSeek</strong><br>
        <span style="color: #64748b;">Slower (~5-10 seconds) • Lower cost</span>
        {"<br><span style='color: #22c55e; font-weight: 600;'>✓ ACTIVE</span>" if current == "deepseek" else ""}
    </div>
    """, unsafe_allow_html=True)
    
    if current != "deepseek":
        if st.button("Select DeepSeek"):
            st.session_state.ai_provider = "deepseek"
            st.rerun()
    
    st.markdown("---")
    if st.button("🔌 Test Connection"):
        with st.spinner("Testing..."):
            result = call_ai([{"role": "user", "content": "Say OK"}], "Reply with OK only")
            if "error" in result.lower():
                st.error(f"❌ {result}")
            else:
                st.success("✅ Working!")

# =============================================================================
# MAIN APP
# =============================================================================

def render_main_app():
    datasets = get_datasets()
    
    # Dataset Selection Screen
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
            for i, ds in enumerate(datasets):
                with cols[i % 2]:
                    if st.button(f"{icons.get(ds['dataset_id'], '📊')} {ds['dataset_name']}", key=f"ds_{i}", use_container_width=True):
                        st.session_state.selected_dataset = ds['dataset_id']
                        st.session_state.dataset_summary = ds['summary']
                        st.session_state.messages = []
                        st.rerun()
        
        # Admin link at bottom - ONLY place admin button exists
        st.markdown("---")
        col1, col2, col3 = st.columns([6, 1, 1])
        with col3:
            st.markdown('<div class="admin-button">', unsafe_allow_html=True)
            if st.button("Admin", key="admin_home"):
                st.session_state.page = "admin"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat Interface Screen
    else:
        current_ds = next((d for d in datasets if d['dataset_id'] == st.session_state.selected_dataset), None)
        if not current_ds:
            st.error("Dataset not found")
            return
        
        stats = get_stats(st.session_state.selected_dataset)
        key_stats = extract_key_stats(current_ds['summary'])
        facts = parse_summary_to_facts(current_ds['summary'])
        
        col_main, col_sidebar = st.columns([2, 1])
        
        # RIGHT SIDEBAR
        with col_sidebar:
            if st.button("← Back to datasets"):
                st.session_state.selected_dataset = None
                st.session_state.messages = []
                st.rerun()
            
            st.markdown("---")
            st.markdown(f"### 📊 {current_ds['dataset_name']}")
            
            # Stat boxes with fallback values
            total_val = key_stats.get('total', '287,200')
            total_label = key_stats.get('total_label', 'Transactions')
            avg_val = key_stats.get('avg_price', '$219,542')
            max_val = key_stats.get('max_price', '$900,000')
            
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-box-icon">📊</div>
                <div class="stat-box-value">{total_val}</div>
                <div class="stat-box-label">{total_label}</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-icon">💰</div>
                <div class="stat-box-value">{avg_val}</div>
                <div class="stat-box-label">Average Price</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-icon">📈</div>
                <div class="stat-box-value">{max_val}</div>
                <div class="stat-box-label">Maximum Price</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("**Key Facts:**")
            
            # Display facts as plain HTML - no markdown processing
            for fact in facts:
                st.markdown(f'<p class="key-fact-item">• {fact}.</p>', unsafe_allow_html=True)
        
        # MAIN CHAT AREA
        with col_main:
            st.markdown("### 💬 Chat with your data")
            provider = "⚡ Groq" if st.session_state.ai_provider == "groq" else "🧠 DeepSeek"
            st.caption(f"Powered by {provider}")
            
            # Initial suggestions (when no messages)
            if not st.session_state.messages:
                st.write("What insights are you looking for?")
                suggestions = get_initial_suggestions(st.session_state.selected_dataset)
                cols = st.columns(2)
                for i, sugg in enumerate(suggestions):
                    with cols[i % 2]:
                        if st.button(sugg, key=f"sugg_{i}", use_container_width=True):
                            st.session_state.pending_question = sugg
                            st.rerun()
            
            # Display chat messages
            for idx, msg in enumerate(st.session_state.messages):
                if msg["role"] == "user":
                    st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    content = msg["content"]
                    
                    # Check for dashboard embed
                    dashboard_match = re.search(r'\[DASHBOARD:(.*?)\]', content)
                    
                    if dashboard_match:
                        embed_url = dashboard_match.group(1)
                        # Remove the dashboard tag from content
                        content_clean = re.sub(r'\[DASHBOARD:.*?\]', '', content)
                        content_clean = clean_response_for_display(content_clean)
                        content_html = format_response_html(content_clean)
                        
                        # Show text message
                        st.markdown(f'<div class="assistant-message-box">{content_html}</div>', unsafe_allow_html=True)
                        
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
                    else:
                        content_clean = clean_response_for_display(content)
                        content_html = format_response_html(content_clean)
                        st.markdown(f'<div class="assistant-message-box">{content_html}</div>', unsafe_allow_html=True)
                    
                    # Chart if present
                    chart_data = parse_chart_from_response(msg["content"])
                    if chart_data:
                        fig = create_chart(chart_data)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Follow-up questions (only for last message)
                    if idx == len(st.session_state.messages) - 1:
                        followups = extract_followup_questions(msg["content"])
                        if followups:
                            st.write("**Suggested follow-up questions:**")
                            for i, q in enumerate(followups):
                                if st.button(q, key=f"fu_{idx}_{i}", use_container_width=True):
                                    st.session_state.pending_question = q
                                    st.rerun()
            
            # Input area
            st.markdown("---")
            st.write("**Ask your own question:**")
            col1, col2 = st.columns([5, 1])
            with col1:
                user_input = st.text_area("Question", placeholder="Ask about the data...", height=80, label_visibility="collapsed")
            with col2:
                st.write("")  # Spacing
                if st.button("Send ➤", use_container_width=True):
                    if user_input.strip():
                        st.session_state.pending_question = user_input.strip()
                        st.rerun()
        
        # Process pending question
        if st.session_state.pending_question:
            q = st.session_state.pending_question
            st.session_state.pending_question = None
            st.session_state.messages.append({"role": "user", "content": q})
            
            # Check for dashboard request
            if any(kw in q.lower() for kw in ["dashboard", "power bi"]):
                dashboards = get_dashboards(st.session_state.selected_dataset)
                if dashboards and dashboards[0].get('embed_url', '').startswith('http'):
                    url = dashboards[0]['embed_url']
                    response = f"Here's the dashboard:\n\n[DASHBOARD:{url}]\n\nFollow-up questions:\n1. What trends do you notice in the visualization?\n2. Which category shows the highest values?\n3. How do the numbers compare across segments?"
                else:
                    response = "Dashboard not configured yet.\n\nFollow-up questions:\n1. What specific data would you like to explore?\n2. Should I create a chart for you?\n3. Which metrics are most important?"
            else:
                with st.spinner("Analyzing..."):
                    response = get_ai_response(q, current_ds['dataset_name'], stats)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        # Admin link at bottom of chat page
        st.markdown("---")
        col1, col2, col3 = st.columns([6, 1, 1])
        with col3:
            st.markdown('<div class="admin-button">', unsafe_allow_html=True)
            if st.button("Admin", key="admin_chat"):
                st.session_state.page = "admin"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    if st.session_state.page == "admin":
        render_admin_page()
    else:
        render_main_app()

if __name__ == "__main__":
    main()
