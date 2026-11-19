"""Load the research archive, newest first, for pages and metadata."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def load_blogs():
    posts = [json.loads(path.read_text(encoding='utf-8'))
             for path in sorted((ROOT / 'content').glob('blog-*.json'))]
    assert posts and len({post['slug'] for post in posts}) == len(posts)
    return sorted(posts, key=lambda post: post['published'], reverse=True)
