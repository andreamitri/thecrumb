from datetime import datetime
import re


class Comment:
    def __init__(self, comment_id, post_id, title, body, date):
        self.comment_id = comment_id
        self.post_id    = post_id
        self.title      = title
        self.body       = body
        self.date       = date

    def formatted_date(self):
        try:
            dt = datetime.strptime(self.date, "%Y-%m-%d")
            return dt.strftime("%-d %B %Y")
        except ValueError:
            return self.date

    def to_dict(self):
        return {
            "comment_id": self.comment_id,
            "post_id":    self.post_id,
            "title":      self.title,
            "body":       self.body,
            "date":       self.date,
        }


class BlogPost:
    def __init__(self, post_id, title, date, body,
                 tags, author, category, icon, read_mins):
        self.post_id   = post_id
        self.title     = title
        self.date      = date
        self.body      = body
        self.tags      = tags
        self.author    = author
        self.category  = category
        self.icon      = icon
        self.read_mins = read_mins

    def excerpt(self, length=150):
        if len(self.body) <= length:
            return self.body
        trimmed = self.body[:length]
        last_space = trimmed.rfind(" ")
        return trimmed[:last_space] + "…"

    def formatted_date(self):
        try:
            dt = datetime.strptime(self.date, "%Y-%m-%d")
            return dt.strftime("%-d %B %Y")
        except ValueError:
            return self.date

    def slug(self):
        s = self.title.lower()
        s = re.sub(r"[^\w\s-]", "", s)
        s = re.sub(r"\s+", "-", s)
        return s

    def tag_string(self):
        return ", ".join("#" + t for t in self.tags)

    def byline(self):
        return self.author + " · " + str(self.read_mins) + " min read"

    def edit(self, title=None, body=None, tags=None):
        if title is not None:
            self.title = title
        if body is not None:
            self.body = body
        if tags is not None:
            self.tags = tags

    def to_dict(self):
        return {
            "post_id":   self.post_id,
            "title":     self.title,
            "date":      self.date,
            "body":      self.body,
            "tags":      self.tags,
            "author":    self.author,
            "category":  self.category,
            "icon":      self.icon,
            "read_mins": self.read_mins,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            post_id   = data["post_id"],
            title     = data["title"],
            date      = data["date"],
            body      = data["body"],
            tags      = data.get("tags", []),
            author    = data.get("author", "Unknown"),
            category  = data.get("category", ""),
            icon      = data.get("icon", "🍞"),
            read_mins = data.get("read_mins", 5),
        )