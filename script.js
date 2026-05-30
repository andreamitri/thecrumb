// Set current year in footer
document.getElementById("yr").textContent = new Date().getFullYear();

// Toggle the full post text open/closed
function toggleFull(e, id) {
  e.preventDefault();
  const el = document.getElementById(id);
  const btn = document.getElementById("btn-" + id);
  const open = el.classList.toggle("open");
  btn.textContent = open ? "Collapse ↑" : "Read the full post ↓";
}

// Dynamically add a new comment to the list
function postComment(e) {
  e.preventDefault();

  const name = document.getElementById("cname").value.trim();
  const comment = document.getElementById("cbody").value.trim();
  const list = document.getElementById("comments-list");
  const confirm = document.getElementById("confirm");

  const today = new Date().toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
  const initial = name.charAt(0).toUpperCase();

  // Build the new comment element
  const item = document.createElement("div");
  item.className = "comment-item";
  item.style.cssText =
    "opacity:0; transform:translateY(12px); transition:opacity 0.4s, transform 0.4s;";
  item.innerHTML = `
    <div class="comment-header">
      <div class="c-avatar">${initial}</div>
      <span class="c-name">${name}</span>
      <span class="c-date">${today}</span>
    </div>
    <p class="c-body">${comment}</p>`;
  list.appendChild(item);

  // Animate the new comment in
  requestAnimationFrame(() =>
    requestAnimationFrame(() => {
      item.style.opacity = "1";
      item.style.transform = "translateY(0)";
    }),
  );

  // Show confirmation banner, then hide after 5s
  confirm.classList.add("show");
  e.target.reset();
  setTimeout(() => confirm.classList.remove("show"), 5000);
}
