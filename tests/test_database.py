"""
tests/test_database.py
----------------------
Tests for modules/database.py.
46 tests covering all CRUD operations, tag queries,
search, stats, and SQL injection prevention.

Each test runs against a fresh temporary database
so real data is never touched.

Run: python -m pytest tests/test_database.py -v
"""

import sys, os, sqlite3, tempfile, shutil, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import modules.database as db



#  Base class — fresh temp database for every test


class DatabaseTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "test_blog.db")
        self._orig_db_path = db.DB_PATH
        db.DB_PATH = self.db_path

        schema_path = os.path.join(
            os.path.dirname(__file__), "..", "schema.sql"
        )
        with open(schema_path, "r", encoding="utf-8") as f:
            sql = f.read()
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.isolation_level = None
        conn.executescript(sql)
        conn.close()

    def tearDown(self):
        db.DB_PATH = self._orig_db_path
        shutil.rmtree(self.tmp_dir)

    def _make_post(self, title="Test Post Title Here",
                   body="Body text " * 10,
                   tags=None, author="Tester",
                   category="Tests", icon="🧪", read_mins=3):
        return db.create_post(
            title, body, tags or ["test"],
            author, category, icon, read_mins
        )


#  get_all_posts


class TestGetAllPosts(DatabaseTestCase):

    def test_returns_list(self):
        posts = db.get_all_posts()
        self.assertIsInstance(posts, list)

    def test_returns_blogpost_objects(self):
        from modules.models import BlogPost
        for p in db.get_all_posts():
            self.assertIsInstance(p, BlogPost)

    def test_sorted_newest_first(self):
        posts = db.get_all_posts()
        dates = [p.date for p in posts]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_each_post_has_tags(self):
        posts = db.get_all_posts()
        has_tags = any(len(p.tags) > 0 for p in posts)
        self.assertTrue(has_tags)


#  get_post_by_id


class TestGetPostById(DatabaseTestCase):

    def test_returns_correct_post(self):
        post = db.get_post_by_id(1)
        self.assertIsNotNone(post)
        self.assertEqual(post.post_id, 1)

    def test_returns_none_for_missing_id(self):
        self.assertIsNone(db.get_post_by_id(99999))

    def test_post_has_tags_list(self):
        post = db.get_post_by_id(1)
        self.assertIsInstance(post.tags, list)
        self.assertGreater(len(post.tags), 0)

    def test_post_fields_populated(self):
        post = db.get_post_by_id(1)
        self.assertTrue(post.title)
        self.assertTrue(post.body)
        self.assertTrue(post.author)
        self.assertTrue(post.date)

#  create_post


class TestCreatePost(DatabaseTestCase):

    def test_returns_blogpost(self):
        from modules.models import BlogPost
        post = self._make_post()
        self.assertIsInstance(post, BlogPost)

    def test_post_has_auto_incremented_id(self):
        post = self._make_post()
        self.assertIsInstance(post.post_id, int)
        self.assertGreater(post.post_id, 0)

    def test_post_appears_in_get_all(self):
        self._make_post(title="Unique Title XYZ")
        titles = [p.title for p in db.get_all_posts()]
        self.assertIn("Unique Title XYZ", titles)

    def test_tags_saved_correctly(self):
        post = self._make_post(tags=["bread", "sourdough", "easy"])
        fetched = db.get_post_by_id(post.post_id)
        self.assertIn("bread",     fetched.tags)
        self.assertIn("sourdough", fetched.tags)
        self.assertIn("easy",      fetched.tags)

    def test_tags_deduped_in_tags_table(self):
        self._make_post(tags=["shared-tag"])
        self._make_post(tags=["shared-tag"])
        conn = sqlite3.connect(self.db_path)
        cur  = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tags WHERE name = 'shared-tag'")
        count = cur.fetchone()[0]
        conn.close()
        self.assertEqual(count, 1)

    def test_multiple_posts_get_different_ids(self):
        p1 = self._make_post(title="Post One")
        p2 = self._make_post(title="Post Two")
        self.assertNotEqual(p1.post_id, p2.post_id)


#  update_post


class TestUpdatePost(DatabaseTestCase):

    def test_updates_title(self):
        post = self._make_post()
        db.update_post(post.post_id, "Updated Title Here",
                       post.body, post.tags, post.author,
                       post.category, post.icon, post.read_mins)
        fetched = db.get_post_by_id(post.post_id)
        self.assertEqual(fetched.title, "Updated Title Here")

    def test_updates_tags(self):
        post = self._make_post(tags=["old-tag"])
        db.update_post(post.post_id, post.title,
                       post.body, ["new-tag"], post.author,
                       post.category, post.icon, post.read_mins)
        fetched = db.get_post_by_id(post.post_id)
        self.assertIn("new-tag",    fetched.tags)
        self.assertNotIn("old-tag", fetched.tags)

    def test_returns_false_for_missing_id(self):
        result = db.update_post(99999, "T", "B" * 50,
                                [], "A", "C", "🍞", 1)
        self.assertFalse(result)

    def test_returns_true_on_success(self):
        post = self._make_post()
        result = db.update_post(
            post.post_id, "New Title Here",
            post.body, post.tags, post.author,
            post.category, post.icon, post.read_mins
        )
        self.assertTrue(result)


#  delete_post


class TestDeletePost(DatabaseTestCase):

    def test_post_removed_from_db(self):
        post = self._make_post()
        db.delete_post(post.post_id)
        self.assertIsNone(db.get_post_by_id(post.post_id))

    def test_returns_true_when_found(self):
        post = self._make_post()
        self.assertTrue(db.delete_post(post.post_id))

    def test_returns_false_when_not_found(self):
        self.assertFalse(db.delete_post(99999))

    def test_cascade_deletes_comments(self):
        post    = self._make_post()
        comment = db.create_comment(
            post.post_id, "Title", "Comment body text here."
        )
        db.delete_post(post.post_id)
        conn = sqlite3.connect(self.db_path)
        cur  = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM comments WHERE comment_id = ?",
            (comment.comment_id,)
        )
        count = cur.fetchone()[0]
        conn.close()
        self.assertEqual(count, 0)

    def test_cascade_deletes_post_tags(self):
        post    = self._make_post(tags=["cascade-test"])
        post_id = post.post_id
        db.delete_post(post_id)
        conn = sqlite3.connect(self.db_path)
        cur  = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM post_tags WHERE post_id = ?",
            (post_id,)
        )
        count = cur.fetchone()[0]
        conn.close()
        self.assertEqual(count, 0)

#  Comments


class TestComments(DatabaseTestCase):

    def test_create_comment_returns_comment_object(self):
        from modules.models import Comment
        post    = self._make_post()
        comment = db.create_comment(
            post.post_id, "Great post!", "Really helpful content."
        )
        self.assertIsInstance(comment, Comment)
        self.assertEqual(comment.post_id, post.post_id)
        self.assertEqual(comment.title, "Great post!")

    def test_get_comments_for_post_returns_list(self):
        post = self._make_post()
        db.create_comment(post.post_id, "First",  "First comment body here.")
        db.create_comment(post.post_id, "Second", "Second comment body here.")
        comments = db.get_comments_for_post(post.post_id)
        self.assertEqual(len(comments), 2)

    def test_get_comments_only_returns_for_that_post(self):
        p1 = self._make_post(title="Post A")
        p2 = self._make_post(title="Post B")
        db.create_comment(p1.post_id, "For P1", "Comment for post one body.")
        db.create_comment(p2.post_id, "For P2", "Comment for post two body.")
        self.assertEqual(len(db.get_comments_for_post(p1.post_id)), 1)
        self.assertEqual(len(db.get_comments_for_post(p2.post_id)), 1)

    def test_get_comments_empty_for_new_post(self):
        post = self._make_post()
        self.assertEqual(db.get_comments_for_post(post.post_id), [])

    def test_delete_comment(self):
        post    = self._make_post()
        comment = db.create_comment(
            post.post_id, "T", "Body text is long enough."
        )
        result  = db.delete_comment(comment.comment_id)
        self.assertTrue(result)
        self.assertEqual(db.get_comments_for_post(post.post_id), [])

    def test_delete_comment_not_found(self):
        self.assertFalse(db.delete_comment(99999))


#  Tags


class TestTags(DatabaseTestCase):

    def test_get_all_tags_returns_sorted_list(self):
        tags = db.get_all_tags()
        self.assertEqual(tags, sorted(tags))

    def test_get_all_tags_no_duplicates(self):
        tags = db.get_all_tags()
        self.assertEqual(len(tags), len(set(tags)))

    def test_get_posts_by_tag_returns_matching_posts(self):
        self._make_post(tags=["rye", "bread"])
        self._make_post(tags=["cakes"])
        rye_posts = db.get_posts_by_tag("rye")
        self.assertTrue(all("rye" in p.tags for p in rye_posts))

    def test_get_posts_by_tag_empty_for_unknown_tag(self):
        result = db.get_posts_by_tag("this-tag-does-not-exist")
        self.assertEqual(result, [])

    def test_new_tags_appear_in_get_all_tags(self):
        self._make_post(tags=["brand-new-tag-xyz"])
        tags = db.get_all_tags()
        self.assertIn("brand-new-tag-xyz", tags)


#  Search

class TestSearch(DatabaseTestCase):

    def test_search_by_title_keyword(self):
        self._make_post(title="Chocolate Chip Cookies Recipe")
        results = db.search_posts("Chocolate")
        titles  = [p.title for p in results]
        self.assertIn("Chocolate Chip Cookies Recipe", titles)

    def test_search_by_body_keyword(self):
        self._make_post(body="unique_search_keyword_xyz " * 5)
        results = db.search_posts("unique_search_keyword_xyz")
        self.assertGreater(len(results), 0)

    def test_search_no_match_returns_empty(self):
        results = db.search_posts("zzznomatchzzz")
        self.assertEqual(results, [])

    def test_search_case_insensitive(self):
        self._make_post(title="Lemon Drizzle Cake")
        lower = db.search_posts("lemon drizzle")
        upper = db.search_posts("LEMON DRIZZLE")
        self.assertEqual(len(lower), len(upper))


#  Stats


class TestStats(DatabaseTestCase):

    def test_returns_dict(self):
        stats = db.get_stats()
        self.assertIsInstance(stats, dict)

    def test_contains_expected_keys(self):
        stats = db.get_stats()
        for key in ["total_posts", "avg_read_mins",
                    "total_comments", "total_tags", "top_tag"]:
            self.assertIn(key, stats)

    def test_post_count_matches_get_all(self):
        stats = db.get_stats()
        posts = db.get_all_posts()
        self.assertEqual(stats["total_posts"], len(posts))

    def test_counts_increase_after_insert(self):
        before = db.get_stats()["total_posts"]
        self._make_post()
        after = db.get_stats()["total_posts"]
        self.assertEqual(after, before + 1)


#  SQL injection prevention


class TestSQLInjectionPrevention(DatabaseTestCase):

    def test_sql_injection_in_search(self):
        evil = "'; DROP TABLE posts; --"
        try:
            results = db.search_posts(evil)
            self.assertIsInstance(results, list)
        except Exception as e:
            self.fail(f"search_posts raised an exception: {e}")

    def test_sql_injection_in_post_title(self):
        evil  = "'); DROP TABLE posts; --"
        post  = self._make_post(title=evil)
        fetched = db.get_post_by_id(post.post_id)
        self.assertEqual(fetched.title, evil)

    def test_posts_table_still_exists_after_injection_attempt(self):
        db.search_posts("'; DROP TABLE posts; --")
        posts = db.get_all_posts()
        self.assertIsInstance(posts, list)


if __name__ == "__main__":
    unittest.main(verbosity=2)