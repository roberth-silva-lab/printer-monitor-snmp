import streamlit as st


def inject_global_css():
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 1.1rem;
                padding-bottom: 1.2rem;
                max-width: 1380px;
            }

            section[data-testid="stSidebar"] {
                border-right: 1px solid rgba(148, 163, 184, 0.22);
                background: linear-gradient(180deg, rgba(2, 6, 23, 0.97), rgba(15, 23, 42, 0.95));
            }

            .brand-card {
                border: 1px solid rgba(148, 163, 184, 0.26);
                border-radius: 14px;
                padding: 0.75rem 0.8rem;
                background: rgba(15, 23, 42, 0.45);
                margin-bottom: 0.85rem;
            }

            .brand-title {
                font-size: 1.02rem;
                font-weight: 700;
                color: #f8fafc;
                margin-bottom: 0.2rem;
            }

            .brand-subtitle {
                color: #cbd5e1;
                font-size: 0.83rem;
            }

            .app-subtitle {
                color: #94a3b8;
                font-size: 0.97rem;
                margin-top: -8px;
                margin-bottom: 1rem;
            }

            .section-title {
                font-size: 1.03rem;
                font-weight: 700;
                margin-top: 0.45rem;
                margin-bottom: 0.65rem;
            }

            .metric-card {
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 14px;
                padding: 0.9rem 0.95rem;
                background:
                    radial-gradient(circle at top right, rgba(30, 64, 175, 0.24), transparent 40%),
                    rgba(15, 23, 42, 0.38);
                margin-bottom: 0.5rem;
                min-height: 112px;
            }

            .metric-label {
                color: #cbd5e1;
                font-size: 0.86rem;
                margin-bottom: 0.35rem;
            }

            .metric-value {
                color: #f8fafc;
                font-size: 1.4rem;
                font-weight: 700;
                line-height: 1.2;
                word-break: break-word;
            }

            .soft-card {
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 14px;
                background: rgba(15, 23, 42, 0.3);
                padding: 0.8rem;
                margin-bottom: 0.75rem;
            }

            .status-chip {
                display: inline-block;
                font-size: 0.77rem;
                font-weight: 700;
                border-radius: 999px;
                padding: 0.18rem 0.55rem;
                border: 1px solid transparent;
            }

            .status-online {
                color: #4ade80;
                background: rgba(34, 197, 94, 0.16);
                border-color: rgba(74, 222, 128, 0.35);
            }

            .status-offline {
                color: #f87171;
                background: rgba(239, 68, 68, 0.15);
                border-color: rgba(248, 113, 113, 0.35);
            }

            .status-warning {
                color: #facc15;
                background: rgba(234, 179, 8, 0.17);
                border-color: rgba(250, 204, 21, 0.35);
            }

            [data-testid="stDataFrame"] {
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 12px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_branding(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="brand-card">
            <div class="brand-title">{title}</div>
            <div class="brand-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str | None = None, icon: str | None = None):
    title_text = f"{icon} {title}" if icon else title
    st.title(title_text)
    if subtitle:
        st.markdown(f"<div class='app-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def render_section_title(title: str):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)


def render_metric_card(title: str, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(status: str):
    css_class = "status-warning"
    if status == "ONLINE":
        css_class = "status-online"
    elif status == "OFFLINE":
        css_class = "status-offline"

    st.markdown(
        f"<span class='status-chip {css_class}'>{status}</span>",
        unsafe_allow_html=True,
    )


def render_empty_state(message: str):
    st.markdown(
        f"""
        <div class="soft-card">
            <strong>Sem dados</strong><br>{message}
        </div>
        """,
        unsafe_allow_html=True,
    )
