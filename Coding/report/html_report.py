import markdown2
import os
import re
 
def html_report(md_text: str, output_path: str, source_name: str = 'Dataset'):
    html_body = markdown2.markdown(md_text, extras=["tables"])
    style = '''
    <style>
      * {box-sizing: border-box;}
      body {
        font-family: 'Segoe UI', Tahoma, Arial, sans-serif; 
        margin: 0;
        padding: 0;
        background: #f5f7fa;
        color: #2a2a2a;
        line-height: 1.6;
      }
      .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2em;
        background: white;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
      }
      h1 {
        color: #1a1a1a;
        font-size: 2.5em;
        margin: 0 0 0.5em 0;
        padding-bottom: 0.3em;
        border-bottom: 3px solid #4a90e2;
        font-weight: 600;
      }
      h2 {
        color: #2a2a2a;
        font-size: 1.8em;
        margin: 1.5em 0 0.8em 0;
        padding-bottom: 0.5em;
        border-bottom: 2px solid #e3e3e3;
        font-weight: 600;
      }
      h3 {
        color: #3a3a3a;
        font-size: 1.4em;
        margin: 1.2em 0 0.6em 0;
        font-weight: 600;
      }
      h4 {
        color: #4a4a4a;
        font-size: 1.2em;
        margin: 1em 0 0.5em 0;
        font-weight: 600;
      }
      .section {
        background: #fafbfd;
        border-radius: 8px;
        box-shadow: 0 1px 3px #e3e9f1;
        padding: 1.5em 2em;
        margin-bottom: 2em;
      }
      table {
        border-collapse: collapse;
        width: 100%;
        margin: 15px 0;
        font-size: 0.95em;
      }
      th, td {
        border: 1px solid #dee2e6;
        padding: 10px 12px;
        text-align: left;
      }
      th {
        background: #f3f6f7;
        font-weight: 600;
        color: #2a2a2a;
      }
      tr:nth-child(even) {
        background: #fafbfd;
      }
      hr {
        border: 0;
        border-top: 2px solid #e3e3e3;
        margin: 2em 0;
      }
      ul, ol {
        margin: 0.8em 0 0.8em 20px;
        padding-left: 0;
      }
      li {
        margin-bottom: 0.5em;
      }
      code {
        background: #f5f7f8;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
      }
      .insight {
        background: #d8eff8;
        border-left: 5px solid #1cb0f6;
        padding: 0.9em 1.3em;
        margin: 1.2em 0;
        border-radius: 5px;
        font-size: 1.02em;
      }
      .suggestions {
        background: #ffeec2;
        border-left: 5px solid #f1b100;
        padding: 1em 1.4em;
        margin: 1.2em 0;
        border-radius: 5px;
        font-size: 1.06em;
      }
      blockquote {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1em 1.4em;
        margin: 1.2em 0;
        border-radius: 5px;
        font-size: 1.05em;
      }
      img {
        max-width: 100%;
        height: auto;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1em 0;
      }
      p {
        margin: 0.8em 0;
      }
      strong {
        font-weight: 600;
        color: #1a1a1a;
      }
    </style>
    '''
    # Wrap each section (starting with h2) in a .section div
    def wrap_sections(html):
        s = re.sub(r'(<h2.*?>.*?</h2>)', r'</div>\1<div class="section">', html, flags=re.I)
        s = s.replace('<body>', '<body><div class="section">', 1) + '</div>'
        # decorate 'Suggested Transforms' blockquotes
        s = re.sub(r'<blockquote>\s*<p>\s*<strong>Suggested Transforms / Actions:</strong>',
                 '<blockquote class="suggestions"><p><strong>Suggested Transforms / Actions:</strong>',s,flags=re.I)
        return s
    
    html_body = wrap_sections(html_body)
    
    
    html_full = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDA Report - {source_name}</title>
    {style}
</head>
<body>
    {html_body}
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf8') as f:
        f.write(html_full)
 