// 1. BLOG-LEVEL VARIABLES
const blogName    = "Crumb & Hearth";
const foundedYear = 2024;

// 2. POST DATA as an array of objects
const posts = [
  { title: "The Secret to a Perfect Sourdough Crust", author: "Clara Bennet",   category: "Breads",      mins: 7,  date: "May 2025", icon: "🍞" },
  { title: "Laminated Dough, Demystified",             author: "Clara Bennet",   category: "Pastries",    mins: 12, date: "May 20",   icon: "🥐" },
  { title: "Why Reverse Creaming Changes Everything",  author: "James Holloway", category: "Cakes",       mins: 8,  date: "May 17",   icon: "🍰" },
  { title: "No-Knead Focaccia for a Friday Night",     author: "Clara Bennet",   category: "Breads",      mins: 6,  date: "May 14",   icon: "🍞" },
  { title: "Understanding Baking Powder vs. Baking Soda", author: "James Holloway", category: "Techniques", mins: 5, date: "May 10", icon: "🧁" },
  { title: "One Bowl Brown Butter Chocolate Cake",     author: "Clara Bennet",   category: "Cakes",       mins: 10, date: "May 3",    icon: "🍫" },
];

// 3. ARITHMETIC
const totalPosts    = posts.length;                                       // count
const totalMins     = posts.reduce((sum, p) => sum + p.mins, 0);         // sum
const avgMins       = (totalMins / totalPosts).toFixed(1);               // average
const blogAge       = new Date().getFullYear() - foundedYear;            // subtraction
const longestPost   = posts.reduce((a, b) => a.mins > b.mins ? a : b);  // max

// 4. STRING OPERATIONS

document.getElementById("yr").textContent = new Date().getFullYear();

// Inject live stats banner into the page
const statsEl = document.getElementById("blog-stats");
if (statsEl) {
  // String concatenation to build each stat label
  statsEl.querySelector(".stat-posts").textContent  = totalPosts + " posts";
  statsEl.querySelector(".stat-mins").textContent   = totalMins + " min of reading";
  statsEl.querySelector(".stat-avg").textContent    = "~" + avgMins + " min avg";
  statsEl.querySelector(".stat-age").textContent    = blogAge + " year" + (blogAge !== 1 ? "s" : "") + " old";
  statsEl.querySelector(".stat-longest").textContent =
    "Longest: "" + longestPost.title + "" (" + longestPost.mins + " min)";
}

// 5. TOGGLE — expand/collapse a post excerpt
function toggleFull(e, id) {
  e.preventDefault();
  const el   = document.getElementById(id);
  const btn  = document.getElementById("btn-" + id);
  const open = el.classList.toggle("open");
  // Template literal for button label
  btn.textContent = open ? "Collapse ↑" : "Read the full post ↓";
}

// 6. COMMENT SUBMISSION 
function postComment(e) {
  e.preventDefault();

  // Variables to hold form field values
  const name    = document.getElementById("cname").value.trim();
  const comment = document.getElementById("cbody").value.trim();
  const list    = document.getElementById("comments-list");
  const confirm = document.getElementById("confirm");

  // String operation: format today's date
  const today   = new Date().toLocaleDateString("en-GB", {
    day: "numeric", month: "long", year: "numeric"
  });

  // String operation: get first letter (initial) via index
  const initial = name.charAt(0).toUpperCase();

  // Build the new comment element using template literals
  const item = document.createElement("div");
  item.className = "comment-item";
  item.style.cssText = "opacity:0; transform:translateY(12px); transition:opacity 0.4s, transform 0.4s;";
  item.innerHTML = `
    <div class="comment-header">
      <div class="c-avatar">${initial}</div>
      <span class="c-name">${name}</span>
      <span class="c-date">${today}</span>
    </div>
    <p class="c-body">${comment}</p>`;
  list.appendChild(item);

  // Animate in
  requestAnimationFrame(() => requestAnimationFrame(() => {
    item.style.opacity   = "1";
    item.style.transform = "translateY(0)";
  }));

  confirm.classList.add("show");
  e.target.reset();
  setTimeout(() => confirm.classList.remove("show"), 5000);
}
