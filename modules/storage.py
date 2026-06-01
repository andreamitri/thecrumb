import json
import os
from modules.models import BlogPost, Comment

DATA_DIR      = os.path.join(os.path.dirname(__file__), "..", "data")
POSTS_FILE    = os.path.join(DATA_DIR, "posts.json")
COMMENTS_FILE = os.path.join(DATA_DIR, "comments.json")


def _read_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def _write_json(filepath, data):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False


def load_posts():
    posts = []
    for item in _read_json(POSTS_FILE):
        try:
            posts.append(BlogPost.from_dict(item))
        except KeyError:
            pass
    return posts


def save_posts(posts):
    return _write_json(POSTS_FILE, [p.to_dict() for p in posts])


def get_post_by_id(post_id):
    for post in load_posts():
        if post.post_id == post_id:
            return post
    return None


def add_post(post):
    posts = load_posts()
    if any(p.post_id == post.post_id for p in posts):
        return False
    posts.append(post)
    posts.sort(key=lambda p: p.date, reverse=True)
    return save_posts(posts)


def update_post(updated):
    posts = load_posts()
    for i, p in enumerate(posts):
        if p.post_id == updated.post_id:
            posts[i] = updated
            return save_posts(posts)
    return False


def load_comments():
    comments = []
    for item in _read_json(COMMENTS_FILE):
        try:
            comments.append(Comment(**item))
        except (KeyError, TypeError):
            pass
    return comments


def save_comments(comments):
    return _write_json(COMMENTS_FILE, [c.to_dict() for c in comments])


def get_comments_for_post(post_id):
    return sorted(
        [c for c in load_comments() if c.post_id == post_id],
        key=lambda c: c.date,
        reverse=True
    )


def add_comment(comment):
    comments = load_comments()
    if any(c.comment_id == comment.comment_id for c in comments):
        return False
    comments.append(comment)
    return save_comments(comments)


def get_all_tags():
    tags = set()
    for post in load_posts():
        tags.update(post.tags)
    return sorted(tags)


def get_posts_by_tag(tag):
    return [p for p in load_posts() if tag in p.tags]


def next_post_id():
    posts = load_posts()
    return max((p.post_id for p in posts), default=0) + 1


def next_comment_id():
    comments = load_comments()
    return max((c.comment_id for c in comments), default=0) + 1