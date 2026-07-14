"use strict";

// Side navigation bar
function toggleSidebar() {
  const sidebar = document.getElementById("side-nav");
  const main = document.getElementById("main");
  const navbar = document.getElementById("top-navbar");
  if (!sidebar || !main || !navbar) return;

  const isMobile = window.matchMedia("(max-width: 1150px)").matches;
  sidebar.classList.toggle("toggle-active");
  main.classList.toggle("toggle-active");
  navbar.classList.toggle("toggle-active");

  const isOpen = isMobile && sidebar.classList.contains("toggle-active");
  document.body.classList.toggle("sidebar-open", isOpen);
  document.querySelectorAll('[aria-controls="side-nav"]').forEach(function (button) {
    button.setAttribute("aria-expanded", String(isOpen));
  });

  const manageWrap = document.querySelector(".manage-wrap");
  if (manageWrap) {
    manageWrap.classList.toggle("toggle-active");
  }
}

function closeSidebar() {
  const sidebar = document.getElementById("side-nav");
  if (!sidebar || !window.matchMedia("(max-width: 1150px)").matches) return;

  sidebar.classList.remove("toggle-active");
  document.getElementById("main")?.classList.remove("toggle-active");
  document.getElementById("top-navbar")?.classList.remove("toggle-active");
  document.querySelector(".manage-wrap")?.classList.remove("toggle-active");
  document.body.classList.remove("sidebar-open");
  document.querySelectorAll('[aria-controls="side-nav"]').forEach(function (button) {
    button.setAttribute("aria-expanded", "false");
  });
}

// popup
var c = 0;
function pop() {
  if (c == 0) {
    document.getElementById("popup-box").style.display = "block";
    c = 1;
  } else {
    document.getElementById("popup-box").style.display = "none";
    c = 0;
  }
}

// Bootstrap-style validation for marked forms.
var forms = document.getElementsByClassName("needs-validation");
Array.prototype.filter.call(forms, function (form) {
  form.addEventListener(
    "submit",
    function (event) {
      if (form.checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add("was-validated");
    },
    false
  );
});

// extend and collapse
let collapsed = true;

function showCourses(btn) {
  var button = $(btn);

  if (collapsed) {
    button.html('Collapse <i class="fas fa-angle-up"></i>');
    $(".hide").css("max-height", "unset");
    $(".white-shadow").css({ background: "unset", "z-index": "0" });
  } else {
    button.html('Expand <i class="fas fa-angle-down"></i>');
    $(".hide").css("max-height", "150");
    $(".white-shadow").css({
      background: "linear-gradient(transparent 50%, rgba(255,255,255,.8) 80%)",
      "z-index": "2",
    });
  }
  collapsed = !collapsed;
}

document.addEventListener("DOMContentLoaded", function () {
  const languageSelect = document.getElementById("lang-select");
  if (languageSelect) {
    languageSelect.addEventListener("change", function () {
      document.getElementById("lang-form")?.submit();
    });
  }

  document.querySelectorAll("#side-nav a").forEach(function (link) {
    link.addEventListener("click", closeSidebar);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeSidebar();
  });

  let wasMobile = window.matchMedia("(max-width: 1150px)").matches;
  window.addEventListener("resize", function () {
    const isMobile = window.matchMedia("(max-width: 1150px)").matches;
    if (isMobile !== wasMobile) {
      document.getElementById("side-nav")?.classList.remove("toggle-active");
      document.getElementById("main")?.classList.remove("toggle-active");
      document.getElementById("top-navbar")?.classList.remove("toggle-active");
      document.querySelector(".manage-wrap")?.classList.remove("toggle-active");
      document.body.classList.remove("sidebar-open");
      wasMobile = isMobile;
    }
  });
});
