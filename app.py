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
        line-height: 1.7;
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
    
    .admin-link {
        font-size: 0.75rem;
        color: #9ca3af;
        text-decoration: none;
        cursor: pointer;
    }
    
    .admin-link:hover {
        color: #6366f1;
        text-decoration: underline;
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
        df = pd.read_csv(url)
        return df
    except Exception as e:
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
            filtered = df[df['dataset_id'] == dataset_id]
            return filtered.to_dict('records')
    except:
        pass
    return []

def get_dashboards(dataset_id):
    try:
        sheet_id = st.secrets["GOOGLE_SHEET_ID"]
        df = load_google_sheet_data(sheet_id, "Dashboards")
        if df is not None:
            filtered = df[df['dataset_id'] == dataset_id]
            return filtered.to_dict('records')
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

## IMPORTANT FORMATTING RULES:
1. Use ONLY plain text - no markdown, no **bold**, no *italic*, no special formatting
2. Use simple bullet points with • character
3. Write numbers clearly without any special formatting
4. Use line breaks to separate sections
5. Keep everything in the same consistent font size

## Response Structure:
- Start with a clear summary sentence
- List key insights with • bullet points
- Include specific numbers from the statistics
- If asked for a chart, include the JSON code block

## Chart JSON Format (when charts are requested):
```json
{{
    "chart_type": "bar|line|pie",
    "title": "Chart Title",
    "data": {{"labels": [...], "values": [...]}},
    "x_label": "X Axis Label",
    "y_label": "Y Axis Label"
}}
```

## End every response with exactly 3 follow-up questions:
Follow-up questions:
1. [question]
2. [question]
3. [question]"""

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
            return json.loads(matches[0])
        except:
            pass
    return None

def create_chart(chart_data):
    chart_type = chart_data.get("chart_type", "bar")
    title = chart_data.get("title", "Chart")
    data = chart_data.get("data", {})
    labels = data.get("labels", [])
    values = data.get("values", [])
    
    if not labels or not values:
        return None
    
    if chart_type == "bar":
        fig = px.bar(x=labels, y=values, title=title)
    elif chart_type == "line":
        fig = px.line(x=labels, y=values, title=title, markers=True)
    elif chart_type == "pie":
        fig = px.pie(names=labels, values=values, title=title)
    else:
        fig = px.bar(x=labels, y=values, title=title)
    
    fig.update_layout(
        font_family="DM Sans",
        title_font_size=16,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=50, l=50, r=30, b=50)
    )
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
                questions.append(clean)
    return questions[:3]

def clean_response_for_display(response):
    cleaned = re.sub(r'```json\s*.*?\s*```', '', response, flags=re.DOTALL)
    cleaned = re.sub(r'Follow-up questions:.*', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    return cleaned.strip()

def extract_key_stats(summary):
    key_stats = {}
    
    # Extract total records - improved regex
    total_match = re.search(r'contains?\s*([\d,]+)\s*(?:HDB\s+)?(?:resale\s+)?(transactions|listings|records)', summary, re.IGNORECASE)
    if total_match:
        key_stats['total'] = total_match.group(1)
        key_stats['total_label'] = total_match.group(2).title()
    else:
        # Fallback - look for any large number followed by transactions/listings
        total_match2 = re.search(r'([\d,]+)\s*(transactions|listings)', summary, re.IGNORECASE)
        if total_match2:
            key_stats['total'] = total_match2.group(1)
            key_stats['total_label'] = total_match2.group(2).title()
    
    # Extract average price
    avg_match = re.search(r'Average\s*price:?\s*\$?([\d,]+)', summary, re.IGNORECASE)
    if avg_match:
        key_stats['avg_price'] = '$' + avg_match.group(1)
    
    # Extract max price from range
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
            bullets.append(sentence + '.')
    return bullets[:5]

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
    
    if st.button("← Back to App"):
        st.session_state.page = "main"
        st.rerun()
    
    st.markdown("---")
    st.markdown("### AI Provider")
    
    current = st.session_state.ai_provider
    
    # Groq
    st.markdown(f"""
    <div class="provider-card {'selected' if current == 'groq' else ''}">
        <strong>⚡ Groq (Llama 3.3 70B)</strong><br>
        <span style="color: #64748b; font-size: 0.9rem;">Fast responses (~1 second) • Recommended for demos</span>
        {' <span style="color: #22c55e; font-weight: 600;"> ✓ ACTIVE</span>' if current == 'groq' else ''}
    </div>
    """, unsafe_allow_html=True)
    
    if current != "groq":
        if st.button("Select Groq"):
            st.session_state.ai_provider = "groq"
            st.rerun()
    
    # DeepSeek
    st.markdown(f"""
    <div class="provider-card {'selected' if current == 'deepseek' else ''}">
        <strong>🧠 DeepSeek</strong><br>
        <span style="color: #64748b; font-size: 0.9rem;">Slower responses (~5-10 seconds) • Lower cost</span>
        {' <span style="color: #22c55e; font-weight: 600;"> ✓ ACTIVE</span>' if current == 'deepseek' else ''}
    </div>
    """, unsafe_allow_html=True)
    
    if current != "deepseek":
        if st.button("Select DeepSeek"):
            st.session_state.ai_provider = "deepseek"
            st.rerun()
    
    st.markdown("---")
    st.markdown("### Test Connection")
    
    if st.button("🔌 Test Current Provider"):
        with st.spinner(f"Testing {st.session_state.ai_provider}..."):
            result = call_ai(
                [{"role": "user", "content": "Say 'OK' only."}],
                "Respond with only 'OK'."
            )
            if "error" in result.lower():
                st.error(f"❌ {result}")
            else:
                st.success(f"✅ {st.session_state.ai_provider.title()} is working!")

# =============================================================================
# MAIN APP
# =============================================================================

def render_main_app():
    datasets = get_datasets()
    
    # Dataset Selection
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
                    if st.button(f"{icon} {dataset['dataset_name']}", key=f"ds_{dataset['dataset_id']}", use_container_width=True):
                        st.session_state.selected_dataset = dataset['dataset_id']
                        st.session_state.dataset_summary = dataset['summary']
                        st.session_state.messages = []
                        st.rerun()
    
    # Chat Interface
    else:
        current_dataset = next((d for d in datasets if d['dataset_id'] == st.session_state.selected_dataset), None)
        if not current_dataset:
            st.error("Dataset not found")
            return
        
        stats = get_stats(st.session_state.selected_dataset)
        key_stats = extract_key_stats(current_dataset['summary'])
        summary_bullets = format_summary_as_bullets(current_dataset['summary'])
        
        col_main, col_sidebar = st.columns([2, 1])
        
        # Sidebar
        with col_sidebar:
            if st.button("← Back to datasets"):
                st.session_state.selected_dataset = None
                st.session_state.messages = []
                st.rerun()
            
            st.markdown("---")
            st.markdown(f"### 📊 {current_dataset['dataset_name']}")
            
            # Stat boxes
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-box-icon">📊</div>
                <div class="stat-box-value">{key_stats.get('total', '287,200')}</div>
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
            st.markdown("**Key Facts:**")
            for bullet in summary_bullets:
                st.write(f"• {bullet}")
        
        # Main chat area
        with col_main:
            st.markdown("### 💬 Chat with your data")
            
            provider = "⚡ Groq" if st.session_state.ai_provider == "groq" else "🧠 DeepSeek"
            st.caption(f"Powered by {provider}")
            
            if not st.session_state.messages:
                st.write("What insights are you looking for? Try one of these:")
                suggestions = get_initial_suggestions(st.session_state.selected_dataset)
                cols = st.columns(2)
                for i, sugg in enumerate(suggestions):
                    with cols[i % 2]:
                        if st.button(sugg, key=f"sugg_{i}", use_container_width=True):
                            st.session_state.pending_question = sugg
                            st.rerun()
            
            # Messages
            for idx, msg in enumerate(st.session_state.messages):
                if msg["role"] == "user":
                    st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    content = clean_response_for_display(msg["content"])
                    
                    # Check for dashboard
                    dashboard_match = re.search(r'\[DASHBOARD:(.*?)\]', msg["content"])
                    if dashboard_match:
                        embed_url = dashboard_match.group(1)
                        content = re.sub(r'\[DASHBOARD:.*?\]', '', content).strip()
                        
                        st.markdown(f'<div class="assistant-message-box">{content.split(chr(10))[0]}</div>', unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <iframe title="Dashboard" width="100%" height="500" src="{embed_url}" 
                            frameborder="0" allowFullScreen="true"
                            style="border: 1px solid #e2e8f0; border-radius: 12px; margin: 1rem 0;">
                        </iframe>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="assistant-message-box">{content}</div>', unsafe_allow_html=True)
                    
                    # Chart
                    chart_data = parse_chart_from_response(msg["content"])
                    if chart_data:
                        fig = create_chart(chart_data)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Follow-ups
                    if idx == len(st.session_state.messages) - 1:
                        followups = extract_followup_questions(msg["content"])
                        if followups:
                            st.write("**Suggested follow-up questions:**")
                            for i, q in enumerate(followups):
                                if st.button(q, key=f"fu_{idx}_{i}", use_container_width=True):
                                    st.session_state.pending_question = q
                                    st.rerun()
            
            # Input
            st.markdown("---")
            st.write("**Ask your own question:**")
            col1, col2 = st.columns([5, 1])
            with col1:
                user_input = st.text_area("Question", placeholder="Ask about the data...", height=80, label_visibility="collapsed", key="input")
            with col2:
                st.write("")
                if st.button("Send ➤", use_container_width=True):
                    if user_input.strip():
                        st.session_state.pending_question = user_input.strip()
                        st.rerun()
        
        # Process question
        if st.session_state.pending_question:
            question = st.session_state.pending_question
            st.session_state.pending_question = None
            st.session_state.messages.append({"role": "user", "content": question})
            
            dashboard_keywords = ["dashboard", "power bi", "powerbi"]
            if any(kw in question.lower() for kw in dashboard_keywords):
                dashboards = get_dashboards(st.session_state.selected_dataset)
                if dashboards:
                    url = dashboards[0].get('embed_url', '')
                    name = dashboards[0].get('dashboard_name', 'Dashboard')
                    if url and url != 'REPLACE_WITH_YOUR_POWERBI_URL':
                        response = f"Here's the {name} dashboard:\n\n[DASHBOARD:{url}]\n\nFollow-up questions:\n1. What insights do you see?\n2. Would you like me to analyze specific data?\n3. Should I create a custom chart?"
                    else:
                        response = "Dashboard URL not configured. Please add it to the Google Sheet.\n\nFollow-up questions:\n1. What data would you like to see?\n2. Should I create a chart?\n3. What trends interest you?"
                else:
                    response = "No dashboards configured yet.\n\nFollow-up questions:\n1. What data would you like to see?\n2. Should I create a chart?\n3. What trends interest you?"
            else:
                with st.spinner("Analyzing..."):
                    response = get_ai_response(question, current_dataset['dataset_name'], stats)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Small admin link at bottom right
    st.markdown("---")
    cols = st.columns([8, 1])
    with cols[1]:
        st.markdown('<p style="text-align: right;"><a class="admin-link" href="#" onclick="return false;">Admin</a></p>', unsafe_allow_html=True)
        if st.button("⚙️", key="admin_btn", help="Admin Settings"):
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
