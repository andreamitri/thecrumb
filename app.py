from flask import Flask, render_template, request, redirect, url_for, abort
from modules.database   import (
    get_all_posts, get_post_by_id, create_post, update_post, delete_post,
    get_comments_for_post, create_comment,
    get_all_tags, get_posts_by_tag, search_posts, get_stats,
)
from modules.validation import validate_comment, validate_post

app = Flask(__name__)



@app.route("/")
def home():
    posts = get_all_posts()
    stats = get_stats()
    return render_template("home.html",
                           posts=posts,
                           stats=stats,
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

    create_comment(post_id, title, body)
    return redirect(url_for("post_detail", post_id=post_id) + "#comments")


@app.route("/new", methods=["GET", "POST"])
def new_post():
    if request.method == "GET":
        return render_template("edit_post.html",
                               post=None,
                               errors=[],
                               form={},
                               all_tags=get_all_tags())

    title    = request.form.get("title",    "").strip()
    body     = request.form.get("body",     "").strip()
    tags_raw = request.form.get("tags",     "").strip()
    author   = request.form.get("author",   "Anonymous").strip()
    category = request.form.get("category", "General").strip()
    icon     = request.form.get("icon",     "🍞").strip()

    result = validate_post(title, body, tags_raw)
    if not result["ok"]:
        return render_template("edit_post.html",
                               post=None,
                               errors=result["errors"],
                               all_tags=get_all_tags(),
                               form={"title": title, "body": body,
                                     "tags": tags_raw, "author": author,
                                     "category": category, "icon": icon})

    read_mins = max(1, round(len(body.split()) / 200))
    post = create_post(title, body, result["tags"],
                       author, category, icon, read_mins)
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
                               post=post,
                               errors=[],
                               form=form,
                               all_tags=get_all_tags())

    title    = request.form.get("title",    "").strip()
    body     = request.form.get("body",     "").strip()
    tags_raw = request.form.get("tags",     "").strip()
    author   = request.form.get("author",   post.author).strip()
    category = request.form.get("category", post.category).strip()
    icon     = request.form.get("icon",     post.icon).strip()

    result = validate_post(title, body, tags_raw)
    if not result["ok"]:
        return render_template("edit_post.html",
                               post=post,
                               errors=result["errors"],
                               all_tags=get_all_tags(),
                               form={"title": title, "body": body,
                                     "tags": tags_raw, "author": author,
                                     "category": category, "icon": icon})

    read_mins = max(1, round(len(body.split()) / 200))
    update_post(post_id, title, body, result["tags"],
                author, category, icon, read_mins)
    return redirect(url_for("post_detail", post_id=post_id))



@app.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post_route(post_id):
    delete_post(post_id)
    return redirect(url_for("home"))



@app.route("/tag/<tag>")
def tag_page(tag):
    posts = get_posts_by_tag(tag)
    return render_template("tag.html",
                           tag=tag,
                           posts=posts,
                           all_tags=get_all_tags())

 
@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    posts = search_posts(query) if query else []
    return render_template("search.html",
                           query=query,
                           posts=posts,
                           all_tags=get_all_tags())


# 404 
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", all_tags=get_all_tags()), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)