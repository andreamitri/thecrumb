from flask import Flask, render_template, request, redirect, url_for, abort
from datetime import date

from modules.models     import BlogPost, Comment
from modules.storage    import (
    load_posts, get_post_by_id, add_post, update_post,
    get_comments_for_post, add_comment,
    get_all_tags, get_posts_by_tag,
    next_post_id, next_comment_id,
)
from modules.validation import validate_comment, validate_post

app = Flask(__name__)


@app.route("/")
def home():
    posts = load_posts()
    return render_template("home.html",
                           posts=posts,
                           all_tags=get_all_tags())


@app.route("/post/<int:post_id>")
def post_detail(post_id):
    post = get_post_by_id(post_id)
    if post is None:
        abort(404)
    comments = get_comments_for_post(post_id)
    return render_template("post.html",
                           post=post,
                           comments=comments,
                           all_tags=get_all_tags(),
                           errors=[],
                           form={})


@app.route("/post/<int:post_id>/comment", methods=["POST"])
def add_comment_route(post_id):
    post = get_post_by_id(post_id)
    if post is None:
        abort(404)
    title  = request.form.get("c_title", "").strip()
    body   = request.form.get("c_body",  "").strip()
    result = validate_comment(title, body)
    if not result["ok"]:
        comments = get_comments_for_post(post_id)
        return render_template("post.html",
                               post=post,
                               comments=comments,
                               all_tags=get_all_tags(),
                               errors=result["errors"],
                               form={"c_title": title, "c_body": body})
    new_comment = Comment(
        comment_id = next_comment_id(),
        post_id    = post_id,
        title      = title,
        body       = body,
        date       = date.today().isoformat(),
    )
    add_comment(new_comment)
    return redirect(url_for("post_detail", post_id=post_id) + "#comments")


@app.route("/new", methods=["GET", "POST"])
def new_post():
    if request.method == "GET":
        return render_template("edit_post.html",
                               post=None, errors=[],
                               form={}, all_tags=get_all_tags())
    title    = request.form.get("title",    "").strip()
    body     = request.form.get("body",     "").strip()
    tags_raw = request.form.get("tags",     "").strip()
    author   = request.form.get("author",   "Anonymous").strip()
    category = request.form.get("category", "General").strip()
    icon     = request.form.get("icon",     "🍞").strip()
    result   = validate_post(title, body, tags_raw)
    if not result["ok"]:
        return render_template("edit_post.html",
                               post=None,
                               errors=result["errors"],
                               all_tags=get_all_tags(),
                               form={"title": title, "body": body,
                                     "tags": tags_raw, "author": author,
                                     "category": category, "icon": icon})
    read_mins = max(1, round(len(body.split()) / 200))
    post = BlogPost(
        post_id   = next_post_id(),
        title     = title,
        date      = date.today().isoformat(),
        body      = body,
        tags      = result["tags"],
        author    = author,
        category  = category,
        icon      = icon,
        read_mins = read_mins,
    )
    add_post(post)
    return redirect(url_for("post_detail", post_id=post.post_id))


@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    post = get_post_by_id(post_id)
    if post is None:
        abort(404)
    if request.method == "GET":
        form = {
            "title":    post.title,
            "body":     post.body,
            "tags":     ", ".join(post.tags),
            "author":   post.author,
            "category": post.category,
            "icon":     post.icon,
        }
        return render_template("edit_post.html",
                               post=post, errors=[],
                               form=form, all_tags=get_all_tags())
    title    = request.form.get("title",    "").strip()
    body     = request.form.get("body",     "").strip()
    tags_raw = request.form.get("tags",     "").strip()
    author   = request.form.get("author",   post.author).strip()
    category = request.form.get("category", post.category).strip()
    icon     = request.form.get("icon",     post.icon).strip()
    result   = validate_post(title, body, tags_raw)
    if not result["ok"]:
        return render_template("edit_post.html",
                               post=post,
                               errors=result["errors"],
                               all_tags=get_all_tags(),
                               form={"title": title, "body": body,
                                     "tags": tags_raw, "author": author,
                                     "category": category, "icon": icon})
    post.edit(title=title, body=body, tags=result["tags"])
    post.author    = author
    post.category  = category
    post.icon      = icon
    post.read_mins = max(1, round(len(body.split()) / 200))
    update_post(post)
    return redirect(url_for("post_detail", post_id=post_id))


@app.route("/tag/<tag>")
def tag_page(tag):
    posts = get_posts_by_tag(tag)
    return render_template("tag.html",
                           tag=tag,
                           posts=posts,
                           all_tags=get_all_tags())


@app.errorhandler(404)
def not_found(e):
    return "<h1>404 — Page not found</h1><a href='/'>← Home</a>", 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)