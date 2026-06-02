-- schema.sql
-- Crumb & Hearth — SQLite database schema
--
-- Run via Python:
--   python migrate.py
-- Or directly in SQLite:
--   sqlite3 data/blog.db < schema.sql

-- Drop tables in reverse dependency order (safe to re-run)
DROP TABLE IF EXISTS post_tags;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS posts;

-- Posts table
CREATE TABLE posts (
    post_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT    NOT NULL,
    date       TEXT    NOT NULL,
    body       TEXT    NOT NULL,
    author     TEXT    NOT NULL DEFAULT 'Unknown',
    category   TEXT    NOT NULL DEFAULT '',
    icon       TEXT    NOT NULL DEFAULT '🍞',
    read_mins  INTEGER NOT NULL DEFAULT 5,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Tags table (each tag stored once)
CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT    NOT NULL UNIQUE
);

-- post_tags join table (many posts can have many tags)
CREATE TABLE post_tags (
    post_id INTEGER NOT NULL,
    tag_id  INTEGER NOT NULL,
    PRIMARY KEY (post_id, tag_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id)  REFERENCES tags(tag_id)   ON DELETE CASCADE
);

-- Comments table
CREATE TABLE comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id    INTEGER NOT NULL,
    title      TEXT    NOT NULL,
    body       TEXT    NOT NULL,
    date       TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);

-- Indexes to speed up common queries
CREATE INDEX idx_posts_date       ON posts(date DESC);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_post_tags_post   ON post_tags(post_id);
CREATE INDEX idx_post_tags_tag    ON post_tags(tag_id);

-- Example posts
INSERT INTO posts (title, date, body, author, category, icon, read_mins) VALUES
(
    'The Secret to a Perfect Sourdough Crust',
    '2025-05-22',
    'After two years and more failed loaves than I care to admit, I finally cracked it. The answer isn''t in the recipe — it''s in the steam.

The oven spring happens only when the surface stays moist enough to keep expanding. Use a Dutch oven: the lid traps moisture. Remove it for the final twenty minutes to brown and blister.

Score your loaf at a 45-degree angle. Bake at 250C covered for 20 minutes, then 220C uncovered for 20 more. Let it cool fully before slicing.',
    'Clara Bennet', 'Breads', '🍞', 7
),
(
    'Laminated Dough, Demystified',
    '2025-05-20',
    'Croissants seem impossibly technical. But once you understand what lamination is doing, they become approachable.

Lamination means folding layers of butter into dough repeatedly. The butter must stay cold and distinct. Work in a cool kitchen, chill everything, and rest in the fridge between turns.

Three double turns gives you 729 distinct layers.',
    'Clara Bennet', 'Pastries', '🥐', 12
),
(
    'Why Reverse Creaming Changes Everything',
    '2025-05-17',
    'The classic cream butter and sugar first method is not the only way. Adding fat to flour before liquid produces a more tender crumb.

Reverse creaming coats the flour particles in fat first, limiting gluten development. Less gluten means a softer, more velvety texture.

Try it once on a vanilla cake and you will not go back.',
    'James Holloway', 'Cakes', '🍰', 8
),
(
    'No-Knead Focaccia for a Friday Night',
    '2025-05-14',
    'You do not need fancy equipment or any plan made before 4pm.

Combine flour, water, yeast, salt and olive oil. Stir until shaggy. Refrigerate overnight. Tip into an oiled tin, dimple aggressively, scatter salt and rosemary, bake at 220C.

Eat the same day, torn rather than sliced.',
    'Clara Bennet', 'Breads', '🍞', 6
),
(
    'Understanding Baking Powder vs Baking Soda',
    '2025-05-10',
    'Recipes mix them, swap them, or use both. Here is the actual chemistry.

Baking soda is a pure base. It reacts immediately with acid to release CO2. Batters made with soda must go straight into the oven.

Baking powder is soda pre-mixed with a dry acid. It is double-acting: gas when wet, more gas when heated. Soda is roughly 3 to 4 times stronger.',
    'James Holloway', 'Techniques', '🧁', 5
),
(
    'The Butter Tart Debate: Runny or Firm?',
    '2025-05-07',
    'A purely personal, entirely biased case for the runny filling.

Melt butter with brown sugar, whisk in eggs and golden syrup, fill short-pastry shells two thirds full.

Bake at 200C for 15 to 17 minutes. The filling should be puffed and barely set.',
    'Priya Sen', 'Pastries', '🥧', 7
),
(
    'One Bowl Brown Butter Chocolate Cake',
    '2025-05-03',
    'Brown butter adds a hazelnut depth that no extract can replicate.

Brown 150g butter until the solids turn amber. Cool slightly, then whisk in sugar, eggs, flour, cocoa, baking powder, salt and buttermilk.

Bake at 175C for 30 to 35 minutes. Finish with equal parts cream and dark chocolate.',
    'Clara Bennet', 'Cakes', '🍫', 10
),
(
    'Choux Pastry: What Nobody Tells You',
    '2025-04-28',
    'Choux is cooked twice: on the hob, then in the oven.

Boil water with butter, tip in flour all at once and beat until the dough leaves the pan. Cook one more minute to dry it out — most recipes skip this step.

Beat in eggs one at a time. Bake at 200C for 25 minutes without opening the oven.',
    'James Holloway', 'Pastries', '🥐', 9
),
(
    'The Case for Cold-Fermented Pizza Dough',
    '2025-04-21',
    'Most pizza dough recipes say rest for one hour. They are leaving flavour on the table.

Cold fermentation over 48 to 72 hours develops acids and esters a quick rise never produces.

Use 00 flour, 3g yeast per 500g flour, refrigerate 48 to 72 hours, bake on a preheated steel at 280C.',
    'Priya Sen', 'Breads', '🍕', 8
),
(
    'Tarte Tatin: A Controlled Accident',
    '2025-04-15',
    'The tarte Tatin was allegedly invented by accident — an apple tart baked upside down and rescued by flipping.

Caramelise apples directly in the pan, top with pastry, bake, then invert. Cook the caramel to deep amber before adding the apples.

Rest five minutes before inverting. Serve warm with creme fraiche.',
    'Clara Bennet', 'Pastries', '🥧', 8
),
(
    'Rye Bread: Dark, Dense, and Worth It',
    '2025-04-08',
    'Rye bread intimidates beginners because it behaves nothing like wheat bread.

Rye contains less gluten-forming protein and more pentosans that create a gel-like structure. This is why rye doughs are baked in tins rather than shaped freeform.

Cool completely overnight before slicing.',
    'James Holloway', 'Breads', '🍞', 9
);

-- Tags
INSERT INTO tags (name) VALUES
('sourdough'), ('bread'), ('technique'), ('crust'), ('steam'),
('pastries'), ('croissants'), ('lamination'), ('butter'),
('cakes'), ('creaming'), ('texture'), ('baking-science'),
('focaccia'), ('no-knead'), ('olive-oil'), ('easy'),
('chemistry'), ('leavening'), ('butter-tart'), ('canadian'),
('custard'), ('short-pastry'), ('chocolate'), ('brown-butter'),
('one-bowl'), ('choux'), ('eclairs'), ('profiteroles'),
('pizza'), ('fermentation'), ('cold-proof'), ('french'),
('tarte-tatin'), ('apples'), ('caramel'), ('rye'), ('dense');

-- Link posts to tags
INSERT INTO post_tags (post_id, tag_id)
SELECT 1, tag_id FROM tags WHERE name IN
    ('sourdough', 'bread', 'technique', 'crust', 'steam');

INSERT INTO post_tags (post_id, tag_id)
SELECT 2, tag_id FROM tags WHERE name IN
    ('pastries', 'croissants', 'lamination', 'technique', 'butter');

INSERT INTO post_tags (post_id, tag_id)
SELECT 3, tag_id FROM tags WHERE name IN
    ('cakes', 'technique', 'creaming', 'texture', 'baking-science');

INSERT INTO post_tags (post_id, tag_id)
SELECT 4, tag_id FROM tags WHERE name IN
    ('bread', 'focaccia', 'no-knead', 'olive-oil', 'easy');

INSERT INTO post_tags (post_id, tag_id)
SELECT 5, tag_id FROM tags WHERE name IN
    ('technique', 'baking-science', 'chemistry', 'leavening');

INSERT INTO post_tags (post_id, tag_id)
SELECT 6, tag_id FROM tags WHERE name IN
    ('pastries', 'butter-tart', 'canadian', 'custard', 'short-pastry');

INSERT INTO post_tags (post_id, tag_id)
SELECT 7, tag_id FROM tags WHERE name IN
    ('cakes', 'chocolate', 'brown-butter', 'one-bowl', 'easy');

INSERT INTO post_tags (post_id, tag_id)
SELECT 8, tag_id FROM tags WHERE name IN
    ('pastries', 'choux', 'technique', 'eclairs', 'profiteroles');

INSERT INTO post_tags (post_id, tag_id)
SELECT 9, tag_id FROM tags WHERE name IN
    ('bread', 'pizza', 'fermentation', 'cold-proof', 'technique');

INSERT INTO post_tags (post_id, tag_id)
SELECT 10, tag_id FROM tags WHERE name IN
    ('pastries', 'french', 'tarte-tatin', 'apples', 'caramel');

INSERT INTO post_tags (post_id, tag_id)
SELECT 11, tag_id FROM tags WHERE name IN
    ('bread', 'rye', 'sourdough', 'dense', 'technique');

-- Comments
INSERT INTO comments (post_id, title, body, date) VALUES
(1, 'Game changer!',
 'The Dutch oven tip changed my sourdough life. Tried the lid method last weekend — incredible difference.',
 '2025-05-24'),
(1, 'Steam timing question',
 'How long exactly should I keep the lid on? My oven runs hot.',
 '2025-05-23'),
(7, 'Espresso powder tip',
 'Added a pinch of espresso powder and it got even better.',
 '2025-05-05'),
(5, 'Finally some clarity',
 'Finally someone explains baking powder vs soda clearly.',
 '2025-05-12'),
(4, 'Overnight proof',
 'Left mine in the fridge for 18 hours — best focaccia I have ever made.',
 '2025-05-16');