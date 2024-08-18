document.addEventListener("DOMContentLoaded", function() {
  var badge = document.getElementById("badge");
  if (badge.innerText === "0") {
    badge.style.display = "none";
  }
});