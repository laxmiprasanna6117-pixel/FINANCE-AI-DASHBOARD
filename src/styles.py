"""
UI Themes and CSS Styling for the Finance Data Analysis & AI Automation Dashboard.
Provides a modern dark FinTech aesthetic, responsive metric cards, user profile badges, and accents.
"""

CUSTOM_CSS = """
<style>
/* Main app background and font smoothing */
.main {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* User Profile Badge */
.profile-badge {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border: 1px solid #3B82F6;
    border-radius: 12px;
    padding: 12px 18px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    margin-bottom: 14px;
}

.profile-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: 700;
    color: #FFFFFF;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.profile-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0;
}

.profile-role {
    font-size: 0.8rem;
    color: #94A3B8;
    margin: 0;
}

.profile-org {
    font-size: 0.75rem;
    color: #38BDF8;
    margin-top: 2px;
}

/* Metric Card Containers */
.fin-card {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 18px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.fin-card:hover {
    border-color: #3B82F6;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.2);
}

.fin-title {
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94A3B8;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.fin-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1.2;
    margin-bottom: 4px;
}

.fin-sub {
    font-size: 0.85rem;
    color: #64748B;
    display: flex;
    align-items: center;
    gap: 6px;
}

.badge-pos {
    background-color: rgba(16, 185, 129, 0.15);
    color: #10B981;
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.78rem;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-neg {
    background-color: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.78rem;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-neutral {
    background-color: rgba(59, 130, 246, 0.15);
    color: #60A5FA;
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.78rem;
    border: 1px solid rgba(59, 130, 246, 0.3);
}

/* Header Banner */
.header-container {
    background: linear-gradient(90deg, #1E1B4B 0%, #1E293B 50%, #0F172A 100%);
    border: 1px solid #4338CA;
    border-radius: 14px;
    padding: 22px 28px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-title {
    font-size: 1.95rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0;
    letter-spacing: -0.02em;
}

.header-subtitle {
    font-size: 0.92rem;
    color: #CBD5E1;
    margin-top: 5px;
}

/* AI Assistant Chat Bubble */
.ai-bubble {
    background-color: #1E293B;
    border-left: 4px solid #8B5CF6;
    border-radius: 0 10px 10px 0;
    padding: 16px 20px;
    margin: 12px 0;
    color: #E2E8F0;
    line-height: 1.6;
}

/* Dataset active banner */
.dataset-banner {
    background: linear-gradient(90deg, rgba(59, 130, 246, 0.15) 0%, rgba(16, 185, 129, 0.1) 100%);
    border: 1px solid #3B82F6;
    border-radius: 10px;
    padding: 12px 18px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #E2E8F0;
    font-size: 0.9rem;
}
</style>
"""

def metric_card(title, value, subtext="", badge="", badge_type="pos"):
    badge_html = ""
    if badge:
        cls = "badge-pos" if badge_type == "pos" else ("badge-neg" if badge_type == "neg" else "badge-neutral")
        badge_html = f'<span class="{cls}">{badge}</span>'
        
    return f"""
    <div class="fin-card">
        <div class="fin-title">{title}</div>
        <div class="fin-value">{value}</div>
        <div class="fin-sub">{badge_html} <span>{subtext}</span></div>
    </div>
    """

def user_profile_card(user):
    name = user.get("name", "User")
    initials = "".join([part[0] for part in name.split()[:2]]).upper() or "U"
    role = user.get("role", "Financial Analyst")
    org = user.get("organization", "Enterprise Organization")
    color = user.get("avatar_color", "#3B82F6")
    
    return f"""
    <div class="profile-badge">
        <div class="profile-avatar" style="background-color: {color};">{initials}</div>
        <div style="flex-grow: 1;">
            <div class="profile-name">{name}</div>
            <div class="profile-role">{role}</div>
            <div class="profile-org">🏢 {org}</div>
        </div>
    </div>
    """
