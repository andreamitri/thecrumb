"""
tests/test_e2e.py
-----------------
End-to-end tests using Flask's built-in test client.
57 tests simulating real browser interactions.

Every test gets a fresh temporary database.
No real data is ever touched.

Run: python -m pytest tests/test_e2e.py -v
"""

import sys, os, sqlite3, tempfile, shutil, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import modules.database as db
from app import app


#  Base class — fresh database and test client per test


class E2ETestCase(unittest.TestCase):

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
        conn.isolation_level = None
        conn.executescript(sql)
        conn.close()

        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        db.DB_PATH = self._orig_db_path
        shutil.rmtree(self.tmp_dir)

    def _create_post(self, title="Test Post Title Here",
                     body="Body text " * 12,
                     tags="test, demo",
                     author="Tester",
                     category="Tests",
                     icon="🧪"):
        return self.client.post("/new", data={
            "title":    title,
            "body":     body,
            "tags":     tags,
            "author":   author,
            "category": category,
            "icon":     icon,
        }, follow_redirects=True)



#  Home page


class TestHomePage(E2ETestCase):

    def test_home_page_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_home_page_contains_blog_name(self):
        response = self.client.get("/")
        self.assertIn(b"Crumb", response.data)
        self.assertIn(b"Hearth", response.data)

    def test_home_page_lists_posts(self):
        response = self.client.get("/")
        self.assertIn(b"Sourdough", response.data)

    def test_home_page_has_new_post_link(self):
        response = self.client.get("/")
        self.assertIn(b"/new", response.data)

    def test_home_page_shows_stats(self):
        response = self.client.get("/")
        self.assertIn(b"posts", response.data)



#  Post detail page


class TestPostDetailPage(E2ETestCase):

    def test_post_page_returns_200(self):
        response = self.client.get("/post/1")
        self.assertEqual(response.status_code, 200)

    def test_post_page_shows_title(self):
        post     = db.get_post_by_id(1)
        response = self.client.get("/post/1")
        self.assertIn(post.title.encode(), response.data)

    def test_post_page_shows_author(self):
        post     = db.get_post_by_id(1)
        response = self.client.get("/post/1")
        self.assertIn(post.author.encode(), response.data)

    def test_post_page_shows_tags(self):
        post     = db.get_post_by_id(1)
        response = self.client.get("/post/1")
        for tag in post.tags:
            self.assertIn(tag.encode(), response.data)

    def test_post_page_shows_edit_link(self):
        response = self.client.get("/post/1")
        self.assertIn(b"/post/1/edit", response.data)

    def test_post_page_shows_comment_form(self):
        response = self.client.get("/post/1")
        self.assertIn(b"c_title", response.data)
        self.assertIn(b"c_body",  response.data)

    def test_missing_post_returns_404(self):
        response = self.client.get("/post/99999")
        self.assertEqual(response.status_code, 404)


#  Tag page


class TestTagPage(E2ETestCase):

    def test_tag_page_returns_200(self):
        response = self.client.get("/tag/bread")
        self.assertEqual(response.status_code, 200)

    def test_tag_page_shows_tag_name(self):
        response = self.client.get("/tag/bread")
        self.assertIn(b"bread", response.data)

    def test_tag_page_only_shows_tagged_posts(self):
        posts    = db.get_posts_by_tag("bread")
        response = self.client.get("/tag/bread")
        for post in posts:
            self.assertIn(post.title.encode(), response.data)

    def test_unknown_tag_returns_200(self):
        response = self.client.get("/tag/zzznotarealtag")
        self.assertEqual(response.status_code, 200)

    def test_tag_page_shows_tag_cloud(self):
        response = self.client.get("/tag/bread")
        self.assertIn(b"/tag/", response.data)


#  Search


class TestSearch(E2ETestCase):

    def test_search_returns_200(self):
        response = self.client.get("/search?q=sourdough")
        self.assertEqual(response.status_code, 200)

    def test_search_shows_matching_post(self):
        response = self.client.get("/search?q=sourdough")
        self.assertIn(b"Sourdough", response.data)

    def test_search_no_results(self):
        response = self.client.get("/search?q=zzznomatch")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"0 result", response.data)

    def test_search_reflects_query_in_page(self):
        response = self.client.get("/search?q=chocolate")
        self.assertIn(b"chocolate", response.data)

    def test_empty_search_returns_200(self):
        response = self.client.get("/search")
        self.assertEqual(response.status_code, 200)


#  Create post


class TestCreatePost(E2ETestCase):

    def test_new_post_form_loads(self):
        response = self.client.get("/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"title", response.data)

    def test_create_post_redirects_to_new_post(self):
        response = self._create_post(title="My Fresh Rye Loaf Recipe")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"My Fresh Rye Loaf Recipe", response.data)

    def test_created_post_appears_on_home_page(self):
        self._create_post(title="Unique Post Title XYZ123")
        response = self.client.get("/")
        self.assertIn(b"Unique Post Title XYZ123", response.data)

    def test_created_post_saved_to_database(self):
        self._create_post(title="Database Check Post ABC")
        titles = [p.title for p in db.get_all_posts()]
        self.assertIn("Database Check Post ABC", titles)

    def test_create_post_with_tags_saves_tags(self):
        self._create_post(title="Tagged Post Here", tags="rye, dense, nordic")
        posts = db.get_all_posts()
        post  = next(p for p in posts if p.title == "Tagged Post Here")
        self.assertIn("rye",    post.tags)
        self.assertIn("dense",  post.tags)
        self.assertIn("nordic", post.tags)

    def test_create_post_invalid_title_shows_error(self):
        response = self._create_post(title="Hi")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"5 characters", response.data)

    def test_create_post_invalid_body_shows_error(self):
        response = self._create_post(body="Too short.")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"50 characters", response.data)

    def test_create_post_invalid_does_not_save(self):
        before = len(db.get_all_posts())
        self._create_post(title="Hi", body="short")
        after  = len(db.get_all_posts())
        self.assertEqual(before, after)

    def test_create_post_preserves_input_on_error(self):
        response = self._create_post(title="Hi", body="short", author="Clara")
        self.assertIn(b"Clara", response.data)


#  Edit post


class TestEditPost(E2ETestCase):

    def test_edit_form_loads_with_existing_data(self):
        post     = db.get_post_by_id(1)
        response = self.client.get("/post/1/edit")
        self.assertEqual(response.status_code, 200)
        self.assertIn(post.title.encode(), response.data)

    def test_edit_post_saves_new_title(self):
        post     = db.get_post_by_id(1)
        response = self.client.post("/post/1/edit", data={
            "title":    "Updated Sourdough Guide",
            "body":     post.body,
            "tags":     ", ".join(post.tags),
            "author":   post.author,
            "category": post.category,
            "icon":     post.icon,
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Updated Sourdough Guide", response.data)

    def test_edit_post_persisted_to_database(self):
        post = db.get_post_by_id(1)
        self.client.post("/post/1/edit", data={
            "title":    "Persisted Update Title",
            "body":     post.body,
            "tags":     ", ".join(post.tags),
            "author":   post.author,
            "category": post.category,
            "icon":     post.icon,
        })
        updated = db.get_post_by_id(1)
        self.assertEqual(updated.title, "Persisted Update Title")

    def test_edit_post_invalid_title_shows_error(self):
        post     = db.get_post_by_id(1)
        response = self.client.post("/post/1/edit", data={
            "title":    "Hi",
            "body":     post.body,
            "tags":     ", ".join(post.tags),
            "author":   post.author,
            "category": post.category,
            "icon":     post.icon,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"5 characters", response.data)

    def test_edit_missing_post_returns_404(self):
        response = self.client.get("/post/99999/edit")
        self.assertEqual(response.status_code, 404)


#  Delete post


class TestDeletePost(E2ETestCase):

    def test_delete_post_redirects_to_home(self):
        response = self.client.post(
            "/post/1/delete", follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Crumb", response.data)

    def test_deleted_post_gone_from_database(self):
        self.client.post("/post/1/delete")
        self.assertIsNone(db.get_post_by_id(1))

    def test_deleted_post_returns_404(self):
        self.client.post("/post/1/delete")
        response = self.client.get("/post/1")
        self.assertEqual(response.status_code, 404)

    def test_deleted_post_not_on_home_page(self):
        post  = db.get_post_by_id(1)
        title = post.title
        self.client.post("/post/1/delete", follow_redirects=True)
        response = self.client.get("/")
        self.assertNotIn(title.encode(), response.data)


#  Add comment


class TestAddComment(E2ETestCase):

    def test_valid_comment_redirects_to_post(self):
        response = self.client.post("/post/1/comment", data={
            "c_title": "Brilliant tip!",
            "c_body":  "I tried the Dutch oven method and it worked perfectly.",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_valid_comment_appears_on_post_page(self):
        self.client.post("/post/1/comment", data={
            "c_title": "My Unique Comment Title XYZ",
            "c_body":  "This is the body of my unique test comment.",
        }, follow_redirects=True)
        response = self.client.get("/post/1")
        self.assertIn(b"My Unique Comment Title XYZ", response.data)

    def test_valid_comment_saved_to_database(self):
        self.client.post("/post/1/comment", data={
            "c_title": "Database Comment Test",
            "c_body":  "Checking this gets saved to the database correctly.",
        })
        comments = db.get_comments_for_post(1)
        titles   = [c.title for c in comments]
        self.assertIn("Database Comment Test", titles)

    def test_invalid_comment_title_shows_error(self):
        response = self.client.post("/post/1/comment", data={
            "c_title": "Hi",
            "c_body":  "This body is long enough to pass validation.",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"3 characters", response.data)

    def test_invalid_comment_body_shows_error(self):
        response = self.client.post("/post/1/comment", data={
            "c_title": "Valid Title Here",
            "c_body":  "short",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"10 characters", response.data)

    def test_invalid_comment_not_saved(self):
        before = len(db.get_comments_for_post(1))
        self.client.post("/post/1/comment", data={
            "c_title": "Hi",
            "c_body":  "short",
        })
        after = len(db.get_comments_for_post(1))
        self.assertEqual(before, after)

    def test_invalid_comment_preserves_input(self):
        response = self.client.post("/post/1/comment", data={
            "c_title": "Hi",
            "c_body":  "This body is long enough to pass validation checks.",
        })
        self.assertIn(b"Hi", response.data)

    def test_comment_on_missing_post_returns_404(self):
        response = self.client.post("/post/99999/comment", data={
            "c_title": "Valid Title Here",
            "c_body":  "This body is long enough to pass validation.",
        })
        self.assertEqual(response.status_code, 404)


#  Template inheritance


class TestTemplateInheritance(E2ETestCase):

    def _check_page(self, url):
        response = self.client.get(url)
        self.assertIn(b"Crumb", response.data,
                      msg=f"Header missing on {url}")
        self.assertIn(b"/tag/", response.data,
                      msg=f"Nav links missing on {url}")

    def test_home_has_base_layout(self):
        self._check_page("/")

    def test_post_has_base_layout(self):
        self._check_page("/post/1")

    def test_tag_has_base_layout(self):
        self._check_page("/tag/bread")

    def test_new_post_has_base_layout(self):
        self._check_page("/new")

    def test_search_has_base_layout(self):
        self._check_page("/search?q=bread")


#  Full user journeys


class TestFullUserJourneys(E2ETestCase):

    def test_create_post_then_find_it_by_tag(self):
        self._create_post(
            title="Spelt Flour Experiment",
            tags="spelt, ancient-grain"
        )
        response = self.client.get("/tag/spelt")
        self.assertIn(b"Spelt Flour Experiment", response.data)

    def test_create_post_then_search_for_it(self):
        self._create_post(title="Kamut Porridge Bread Loaf")
        response = self.client.get("/search?q=Kamut")
        self.assertIn(b"Kamut", response.data)

    def test_create_post_add_comment_then_view(self):
        self._create_post(title="Einkorn Flatbread Guide")
        posts   = db.get_all_posts()
        post    = next(p for p in posts if p.title == "Einkorn Flatbread Guide")
        post_id = post.post_id

        self.client.post(f"/post/{post_id}/comment", data={
            "c_title": "Made this last night",
            "c_body":  "Followed the recipe exactly and it turned out perfectly.",
        })

        response = self.client.get(f"/post/{post_id}")
        self.assertIn(b"Made this last night", response.data)

    def test_create_then_edit_then_delete_post(self):
        self._create_post(title="Temporary Test Post")
        posts   = db.get_all_posts()
        post    = next(p for p in posts if p.title == "Temporary Test Post")
        post_id = post.post_id

        self.client.post(f"/post/{post_id}/edit", data={
            "title":    "Edited Temporary Post",
            "body":     post.body,
            "tags":     ", ".join(post.tags),
            "author":   post.author,
            "category": post.category,
            "icon":     post.icon,
        })
        updated = db.get_post_by_id(post_id)
        self.assertEqual(updated.title, "Edited Temporary Post")

        self.client.post(f"/post/{post_id}/delete")
        self.assertIsNone(db.get_post_by_id(post_id))


if __name__ == "__main__":
    unittest.main(verbosity=2)