# components/metrics.py
"""
Modern metrics display components with professional styling
Complete metrics module for all dashboard analytics
"""
import streamlit as st
from typing import Dict, List

# ============================================
# MODERN CSS FOR METRICS
# ============================================

def inject_metrics_css():
    """Inject modern CSS for metric cards"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Modern Metric Card */
    .modern-metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid transparent;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .modern-metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .modern-metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .metric-label {
        color: #718096;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }
    
    .metric-delta {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .metric-delta-positive {
        background: #d4edda;
        color: #155724;
    }
    
    .metric-delta-negative {
        background: #f8d7da;
        color: #721c24;
    }
    
    /* Gradient Metric Cards */
    .gradient-metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        transition: all 0.3s;
        height: 100%;
    }
    
    .gradient-metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.4);
    }
    
    .gradient-metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    
    .gradient-metric-label {
        font-size: 0.875rem;
        opacity: 0.95;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-success { background: #d4edda; color: #155724; }
    .badge-warning { background: #fff3cd; color: #856404; }
    .badge-danger { background: #f8d7da; color: #721c24; }
    .badge-info { background: #d1ecf1; color: #0c5460; }
    .badge-secondary { background: #e9ecef; color: #6c757d; }
    
    /* KPI Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    /* Progress Bar */
    .progress-container {
        background: #e9ecef;
        border-radius: 10px;
        height: 10px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Comparison Card */
    .comparison-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.25rem;
        border-left: 4px solid #667eea;
    }
    
    .comparison-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a202c;
    }
    
    .comparison-label {
        color: #718096;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# MODERN METRIC RENDERERS
# ============================================

def render_modern_metric(label: str, value, icon: str = "📊", gradient_colors: tuple = ("#667eea", "#764ba2"), delta: str = None):
    """Render a single modern metric card with gradient"""
    inject_metrics_css()
    
    delta_html = ""
    if delta:
        delta_class = "metric-delta-positive" if "+" in str(delta) or "↑" in str(delta) else "metric-delta-negative"
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'
    
    st.markdown(f"""
    <div class="gradient-metric-card" style="background: linear-gradient(135deg, {gradient_colors[0]} 0%, {gradient_colors[1]} 100%);">
        <div class="metric-icon">{icon}</div>
        <div class="gradient-metric-value">{value}</div>
        <div class="gradient-metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_metric_grid(metrics: List[Dict]):
    """Render multiple metrics in a responsive grid"""
    inject_metrics_css()
    
    cols = st.columns(len(metrics))
    
    gradient_presets = [
        ("#667eea", "#764ba2"),
        ("#f093fb", "#f5576c"),
        ("#4facfe", "#00f2fe"),
        ("#43e97b", "#38f9d7"),
        ("#ffd89b", "#19547b"),
        ("#ff6b6b", "#ee5a6f")
    ]
    
    for idx, (col, metric) in enumerate(zip(cols, metrics)):
        with col:
            colors = metric.get('colors', gradient_presets[idx % len(gradient_presets)])
            render_modern_metric(
                label=metric.get('label', 'Metric'),
                value=metric.get('value', 0),
                icon=metric.get('icon', '📊'),
                gradient_colors=colors,
                delta=metric.get('delta')
            )

# ============================================
# ALLOCATION METRICS
# ============================================

def render_allocation_metrics(allocations: List[Dict]):
    """Render allocation summary metrics with modern cards"""
    inject_metrics_css()
    
    # Calculate metrics
    total = len(allocations)
    
    category_count = {}
    for a in allocations:
        cat_type = a.get('trial_category_type', 'Unknown')
        if not cat_type:
            cat = a.get('trial_category', 'Unknown')
            cat_type = 'Change Request' if 'Change Request' in cat else 'Build'
        category_count[cat_type] = category_count.get(cat_type, 0) + 1
    
    systems_count = {}
    for a in allocations:
        sys = a.get('system', 'Unknown')
        systems_count[sys] = systems_count.get(sys, 0) + 1
    
    build_count = category_count.get('Build', 0)
    cr_count = category_count.get('Change Request', 0)
    unique_systems = len(systems_count)
    
    # Render as modern metric grid
    metrics = [
        {
            'label': 'Total Allocations',
            'value': total,
            'icon': '📊',
            'colors': ('#667eea', '#764ba2')
        },
        {
            'label': 'Build Projects',
            'value': build_count,
            'icon': '🏗️',
            'colors': ('#4facfe', '#00f2fe')
        },
        {
            'label': 'Change Requests',
            'value': cr_count,
            'icon': '🔄',
            'colors': ('#f093fb', '#f5576c')
        },
        {
            'label': 'Unique Systems',
            'value': unique_systems,
            'icon': '💻',
            'colors': ('#43e97b', '#38f9d7')
        }
    ]
    
    render_metric_grid(metrics)

def render_allocation_summary_metrics(stats: Dict):
    """Render allocation summary from stats dictionary"""
    inject_metrics_css()
    
    by_category = stats.get('by_category', {})
    by_system = stats.get('by_system', {})
    by_engineer = stats.get('by_engineer', {})
    
    metrics = [
        {
            'label': 'Total Allocations',
            'value': stats.get('total', 0),
            'icon': '📊',
            'colors': ('#667eea', '#764ba2')
        },
        {
            'label': 'Build Projects',
            'value': by_category.get('Build', 0),
            'icon': '🏗️',
            'colors': ('#4facfe', '#00f2fe')
        },
        {
            'label': 'Change Requests',
            'value': by_category.get('Change Request', 0),
            'icon': '🔄',
            'colors': ('#f093fb', '#f5576c')
        },
        {
            'label': 'Active Engineers',
            'value': len(by_engineer),
            'icon': '👥',
            'colors': ('#43e97b', '#38f9d7')
        },
        {
            'label': 'Systems',
            'value': len(by_system),
            'icon': '💻',
            'colors': ('#ffd89b', '#19547b')
        }
    ]
    
    render_metric_grid(metrics)

def render_allocation_detailed_metrics(stats: Dict):
    """Render detailed allocation metrics with breakdown"""
    inject_metrics_css()
    
    st.markdown("### 📊 Allocation Overview")
    
    # Top metrics
    render_allocation_summary_metrics(stats)
    
    st.markdown("---")
    
    # Detailed breakdowns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏗️ Trial Categories")
        by_category = stats.get('by_category', {})
        for category, count in by_category.items():
            percentage = (count / stats.get('total', 1) * 100)
            st.markdown(f"""
            <div class="comparison-card">
                <div class="comparison-label">{category}</div>
                <div class="comparison-value">{count}</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {percentage}%;"></div>
                </div>
                <div style="color: #718096; font-size: 0.875rem; margin-top: 0.25rem;">{percentage:.1f}%</div>
            </div>
            <br>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 💻 Top Systems")
        by_system = stats.get('by_system', {})
        sorted_systems = sorted(by_system.items(), key=lambda x: x[1], reverse=True)[:5]
        for system, count in sorted_systems:
            percentage = (count / stats.get('total', 1) * 100)
            st.markdown(f"""
            <div class="comparison-card">
                <div class="comparison-label">{system}</div>
                <div class="comparison-value">{count}</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {percentage}%;"></div>
                </div>
                <div style="color: #718096; font-size: 0.875rem; margin-top: 0.25rem;">{percentage:.1f}%</div>
            </div>
            <br>
            """, unsafe_allow_html=True)

# ============================================
# UAT METRICS
# ============================================

def render_uat_summary_metrics(stats: Dict):
    """Render UAT summary metrics with modern design"""
    inject_metrics_css()
    
    by_status = stats.get('by_status', {})
    by_result = stats.get('by_result', {})
    total = stats.get('total', 0)
    completed = by_status.get('Completed', 0)
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    metrics = [
        {
            'label': 'Total Records',
            'value': total,
            'icon': '📋',
            'colors': ('#667eea', '#764ba2')
        },
        {
            'label': 'Completed',
            'value': completed,
            'icon': '✅',
            'colors': ('#43e97b', '#38f9d7'),
            'delta': f'{completion_rate:.1f}%'
        },
        {
            'label': 'In Progress',
            'value': by_status.get('In Progress', 0),
            'icon': '🔄',
            'colors': ('#4facfe', '#00f2fe')
        },
        {
            'label': 'Passed',
            'value': by_result.get('Pass', 0),
            'icon': '✅',
            'colors': ('#43e97b', '#38f9d7')
        },
        {
            'label': 'Failed',
            'value': by_result.get('Fail', 0),
            'icon': '❌',
            'colors': ('#ff6b6b', '#ee5a6f')
        }
    ]
    
    render_metric_grid(metrics)

def render_uat_detailed_metrics(stats: Dict):
    """Render detailed UAT metrics with breakdowns"""
    inject_metrics_css()
    
    st.markdown("### 📊 UAT Analytics")
    
    render_uat_summary_metrics(stats)
    
    st.markdown("---")
    
    # Status breakdown with progress bars
    st.markdown("#### 📊 Status Breakdown")
    by_status = stats.get('by_status', {})
    total = stats.get('total', 1)
    
    status_colors = {
        "Not Started": "#9E9E9E",
        "In Progress": "#4facfe",
        "Completed": "#43e97b",
        "On Hold": "#FFC107",
        "Cancelled": "#ff6b6b"
    }
    
    for status, count in by_status.items():
        percentage = (count / total * 100)
        color = status_colors.get(status, "#667eea")
        
        st.markdown(f"""
        <div class="comparison-card" style="border-left-color: {color};">
            <div class="comparison-label">{status}</div>
            <div class="comparison-value">{count}</div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {percentage}%; background: {color};"></div>
            </div>
            <div style="color: #718096; font-size: 0.875rem; margin-top: 0.25rem;">{percentage:.1f}%</div>
        </div>
        <br>
        """, unsafe_allow_html=True)

# ============================================
# AUDIT METRICS
# ============================================

def render_audit_metrics(stats: Dict):
    """Render audit log metrics"""
    inject_metrics_css()
    
    by_action = stats.get('by_action', {})
    by_user = stats.get('by_user', {})
    by_module = stats.get('by_module', {})
    
    most_common_action = max(by_action.items(), key=lambda x: x[1], default=("N/A", 0))[0]
    most_active_user = max(by_user.items(), key=lambda x: x[1], default=("N/A", 0))[0]
    
    metrics = [
        {
            'label': 'Total Logs',
            'value': stats.get('total', 0),
            'icon': '📝',
            'colors': ('#667eea', '#764ba2')
        },
        {
            'label': 'Unique Users',
            'value': len(by_user),
            'icon': '👥',
            'colors': ('#f093fb', '#f5576c')
        },
        {
            'label': 'Actions Tracked',
            'value': len(by_action),
            'icon': '⚡',
            'colors': ('#4facfe', '#00f2fe')
        },
        {
            'label': 'Modules',
            'value': len(by_module),
            'icon': '📦',
            'colors': ('#43e97b', '#38f9d7')
        }
    ]
    
    render_metric_grid(metrics)

def render_audit_detailed_metrics(stats: Dict):
    """Render detailed audit metrics"""
    inject_metrics_css()
    
    st.markdown("### 🔍 Audit Analytics")
    
    render_audit_metrics(stats)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Top Actions")
        by_action = stats.get('by_action', {})
        sorted_actions = sorted(by_action.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for action, count in sorted_actions:
            percentage = (count / stats.get('total', 1) * 100)
            st.markdown(f"""
            <div class="comparison-card">
                <div class="comparison-label">{action}</div>
                <div class="comparison-value">{count}</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {percentage}%;"></div>
                </div>
                <div style="color: #718096; font-size: 0.875rem; margin-top: 0.25rem;">{percentage:.1f}%</div>
            </div>
            <br>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 👥 Top Users")
        by_user = stats.get('by_user', {})
        sorted_users = sorted(by_user.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for user, count in sorted_users:
            percentage = (count / stats.get('total', 1) * 100)
            st.markdown(f"""
            <div class="comparison-card">
                <div class="comparison-label">{user}</div>
                <div class="comparison-value">{count}</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {percentage}%;"></div>
                </div>
                <div style="color: #718096; font-size: 0.875rem; margin-top: 0.25rem;">{percentage:.1f}%</div>
            </div>
            <br>
            """, unsafe_allow_html=True)

# ============================================
# GENERIC UTILITY METRICS
# ============================================

def render_percentage_metric_card(label: str, numerator: int, denominator: int, icon: str = "📊", colors: tuple = ("#667eea", "#764ba2")):
    """Render a percentage metric as a card"""
    inject_metrics_css()
    
    percentage = (numerator / denominator * 100) if denominator > 0 else 0
    
    st.markdown(f"""
    <div class="gradient-metric-card" style="background: linear-gradient(135deg, {colors[0]} 0%, {colors[1]} 100%);">
        <div class="metric-icon">{icon}</div>
        <div class="gradient-metric-value">{numerator}/{denominator}</div>
        <div class="gradient-metric-label">{label}</div>
        <div class="metric-delta metric-delta-positive">{percentage:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

def render_comparison_metrics(label1: str, value1: int, label2: str, value2: int):
    """Render comparison between two metrics"""
    inject_metrics_css()
    
    col1, col2 = st.columns(2)
    
    delta = value2 - value1
    delta_percentage = (delta / value1 * 100) if value1 > 0 else 0
    delta_text = f"{'+' if delta > 0 else ''}{delta} ({delta_percentage:+.1f}%)"
    
    with col1:
        render_modern_metric(label1, value1, "📊", ("#667eea", "#764ba2"))
    
    with col2:
        render_modern_metric(label2, value2, "📈", ("#43e97b", "#38f9d7"), delta=delta_text)

def render_kpi_cards(kpis: List[Dict]):
    """Render KPI cards in a responsive grid"""
    inject_metrics_css()
    render_metric_grid(kpis)

def render_status_badges(status_dict: Dict):
    """Render status badges"""
    inject_metrics_css()
    
    badge_classes = {
        "Completed": "badge-success",
        "Pass": "badge-success",
        "In Progress": "badge-info",
        "Pending": "badge-warning",
        "Failed": "badge-danger",
        "Fail": "badge-danger",
        "On Hold": "badge-warning",
        "Cancelled": "badge-secondary",
        "Not Started": "badge-secondary"
    }
    
    html = ""
    for status, count in status_dict.items():
        badge_class = badge_classes.get(status, "badge-secondary")
        html += f'<span class="status-badge {badge_class}">{status}: {count}</span>'
    
    st.markdown(html, unsafe_allow_html=True)

def render_quick_stats_grid(data_dict: Dict, title: str = "", max_items: int = 6, show_percentage: bool = True):
    """Render quick statistics in a modern grid"""
    inject_metrics_css()
    
    if title:
        st.markdown(f"### {title}")
    
    if not data_dict:
        st.info("📊 No data available")
        return
    
    sorted_items = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)[:max_items]
    total = sum(data_dict.values())
    
    cols = st.columns(min(3, len(sorted_items)))
    
    for idx, (key, value) in enumerate(sorted_items):
        with cols[idx % 3]:
            percentage = (value / total * 100) if show_percentage and total > 0 else None
            delta = f"{percentage:.1f}%" if percentage is not None else None
            
            render_modern_metric(
                label=key,
                value=value,
                icon="📊",
                gradient_colors=("#667eea", "#764ba2"),
                delta=delta
            )