"""
Modern FinTech Dark Theme UI & CSS Styling for Finance Data Analysis & AI Automation Dashboard.
Provides a modern dark aesthetic, emerald green accents (#10A37F),
sleek conversational chat bubbles, responsive metric cards, user profile cards, and clean typography.
"""

CUSTOM_CSS = """
<style>
/* Modern Dark FinTech Theme Base */
:root {
    --bg-main: #212121;
    --bg-sidebar: #171717;
    --bg-card: #2F2F2F;
    --bg-card-hover: #383838;
    --text-primary: #ECECEC;
    --text-secondary: #B4B4B4;
    --text-muted: #8E8E8E;
    --brand-primary: #10A37F;
    --brand-primary-hover: #1A7F64;
    --brand-primary-glow: rgba(16, 163, 127, 0.25);
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-card: rgba(255, 255, 255, 0.12);
}

/* Main Container & Background */
.stApp {
    background-color: var(--bg-main);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

section[data-testid="stSidebar"] div.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* User Profile Badge */
.profile-badge {
    background: #212121;
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
    margin-bottom: 16px;
    transition: all 0.2s ease;
}

.profile-badge:hover {
    border-color: var(--brand-primary);
    box-shadow: 0 4px 14px var(--brand-primary-glow);
}

.profile-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF;
    box-shadow: 0 2px 6px rgba(0,0,0,0.4);
    flex-shrink: 0;
}

.profile-name {
    font-size: 0.98rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.2;
}

.profile-role {
    font-size: 0.78rem;
    color: var(--text-secondary);
    margin-top: 2px;
}

.profile-org {
    font-size: 0.74rem;
    color: var(--brand-primary);
    margin-top: 2px;
    font-weight: 500;
}

/* Metric Card Containers */
.fin-card {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
    transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.fin-card:hover {
    transform: translateY(-2px);
    border-color: var(--brand-primary);
    box-shadow: 0 6px 18px var(--brand-primary-glow);
}

.fin-title {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.fin-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.2;
    margin-bottom: 6px;
    letter-spacing: -0.01em;
}

.fin-sub {
    font-size: 0.82rem;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

/* Badges */
.badge-pos {
    background-color: rgba(16, 163, 127, 0.16);
    color: #10A37F;
    padding: 3px 8px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.76rem;
    border: 1px solid rgba(16, 163, 127, 0.4);
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.badge-neg {
    background-color: rgba(239, 68, 68, 0.16);
    color: #F87171;
    padding: 3px 8px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.76rem;
    border: 1px solid rgba(239, 68, 68, 0.4);
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.badge-neutral {
    background-color: rgba(255, 255, 255, 0.08);
    color: #D1D5DB;
    padding: 3px 8px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.76rem;
    border: 1px solid rgba(255, 255, 255, 0.15);
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.badge-primary {
    background: linear-gradient(135deg, rgba(16, 163, 127, 0.25) 0%, rgba(16, 163, 127, 0.1) 100%);
    color: #10A37F;
    padding: 4px 10px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.78rem;
    border: 1px solid rgba(16, 163, 127, 0.5);
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

/* Header Banner */
.header-container {
    background: #171717;
    border: 1px solid var(--border-card);
    border-radius: 14px;
    padding: 20px 26px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
}

.header-title {
    font-size: 1.85rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 12px;
}

.header-subtitle {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-top: 6px;
}

/* Dataset active banner */
.dataset-banner {
    background: #1E1E1E;
    border: 1px solid rgba(16, 163, 127, 0.35);
    border-radius: 10px;
    padding: 12px 18px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: var(--text-primary);
    font-size: 0.88rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}

/* Conversational UI Elements */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-bottom: 20px;
}

.chat-bubble-user {
    background: #2F2F2F;
    border: 1px solid var(--border-card);
    border-radius: 16px 16px 4px 16px;
    padding: 14px 18px;
    max-width: 85%;
    margin-left: auto;
    color: #FFFFFF;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.chat-bubble-assistant {
    background: #1E1E1E;
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--brand-primary);
    border-radius: 4px 16px 16px 16px;
    padding: 18px 22px;
    max-width: 95%;
    margin-right: auto;
    color: var(--text-primary);
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 3px 12px rgba(0,0,0,0.25);
}

.chat-bubble-assistant h1, .chat-bubble-assistant h2, .chat-bubble-assistant h3, .chat-bubble-assistant h4 {
    color: #FFFFFF;
    margin-top: 12px;
    margin-bottom: 8px;
}

.chat-bubble-assistant ul {
    margin-left: 18px;
}

.chat-header-assistant {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--brand-primary);
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.prompt-pill {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 9999px;
    padding: 6px 14px;
    color: var(--text-primary);
    font-size: 0.82rem;
    font-weight: 500;
    display: inline-block;
    cursor: pointer;
    transition: all 0.2s ease;
    margin: 4px 2px;
}

.prompt-pill:hover {
    border-color: var(--brand-primary);
    color: var(--brand-primary);
    background: #383838;
}

/* Streamlit Tabs Styling */
div[data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 1px solid var(--border-card) !important;
    gap: 8px !important;
}

button[data-baseweb="tab"] {
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    padding: 10px 16px !important;
    border-radius: 8px 8px 0 0 !important;
    background-color: transparent !important;
    border: none !important;
    transition: color 0.18s ease !important;
}

button[data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background-color: rgba(255, 255, 255, 0.03) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--brand-primary) !important;
    border-bottom: 2px solid var(--brand-primary) !important;
}

/* Streamlit Buttons Styling */
div.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:hover {
    border-color: var(--brand-primary) !important;
    color: var(--brand-primary) !important;
    box-shadow: 0 2px 10px var(--brand-primary-glow) !important;
}

/* Form Inputs */
div[data-baseweb="input"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 8px !important;
}

div[data-baseweb="input"]:focus-within {
    border-color: var(--brand-primary) !important;
    box-shadow: 0 0 0 1px var(--brand-primary) !important;
}

/* Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #171717;
}
::-webkit-scrollbar-thumb {
    background: #383838;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #4E4E4E;
}
</style>
"""

def metric_card(title, value, subtext="", badge="", badge_type="pos"):
    """
    Renders a modern FinTech styled metric card with status badges and micro-interactions.
    """
    badge_html = ""
    if badge:
        if badge_type == "pos":
            cls = "badge-pos"
        elif badge_type == "neg":
            cls = "badge-neg"
        elif badge_type == "primary":
            cls = "badge-primary"
        else:
            cls = "badge-neutral"
        badge_html = f'<span class="{cls}">{badge}</span>'
        
    return f"""
    <div class="fin-card">
        <div class="fin-title">{title}</div>
        <div class="fin-value">{value}</div>
        <div class="fin-sub">{badge_html} <span>{subtext}</span></div>
    </div>
    """

def user_profile_card(user):
    """
    Renders a sidebar user account profile card.
    """
    name = user.get("name", "User")
    initials = "".join([part[0] for part in name.split()[:2]]).upper() or "U"
    role = user.get("role", "Financial Analyst")
    org = user.get("organization", "Enterprise Organization")
    color = user.get("avatar_color", "#10A37F")
    
    return f"""
    <div class="profile-badge">
        <div class="profile-avatar" style="background-color: {color};">{initials}</div>
        <div style="flex-grow: 1; min-width: 0;">
            <div class="profile-name" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{name}</div>
            <div class="profile-role" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{role}</div>
            <div class="profile-org">🏢 {org}</div>
        </div>
    </div>
    """
