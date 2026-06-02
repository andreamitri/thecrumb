"""
modules/database.py
-------------------
All database interactions for Crumb & Hearth.
Uses SQLite with parameterised queries throughout.

Usage:
    from modules.database import (
        get_all_posts, get_post_by_id,
        create_post, update_post, delete_post,
        get_comments_for_post, create_comment,
        get_all_tags, get_posts_by_tag,
        search_posts, get_stats,
    )
"""

import sqlite3
import os
from datetime import date
from modules.models import BlogPost, Comment


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "blog.db")


# Connection helpers

def _connect():
    """
    Open a connection to the SQLite database.
    row_factory lets us access columns by name: row["title"]
    instead of by index: row[1]
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _row_to_post(row, tags):
    """Convert a database row and tag list into a BlogPost object."""
    return BlogPost(
        post_id   = row["post_id"],
        title     = row["title"],
        date      = row["date"],
        body      = row["body"],
        tags      = tags,
        author    = row["author"],
        category  = row["category"],
        icon      = row["icon"],
        read_mins = row["read_mins"],
    )


def _row_to_comment(row):
    """Convert a database row into a Comment object."""
    return Comment(
        comment_id = row["comment_id"],
        post_id    = row["post_id"],
        title      = row["title"],
        body       = row["body"],
        date       = row["date"],
    )


def _get_tags_for_post(cursor, post_id):
    """
    Fetch all tag names for a given post.
    Uses a JOIN across tags and post_tags tables.
    The ? is a parameterised placeholder — never string-format
    values into SQL queries.
    """
    cursor.execute("""
        SELECT t.name
        FROM   tags t
        JOIN   post_tags pt ON t.tag_id = pt.tag_id
        WHERE  pt.post_id = ?
        ORDER  BY t.name
    """, (post_id,))
    return [row["name"] for row in cursor.fetchall()]


def _upsert_tags(cursor, post_id, tags):
    """
    Save tags for a post:
    1. Delete existing tag associations for this post
    2. Insert each tag into tags table if it does not exist
    3. Create the post-tag association
    """

    cursor.execute(
        "DELETE FROM post_tags WHERE post_id = ?",
        (post_id,)
    )

    for tag_name in tags:

        cursor.execute(
            "INSERT OR IGNORE INTO tags (name) VALUES (?)",
            (tag_name,)
        )

        cursor.execute(
            "SELECT tag_id FROM tags WHERE name = ?",
            (tag_name,)
        )
        tag_id = cursor.fetchone()["tag_id"]

        cursor.execute(
            "INSERT OR IGNORE INTO post_tags (post_id, tag_id) VALUES (?, ?)",
            (post_id, tag_id)
        )


# Post queries 

def get_all_posts():
    """
    Return all posts ordered newest first.
    Each post is a BlogPost object with its tags list populated.
    """
    conn   = _connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT post_id, title, date, body, author, category, icon, read_mins
        FROM   posts
        ORDER  BY date DESC, post_id DESC
    """)
    rows  = cursor.fetchall()
    posts = []
    for row in rows:
        tags = _get_tags_for_post(cursor, row["post_id"])
        posts.append(_row_to_post(row, tags))

    conn.close()
    return posts


def get_post_by_id(post_id):
    """
    Return a single BlogPost by ID, or None if not found.
    """
    conn   = _connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT post_id, title, date, body, author, category, icon, read_mins
        FROM   posts
        WHERE  post_id = ?
    """, (post_id,))

    row = cursor.fetchone()
    if row is None:
        conn.close()
        return None

    tags = _get_tags_for_post(cursor, post_id)
    post = _row_to_post(row, tags)
    conn.close()
    return post


def create_post(title, body, tags, author, category, icon, read_mins):
    """
    Insert a new post and its tags into the database.
    Returns the created BlogPost object.
    """
    conn   = _connect()
    cursor = conn.cursor()
    today  = date.today().isoformat()

    cursor.execute("""
        INSERT INTO posts (title, date, body, author, category, icon, read_mins)
        VALUES            (?,     ?,    ?,    ?,      ?,        ?,    ?)
    """, (title, today, body, author, category, icon, read_mins))

   
    post_id = cursor.lastrowid

    _upsert_tags(cursor, post_id, tags)
    conn.commit()
    conn.close()

    return get_post_by_id(post_id)


def update_post(post_id, title, body, tags, author, category, icon, read_mins):
    """
    Update an existing post's fields and tags.
    Returns True on success, False if the post was not found.
    """
    conn   = _connect()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE posts
        SET    title = ?, body = ?, author = ?,
               category = ?, icon = ?, read_mins = ?
        WHERE  post_id = ?
    """, (title, body, author, category, icon, read_mins, post_id))

    if cursor.rowcount == 0:
        conn.close()
        return False

    _upsert_tags(cursor, post_id, tags)
    conn.commit()
    conn.close()
    return True


def delete_post(post_id):
    """
    Delete a post. ON DELETE CASCADE in the schema automatically
    removes its comments and tag associations too.
    Returns True if deleted, False if not found.
    """
    conn   = _connect()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM posts WHERE post_id = ?",
        (post_id,)
    )
    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()
    return deleted


# Comment queries 

def get_comments_for_post(post_id):
    """
    Return all comments for a post, newest first.
    """
    conn   = _connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT comment_id, post_id, title, body, date
        FROM   comments
        WHERE  post_id = ?
        ORDER  BY date DESC, comment_id DESC
    """, (post_id,))

    comments = [_row_to_comment(row) for row in cursor.fetchall()]
    conn.close()
    return comments


def create_comment(post_id, title, body):
    """
    Insert a new comment and return the created Comment object.
    """
    conn   = _connect()
    cursor = conn.cursor()
    today  = date.today().isoformat()

    cursor.execute("""
        INSERT INTO comments (post_id, title, body, date)
        VALUES               (?,       ?,     ?,    ?)
    """, (post_id, title, body, today))

    comment_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return Comment(
        comment_id = comment_id,
        post_id    = post_id,
        title      = title,
        body       = body,
        date       = today,
    )


def delete_comment(comment_id):
    """
    Delete a single comment.
    Returns True if deleted, False if not found.
    """
    conn   = _connect()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM comments WHERE comment_id = ?",
        (comment_id,)
    )
    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()
    return deleted


# Tag queries 

def get_all_tags():
    """
    Return a sorted list of every tag that has at least one post.
    """
    conn   = _connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT t.name
        FROM   tags t
        JOIN   post_tags pt ON t.tag_id = pt.tag_id
        ORDER  BY t.name
    """)
    tags = [row["name"] for row in cursor.fetchall()]
    conn.close()
    return tags


def get_posts_by_tag(tag_name):
    """
    Return all posts that have a given tag, newest first.
    """
    conn   = _connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT p.post_id, p.title, p.date, p.body,
                        p.author, p.category, p.icon, p.read_mins
        FROM   posts p
        JOIN   post_tags pt ON p.post_id = pt.post_id
        JOIN   tags      t  ON pt.tag_id = t.tag_id
        WHERE  t.name = ?
        ORDER  BY p.date DESC
    """, (tag_name,))

    rows  = cursor.fetchall()
    posts = []
    for row in rows:
        tags = _get_tags_for_post(cursor, row["post_id"])
        posts.append(_row_to_post(row, tags))

    conn.close()
    return posts


# Search 

def search_posts(query):
    """
    Search post titles and bodies for a keyword.
    Uses LIKE with parameterised wildcards — safe from SQL injection.
    """
    conn    = _connect()
    cursor  = conn.cursor()
    pattern = "%" + query.strip() + "%"

    cursor.execute("""
        SELECT DISTINCT post_id, title, date, body,
                        author, category, icon, read_mins
        FROM   posts
        WHERE  title LIKE ? OR body LIKE ?
        ORDER  BY date DESC
    """, (pattern, pattern))

    rows  = cursor.fetchall()
    posts = []
    for row in rows:
        tags = _get_tags_for_post(cursor, row["post_id"])
        posts.append(_row_to_post(row, tags))

    conn.close()
    return posts


# Stats 

def get_stats():
    """
    Return a dictionary of blog statistics.
    Demonstrates SQL aggregate functions: COUNT, AVG, SUM, MAX, MIN.
    """
    conn   = _connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*)                  AS total_posts,
            ROUND(AVG(read_mins), 1)  AS avg_read_mins,
            SUM(read_mins)            AS total_read_mins
        FROM posts
    """)
    row = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) AS n FROM comments"
    )
    comment_count = cursor.fetchone()["n"]

    cursor.execute("""
        SELECT COUNT(DISTINCT t.tag_id) AS n
        FROM   tags t
        JOIN   post_tags pt ON t.tag_id = pt.tag_id
    """)
    tag_count = cursor.fetchone()["n"]

    cursor.execute("""
        SELECT t.name, COUNT(*) AS c
        FROM   tags t
        JOIN   post_tags pt ON t.tag_id = pt.tag_id
        GROUP  BY t.tag_id
        ORDER  BY c DESC
        LIMIT  1
    """)
    top = cursor.fetchone()
    conn.close()

    return {
        "total_posts":     row["total_posts"],
        "avg_read_mins":   row["avg_read_mins"],
        "total_read_mins": row["total_read_mins"],
        "total_comments":  comment_count,
        "total_tags":      tag_count,
        "top_tag":         top["name"] if top else "",
    }