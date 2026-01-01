import base64
import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader

def b64encode_filter(data):
    if data:
        return base64.b64encode(data).decode('utf-8')
    return ""

def generate_html_report(history):
    """
    Generates a single HTML report string from the session history using Jinja2.
    """
    # Setup Jinja2 Environment
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))

    # Register custom filter for base64 encoding images
    env.filters['b64encode'] = b64encode_filter

    template = env.get_template('report.html')

    return template.render(
        history=history,
        generated_at=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    )
