# 1. SIMPLE VARIABLES 
blog_name   = "Crumb & Hearth"
blog_tagline = "Recipes, techniques & the joy of home baking"
founded_year = 2024
current_year = 2025

# 2. A SINGLE POST AS VARIABLES 
post_title      = "The Secret to a Perfect Sourdough Crust"
post_author     = "Clara Bennet"
post_category   = "Breads"
post_read_mins  = 7
post_hydration  = 75          # percent
post_total_hours = 4
post_difficulty = "Medium"
post_tags       = ["sourdough", "crust", "steam", "dutch-oven", "technique"]

# 3. STRING OPERATIONS — concatenation & formatting ────────

byline = post_author + " · " + str(post_read_mins) + " min read"
print("Byline:", byline)

page_title = f"<title>{post_title} — {blog_name}</title>"
print("Page title tag:", page_title)

tags_string = ", ".join(f"#{t}" for t in post_tags)
print("Tags:", tags_string)

slug = post_title.lower().replace(" ", "-").replace(",", "")
print("URL slug:", slug)

# 4. ARITHMETIC — statistics & insights
total_posts   = 6
total_minutes = 12 + 8 + 6 + 5 + 7 + 10   # per post read times
avg_read_time = total_minutes / total_posts

# Years since founding
blog_age_years = current_year - founded_year

print(f"\n── Blog Stats ──────────────────────────")
print(f"Total posts      : {total_posts}")
print(f"Total read time  : {total_minutes} minutes")
print(f"Average read time: {avg_read_time:.1f} minutes")
print(f"Blog age         : {blog_age_years} year(s)")
print(f"Hydration target : {post_hydration}%")
print(f"Bake window      : {post_total_hours * 60} minutes total")

# 5. LIST OF ALL POSTS AS DICTS 
posts = [
    {
        "title":    "The Secret to a Perfect Sourdough Crust",
        "author":   "Clara Bennet",
        "category": "Breads",
        "mins":     7,
        "date":     "May 2025",
        "icon":     "🍞",
    },
    {
        "title":    "Laminated Dough, Demystified",
        "author":   "Clara Bennet",
        "category": "Pastries",
        "mins":     12,
        "date":     "May 20",
        "icon":     "🥐",
    },
    {
        "title":    "Why Reverse Creaming Changes Everything",
        "author":   "James Holloway",
        "category": "Cakes",
        "mins":     8,
        "date":     "May 17",
        "icon":     "🍰",
    },
    {
        "title":    "No-Knead Focaccia for a Friday Night",
        "author":   "Clara Bennet",
        "category": "Breads",
        "mins":     6,
        "date":     "May 14",
        "icon":     "🍞",
    },
    {
        "title":    "Understanding Baking Powder vs. Baking Soda",
        "author":   "James Holloway",
        "category": "Techniques",
        "mins":     5,
        "date":     "May 10",
        "icon":     "🧁",
    },
    {
        "title":    "One Bowl Brown Butter Chocolate Cake",
        "author":   "Clara Bennet",
        "category": "Cakes",
        "mins":     10,
        "date":     "May 3",
        "icon":     "🍫",
    },
]

# 6. OPERATIONS ON THE LIST 
author_counts = {}
for post in posts:
    author = post["author"]
    author_counts[author] = author_counts.get(author, 0) + 1

print(f"\n── Posts per Author ────────────────────")
for author, count in author_counts.items():
    print(f"  {author}: {count} post(s)")


longest = max(posts, key=lambda p: p["mins"])
print(f"\n── Longest Post ────────────────────────")
print(f"  \"{longest['title']}\" by {longest['author']} ({longest['mins']} min)")


print(f"\n── All Posts Summary ───────────────────")
for i, post in enumerate(posts, start=1):
    summary = (
        str(i) + ". "
        + post["icon"] + "  "
        + "[" + post["category"] + "]  "
        + post["title"]
        + "  —  " + post["author"]
        + " (" + str(post["mins"]) + " min)"
    )
    print(summary)

# 7. BAKER'S TIPS AS A LIST 
tips = [
    "Weigh everything — volume measurements vary by up to 30g.",
    "Egg and butter should be room temperature unless specified.",
    "Ovens lie — invest in an oven thermometer.",
    "Resting dough is not optional — gluten needs time to relax.",
]

print(f"\n── Baker's Tips ({len(tips)} total) ──────────────")
for num, tip in enumerate(tips, start=1):
    
    label = str(num).zfill(2)
    print(f"  {label}. {tip}")

print("\nDone. All variables, operations, and list processing complete.")