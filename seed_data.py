import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from modules.models  import BlogPost, Comment
from modules.storage import save_posts, save_comments

posts = [
    BlogPost(1, "The Secret to a Perfect Sourdough Crust", "2025-05-22",
        "After two years and more failed loaves than I care to admit, I finally cracked it. The answer is not in the recipe — it is in the steam.\n\nThe oven spring happens only when the surface stays moist enough to keep expanding. Use a Dutch oven: the lid traps moisture. Remove it for the final 20 minutes to brown and blister.\n\nScore your loaf at a 45-degree angle. Bake at 250C covered, then 220C uncovered. Let it cool fully before slicing.",
        ["sourdough","bread","technique","crust","steam"], "Clara Bennet", "Breads", "🍞", 7),

    BlogPost(2, "Laminated Dough, Demystified", "2025-05-20",
        "Croissants seem impossibly technical. But once you understand what lamination is doing, they become approachable.\n\nLamination means folding layers of butter into dough repeatedly. The butter must stay cold and distinct. Work in a cool kitchen, chill everything, and rest in the fridge between turns.\n\nThree double turns gives you 729 distinct layers.",
        ["pastries","croissants","lamination","technique","butter"], "Clara Bennet", "Pastries", "🥐", 12),

    BlogPost(3, "Why Reverse Creaming Changes Everything", "2025-05-17",
        "The classic cream butter and sugar first method is not the only way. Adding fat to flour before liquid produces a more tender crumb.\n\nReverse creaming coats the flour particles in fat first, limiting gluten development. Less gluten means a softer texture.\n\nTry it once on a vanilla cake and you will not go back.",
        ["cakes","technique","creaming","texture","baking-science"], "James Holloway", "Cakes", "🍰", 8),

    BlogPost(4, "No-Knead Focaccia for a Friday Night", "2025-05-14",
        "You do not need fancy equipment or any plan made before 4pm.\n\nCombine flour, water, yeast, salt and olive oil. Stir until shaggy. Refrigerate overnight. Tip into an oiled tin, dimple aggressively, scatter salt and rosemary, bake at 220C.\n\nEat the same day, torn rather than sliced.",
        ["bread","focaccia","no-knead","olive-oil","easy"], "Clara Bennet", "Breads", "🍞", 6),

    BlogPost(5, "Understanding Baking Powder vs Baking Soda", "2025-05-10",
        "Recipes mix them, swap them, or use both. Here is the actual chemistry.\n\nBaking soda is a pure base. It reacts immediately with acid to release CO2. Batters made with soda must go straight into the oven.\n\nBaking powder is soda pre-mixed with a dry acid. It is double-acting. Soda is roughly 3 to 4 times stronger.",
        ["technique","baking-science","chemistry","leavening"], "James Holloway", "Techniques", "🧁", 5),

    BlogPost(6, "The Butter Tart Debate: Runny or Firm?", "2025-05-07",
        "A purely personal, entirely biased case for the runny filling.\n\nMelt butter with brown sugar, whisk in eggs and golden syrup, fill short-pastry shells two thirds full.\n\nBake at 200C for 15 to 17 minutes. The filling should be puffed and barely set.",
        ["pastries","butter-tart","canadian","custard","short-pastry"], "Priya Sen", "Pastries", "🥧", 7),

    BlogPost(7, "One Bowl Brown Butter Chocolate Cake", "2025-05-03",
        "Brown butter adds a hazelnut depth that no extract can replicate.\n\nBrown 150g butter until the solids turn amber. Cool slightly, then whisk in sugar, eggs, flour, cocoa, baking powder, salt and buttermilk.\n\nBake at 175C for 30 to 35 minutes. Finish with equal parts cream and dark chocolate.",
        ["cakes","chocolate","brown-butter","one-bowl","easy"], "Clara Bennet", "Cakes", "🍫", 10),

    BlogPost(8, "Choux Pastry: What Nobody Tells You", "2025-04-28",
        "Choux is cooked twice: on the hob, then in the oven.\n\nBoil water with butter, tip in flour all at once and beat until the dough leaves the pan. Cook one more minute to dry it out — most recipes skip this step.\n\nBeat in eggs one at a time. Bake at 200C for 25 minutes without opening the oven.",
        ["pastries","choux","technique","eclairs","profiteroles"], "James Holloway", "Pastries", "🥐", 9),

    BlogPost(9, "The Case for Cold-Fermented Pizza Dough", "2025-04-21",
        "Most pizza dough recipes say rest for one hour. They are leaving flavour on the table.\n\nCold fermentation over 48 to 72 hours develops acids and esters a quick rise never produces.\n\nUse 00 flour, 3g yeast per 500g flour, refrigerate 48 to 72 hours, bake on a preheated steel at 280C.",
        ["bread","pizza","fermentation","cold-proof","technique"], "Priya Sen", "Breads", "🍕", 8),

    BlogPost(10, "Tarte Tatin: A Controlled Accident", "2025-04-15",
        "The tarte Tatin was allegedly invented by accident — an apple tart baked upside down and rescued by flipping.\n\nCaramelise apples directly in the pan, top with pastry, bake, then invert. Cook the caramel to deep amber before adding the apples.\n\nRest five minutes before inverting. Serve warm with creme fraiche.",
        ["pastries","french","tarte-tatin","apples","caramel"], "Clara Bennet", "Pastries", "🥧", 8),

    BlogPost(11, "Rye Bread: Dark, Dense, and Worth It", "2025-04-08",
        "Rye bread intimidates beginners because it behaves nothing like wheat bread.\n\nRye contains less gluten-forming protein and more pentosans that create a gel-like structure. This is why rye doughs are baked in tins rather than shaped freeform.\n\nCool completely overnight before slicing.",
        ["bread","rye","sourdough","dense","technique"], "James Holloway", "Breads", "🍞", 9),
]

comments = [
    Comment(1, 1, "Game changer!", "The Dutch oven tip changed my sourdough life completely.", "2025-05-24"),
    Comment(2, 7, "Espresso powder tip", "Added espresso powder to the chocolate cake and it got even better.", "2025-05-05"),
    Comment(3, 5, "Finally clarity", "Finally someone explains baking powder vs soda clearly.", "2025-05-12"),
    Comment(4, 4, "Overnight proof", "Left mine for 18 hours — best focaccia I have ever made.", "2025-05-16"),
    Comment(5, 2, "Butter temperature", "My butter kept shattering. Realised I was using it straight from the fridge.", "2025-05-21"),
    Comment(6, 9, "72-hour pizza", "The cold ferment pizza dough tasted like a restaurant pizza.", "2025-04-25"),
    Comment(7, 10, "Tarte tatin success", "Finally did it without the caramel burning. Three attempts but worth it.", "2025-04-18"),
    Comment(8, 1, "Steam timing question", "How long exactly should I keep the lid on? My oven runs hot.", "2025-05-23"),
]

posts.sort(key=lambda p: p.date, reverse=True)
save_posts(posts)
save_comments(comments)
print(f"Saved {len(posts)} posts and {len(comments)} comments.")