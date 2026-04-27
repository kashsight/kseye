"""
ks-eye HTML/PDF Export Formatter v2
Generates beautiful HTML reports with charts, tables, and formatting
Can optionally convert to PDF if weasyprint is installed
"""

import os
import json
from datetime import datetime
from ks_eye.config import config


def generate_html_report(report_data, output_path=None, include_charts=True):
    """
    Generate a beautiful HTML report from research data
    
    Args:
        report_data: Dict with metadata, sections, sources, etc.
        output_path: Where to save the HTML file
        include_charts: Whether to include Chart.js visualizations
    """
    
    # Build HTML with embedded CSS and JS
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data.get('metadata', {}).get('title', 'Research Report')}</title>
    <style>
        :root {{
            --primary: #0066cc;
            --secondary: #00a86b;
            --accent: #ff6b35;
            --bg: #f8f9fa;
            --text: #333;
            --border: #dee2e6;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: var(--bg);
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 3rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        header {{
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 3px solid var(--primary);
        }}
        
        h1 {{
            color: var(--primary);
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }}
        
        .meta-info {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
            margin-top: 1rem;
            font-size: 0.9rem;
            color: #555;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .meta-item strong {{
            color: var(--primary);
        }}
        
        section {{
            margin-bottom: 2.5rem;
            page-break-inside: avoid;
        }}
        
        h2 {{
            color: var(--primary);
            font-size: 1.8rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
        }}
        
        h3 {{
            color: var(--secondary);
            font-size: 1.4rem;
            margin: 1.5rem 0 1rem;
        }}
        
        p {{
            margin-bottom: 1rem;
            text-align: justify;
        }}
        
        ul, ol {{
            margin-left: 2rem;
            margin-bottom: 1rem;
        }}
        
        li {{
            margin-bottom: 0.5rem;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            overflow-x: auto;
            display: block;
        }}
        
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background: var(--primary);
            color: white;
            font-weight: 600;
        }}
        
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        tr:hover {{
            background: #e9ecef;
        }}
        
        .chart-container {{
            margin: 2rem 0;
            padding: 1.5rem;
            background: white;
            border: 1px solid var(--border);
            border-radius: 8px;
        }}
        
        .chart-title {{
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: var(--primary);
        }}
        
        .sources-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }}
        
        .source-card {{
            padding: 1rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: #f8f9fa;
        }}
        
        .source-card h4 {{
            color: var(--primary);
            margin-bottom: 0.5rem;
        }}
        
        .source-card .meta {{
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 0.5rem;
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-right: 0.5rem;
        }}
        
        .badge-academic {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-news {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid var(--border);
            text-align: center;
            color: #666;
            font-size: 0.9rem;
        }}
        
        @media print {{
            body {{
                padding: 0;
                background: white;
            }}
            .container {{
                box-shadow: none;
                padding: 1rem;
            }}
            section {{
                page-break-inside: avoid;
            }}
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            .container {{
                padding: 1.5rem;
            }}
            h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{report_data.get('metadata', {}).get('title', 'Research Report')}</h1>
            <div class="subtitle">{report_data.get('metadata', {}).get('subtitle', '')}</div>
            <div class="meta-info">
                <div class="meta-item">
                    <strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y')}
                </div>
                <div class="meta-item">
                    <strong>Sources:</strong> {len(report_data.get('sources', []))}
                </div>
                <div class="meta-item">
                    <strong>Word Count:</strong> {report_data.get('metadata', {}).get('word_count', 'N/A')}
                </div>
            </div>
        </header>
"""
    
    # Add statistics section if available
    if report_data.get('statistics'):
        html += """
        <section>
            <h2>📊 Research Statistics</h2>
            <div class="stats-grid">
"""
        for stat_name, stat_value in report_data['statistics'].items():
            html += f"""
                <div class="stat-card">
                    <div class="stat-number">{stat_value}</div>
                    <div class="stat-label">{stat_name.replace('_', ' ').title()}</div>
                </div>
"""
        html += """
            </div>
        </section>
"""
    
    # Add each section
    for section in report_data.get('sections', []):
        section_title = section.get('title', 'Untitled Section')
        section_content = section.get('content', '')
        
        html += f"""
        <section>
            <h2>{section_title}</h2>
            {section_content}
        </section>
"""
    
    # Add sources grid
    if report_data.get('sources'):
        html += """
        <section>
            <h2>📚 Sources Referenced</h2>
            <div class="sources-grid">
"""
        for i, source in enumerate(report_data['sources'][:20], 1):
            title = source.get('title', 'Untitled')
            authors = source.get('authors', 'Unknown')
            year = source.get('year', 'N/A')
            source_name = source.get('source', 'Unknown')
            category = source.get('type', 'academic')
            
            html += f"""
                <div class="source-card">
                    <h4>{i}. {title}</h4>
                    <div class="meta">
                        <div><strong>Authors:</strong> {authors}</div>
                        <div><strong>Year:</strong> {year}</div>
                        <div><strong>Source:</strong> {source_name}</div>
                    </div>
                    <span class="badge badge-{category}">{category}</span>
                </div>
"""
        html += """
            </div>
        </section>
"""
    
    # Add charts if requested
    if include_charts and report_data.get('charts'):
        html += """
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
"""
        for chart in report_data['charts']:
            html += f"""
        <div class="chart-container">
            <div class="chart-title">{chart.get('title', 'Chart')}</div>
            <canvas id="{chart.get('id', 'chart')}"></canvas>
            <script>
                new Chart(document.getElementById('{chart.get('id', 'chart')}'), {{
                    type: '{chart.get('type', 'bar')}',
                    data: {json.dumps(chart.get('data', {}))},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{
                                position: 'top',
                            }},
                        }},
                    }},
                }});
            </script>
        </div>
"""
    
    # Close HTML
    html += f"""
        <footer>
            <p>Generated by <strong>ks-eye</strong> v1.0 — AI-Human Collaborative Research Assistant</p>
            <p style="margin-top: 0.5rem; font-size: 0.85rem;">
                Report generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
            </p>
        </footer>
    </div>
</body>
</html>
"""
    
    # Save HTML
    if not output_path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() else "_" for c in report_data.get('metadata', {}).get('title', 'report')[:50])
        output_path = os.path.join(config.RESEARCH_DIR, f"{safe_title}_{ts}.html")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return {
        "status": "saved",
        "filepath": output_path,
        "format": "html",
    }


def export_to_pdf(report_data, output_path=None):
    """
    Export to PDF using weasyprint (if installed)
    Falls back to HTML if weasyprint not available
    """
    try:
        from weasyprint import HTML
        
        # Generate HTML first
        html_result = generate_html_report(report_data)
        html_path = html_result["filepath"]
        
        # Convert to PDF
        if not output_path:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c if c.isalnum() else "_" for c in report_data.get('metadata', {}).get('title', 'report')[:50])
            output_path = os.path.join(config.RESEARCH_DIR, f"{safe_title}_{ts}.pdf")
        
        HTML(filename=html_path).write_pdf(output_path)
        
        return {
            "status": "saved",
            "filepath": output_path,
            "format": "pdf",
        }
    except ImportError:
        # weasyprint not installed, return HTML
        return {
            "status": "fallback_html",
            "message": "weasyprint not installed. Install with: pip install weasyprint",
            "result": generate_html_report(report_data),
        }
