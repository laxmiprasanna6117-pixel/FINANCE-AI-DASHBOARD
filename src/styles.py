"""
UI Themes and CSS Styling for the Finance Data Analysis & AI Automation Dashboard.
Provides a modern dark FinTech aesthetic, responsive metric cards, and badge accents.
"""

CUSTOM_CSS = """
<style>
/* Main app background and font smoothing */
.main {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
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
    padding: 24px 28px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-title {
    font-size: 2.0rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0;
    letter-spacing: -0.02em;
}

.header-subtitle {
    font-size: 0.95rem;
    color: #CBD5E1;
    margin-top: 6px;
}

/* Section Dividers */
.section-header {
    font-size: 1.25rem;
    font-weight: 700;
    color: #F1F5F9;
    margin-top: 20px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
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

/* Risk meter tags */
.risk-low {
    color: #10B981;
    font-weight: bold;
}
.risk-med {
    color: #F59E0B;
    font-weight: bold;
}
.risk-high {
    color: #EF4444;
    font-weight: bold;
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
