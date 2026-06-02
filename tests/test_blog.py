"""
tests/test_blog.py
------------------
Tests for modules/models.py and modules/validation.py.
44 tests covering BlogPost methods, Comment methods,
validation rules, and JSON file storage.

Run: python -m pytest tests/test_blog.py -v
"""

import sys, os, unittest, tempfile, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.models     import BlogPost, Comment
from modules.validation import validate_comment, validate_post


#  BlogPost — excerpt()


class TestBlogPostExcerpt(unittest.TestCase):

    def setUp(self):
        self.post = BlogPost(
            post_id=1, title="Test Post", date="2025-05-01",
            body="Word " * 60,
            tags=["test"], author="Tester", category="Tests",
            icon="🧪", read_mins=3
        )

    def test_excerpt_short_body_unchanged(self):
        short = BlogPost(1, "T", "2025-01-01", "Short body.", [], "A", "B", "🍞", 1)
        self.assertEqual(short.excerpt(150), "Short body.")

    def test_excerpt_trims_to_word_boundary(self):
        result = self.post.excerpt(20)
        self.assertFalse(result.endswith(" "))
        self.assertTrue(result.endswith("…"))

    def test_excerpt_default_length_150(self):
        result = self.post.excerpt()
        self.assertLessEqual(len(result), 155)

    def test_excerpt_exact_length(self):
        body = "a" * 150
        p = BlogPost(1, "T", "2025-01-01", body, [], "A", "B", "🍞", 1)
        self.assertEqual(p.excerpt(150), body)


#  BlogPost — slug()


class TestBlogPostSlug(unittest.TestCase):

    def test_slug_lowercases(self):
        p = BlogPost(1, "Hello World", "2025-01-01",
                     "body body body body body body", [], "A", "B", "🍞", 1)
        self.assertEqual(p.slug(), "hello-world")

    def test_slug_removes_punctuation(self):
        p = BlogPost(1, "It's Complicated!", "2025-01-01",
                     "body body body body body body", [], "A", "B", "🍞", 1)
        self.assertNotIn("'", p.slug())
        self.assertNotIn("!", p.slug())

    def test_slug_replaces_spaces_with_hyphens(self):
        p = BlogPost(1, "The Quick Brown Fox", "2025-01-01",
                     "b b b b b b b b", [], "A", "B", "🍞", 1)
        self.assertNotIn(" ", p.slug())
        self.assertIn("-", p.slug())


#  BlogPost — byline()


class TestBlogPostByline(unittest.TestCase):

    def test_byline_format(self):
        p = BlogPost(1, "T", "2025-01-01", "b", [], "Clara Bennet", "B", "🍞", 7)
        self.assertEqual(p.byline(), "Clara Bennet · 7 min read")

    def test_byline_includes_author(self):
        p = BlogPost(1, "T", "2025-01-01", "b", [], "James Holloway", "B", "🍞", 12)
        self.assertIn("James Holloway", p.byline())


#  BlogPost — formatted_date()


class TestBlogPostFormattedDate(unittest.TestCase):

    def test_formats_correctly(self):
        p = BlogPost(1, "T", "2025-05-14", "b", [], "A", "B", "🍞", 1)
        self.assertEqual(p.formatted_date(), "14 May 2025")

    def test_invalid_date_returns_original(self):
        p = BlogPost(1, "T", "not-a-date", "b", [], "A", "B", "🍞", 1)
        self.assertEqual(p.formatted_date(), "not-a-date")


#  BlogPost — serialisation


class TestBlogPostSerialization(unittest.TestCase):

    def setUp(self):
        self.data = {
            "post_id": 5, "title": "Test", "date": "2025-03-01",
            "body": "Some body text here.", "tags": ["a", "b"],
            "author": "Author", "category": "Cat", "icon": "🍞", "read_mins": 4
        }

    def test_from_dict_round_trip(self):
        post = BlogPost.from_dict(self.data)
        self.assertEqual(post.to_dict(), self.data)

    def test_from_dict_missing_optional_fields_use_defaults(self):
        minimal = {"post_id": 1, "title": "T", "date": "2025-01-01",
                   "body": "b", "tags": []}
        post = BlogPost.from_dict(minimal)
        self.assertEqual(post.author, "Unknown")
        self.assertEqual(post.read_mins, 5)

    def test_edit_updates_fields(self):
        post = BlogPost.from_dict(self.data)
        post.edit(title="New Title", tags=["x"])
        self.assertEqual(post.title, "New Title")
        self.assertEqual(post.tags, ["x"])
        self.assertEqual(post.body, "Some body text here.")


#  BlogPost — tag_string()


class TestBlogPostTagString(unittest.TestCase):

    def test_tag_string_format(self):
        p = BlogPost(1, "T", "2025-01-01", "b",
                     ["sourdough", "crust"], "A", "B", "🍞", 1)
        self.assertEqual(p.tag_string(), "#sourdough, #crust")

    def test_empty_tags(self):
        p = BlogPost(1, "T", "2025-01-01", "b", [], "A", "B", "🍞", 1)
        self.assertEqual(p.tag_string(), "")


#  Comment


class TestComment(unittest.TestCase):

    def setUp(self):
        self.comment = Comment(
            1, 1, "Great post!",
            "Really helped me understand the process.",
            "2025-05-20"
        )

    def test_formatted_date(self):
        self.assertEqual(self.comment.formatted_date(), "20 May 2025")

    def test_to_dict_round_trip(self):
        d  = self.comment.to_dict()
        c2 = Comment(**d)
        self.assertEqual(c2.title, self.comment.title)
        self.assertEqual(c2.body,  self.comment.body)

    def test_repr_contains_id(self):
        self.assertIn("1", str(self.comment.comment_id))


#  validate_comment()


class TestValidateComment(unittest.TestCase):

    def test_valid_comment_passes(self):
        result = validate_comment(
            "Great tip!",
            "This really helped me improve my baking."
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["errors"], [])

    def test_title_too_short(self):
        result = validate_comment(
            "ab",
            "This is a long enough body to be valid here."
        )
        self.assertFalse(result["ok"])
        self.assertTrue(any("3 characters" in e for e in result["errors"]))

    def test_title_too_long(self):
        result = validate_comment(
            "x" * 121,
            "This is a long enough body to be valid here."
        )
        self.assertFalse(result["ok"])
        self.assertTrue(any("120" in e for e in result["errors"]))

    def test_body_too_short(self):
        result = validate_comment("Fine title", "short")
        self.assertFalse(result["ok"])
        self.assertTrue(any("10 characters" in e for e in result["errors"]))

    def test_body_too_long(self):
        result = validate_comment("Fine title", "x" * 2001)
        self.assertFalse(result["ok"])
        self.assertTrue(any("2000" in e for e in result["errors"]))

    def test_strips_whitespace_before_checking(self):
        result = validate_comment("  ab  ", "  short  ")
        self.assertFalse(result["ok"])


#  validate_post()


class TestValidatePost(unittest.TestCase):

    GOOD_BODY = "A" * 60

    def test_valid_post_passes(self):
        result = validate_post(
            "A Good Title Here",
            self.GOOD_BODY,
            "bread, technique"
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["tags"], ["bread", "technique"])

    def test_title_too_short(self):
        result = validate_post("Hi", self.GOOD_BODY, "")
        self.assertFalse(result["ok"])
        self.assertTrue(any("5 characters" in e for e in result["errors"]))

    def test_body_too_short(self):
        result = validate_post("Valid Title Here", "Too short.", "")
        self.assertFalse(result["ok"])
        self.assertTrue(any("50 characters" in e for e in result["errors"]))

    def test_too_many_tags(self):
        tags = ", ".join(["tag" + str(i) for i in range(9)])
        result = validate_post("Valid Title Here", self.GOOD_BODY, tags)
        self.assertFalse(result["ok"])
        self.assertTrue(any("8 tags" in e for e in result["errors"]))

    def test_tags_parsed_and_lowercased(self):
        result = validate_post(
            "Valid Title Here",
            self.GOOD_BODY,
            "  Bread , SOURDOUGH , Technique  "
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["tags"], ["bread", "sourdough", "technique"])

    def test_empty_tags_allowed(self):
        result = validate_post("Valid Title Here", self.GOOD_BODY, "")
        self.assertTrue(result["ok"])
        self.assertEqual(result["tags"], [])

    def test_tag_too_short(self):
        result = validate_post("Valid Title Here", self.GOOD_BODY, "a, bread")
        self.assertFalse(result["ok"])
        self.assertTrue(any("too short" in e for e in result["errors"]))



#  Storage — JSON file I/O


class TestStorage(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        import modules.storage as storage
        self._orig_posts    = storage.POSTS_FILE
        self._orig_comments = storage.COMMENTS_FILE
        storage.POSTS_FILE    = os.path.join(self.test_dir, "posts.json")
        storage.COMMENTS_FILE = os.path.join(self.test_dir, "comments.json")

    def tearDown(self):
        import modules.storage as storage
        storage.POSTS_FILE    = self._orig_posts
        storage.COMMENTS_FILE = self._orig_comments
        shutil.rmtree(self.test_dir)

    def _make_post(self, post_id=1, title="Test Post", date="2025-01-01"):
        return BlogPost(
            post_id, title, date,
            "Body text " * 10, ["test"],
            "Author", "Cat", "🍞", 3
        )

    def test_save_and_load_posts(self):
        from modules.storage import save_posts, load_posts
        posts = [self._make_post(1), self._make_post(2, date="2025-02-01")]
        save_posts(posts)
        loaded = load_posts()
        self.assertEqual(len(loaded), 2)

    def test_load_missing_file_returns_empty(self):
        from modules.storage import load_posts
        result = load_posts()
        self.assertEqual(result, [])

    def test_add_post_persists(self):
        from modules.storage import add_post, load_posts
        add_post(self._make_post(1))
        loaded = load_posts()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].title, "Test Post")

    def test_add_duplicate_post_rejected(self):
        from modules.storage import add_post, load_posts
        post = self._make_post(1)
        add_post(post)
        add_post(post)
        self.assertEqual(len(load_posts()), 1)

    def test_update_post(self):
        from modules.storage import add_post, update_post, get_post_by_id
        post = self._make_post(1)
        add_post(post)
        post.edit(title="Updated Title")
        update_post(post)
        loaded = get_post_by_id(1)
        self.assertEqual(loaded.title, "Updated Title")

    def test_get_post_by_id_not_found_returns_none(self):
        from modules.storage import get_post_by_id
        result = get_post_by_id(999)
        self.assertIsNone(result)

    def test_add_and_load_comments(self):
        from modules.storage import add_comment, get_comments_for_post
        c = Comment(
            1, 1, "Good post!",
            "Really useful, thank you so much.",
            "2025-05-01"
        )
        add_comment(c)
        comments = get_comments_for_post(1)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].title, "Good post!")

    def test_get_comments_filters_by_post(self):
        from modules.storage import add_comment, get_comments_for_post
        c1 = Comment(1, 1, "For post 1",
                     "Comment on first post here.", "2025-05-01")
        c2 = Comment(2, 2, "For post 2",
                     "Comment on second post here.", "2025-05-02")
        add_comment(c1)
        add_comment(c2)
        self.assertEqual(len(get_comments_for_post(1)), 1)
        self.assertEqual(len(get_comments_for_post(2)), 1)
        self.assertEqual(len(get_comments_for_post(3)), 0)

    def test_get_all_tags(self):
        from modules.storage import add_post, get_all_tags
        add_post(BlogPost(1, "T", "2025-01-01", "b " * 10,
                          ["bread", "sourdough"], "A", "B", "🍞", 1))
        add_post(BlogPost(2, "T", "2025-01-02", "b " * 10,
                          ["bread", "cakes"], "A", "B", "🍞", 1))
        tags = get_all_tags()
        self.assertIn("bread",     tags)
        self.assertIn("sourdough", tags)
        self.assertIn("cakes",     tags)
        self.assertEqual(tags, sorted(set(tags)))

    def test_malformed_json_returns_empty(self):
        import modules.storage as storage
        with open(storage.POSTS_FILE, "w") as f:
            f.write("this is not valid json {{{")
        result = storage.load_posts()
        self.assertEqual(result, [])

    def test_next_post_id_increments(self):
        from modules.storage import add_post, next_post_id
        add_post(self._make_post(1))
        add_post(self._make_post(2))
        self.assertEqual(next_post_id(), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)