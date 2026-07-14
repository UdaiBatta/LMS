(function () {
  "use strict";

  const site = document.querySelector(".public-site");
  if (!site) return;

  const progress = document.querySelector(".public-scroll-progress span");
  const navLinks = Array.from(document.querySelectorAll(".public-nav-links a[href^='#']"));
  const sections = navLinks
    .map(function (link) {
      return document.querySelector(link.getAttribute("href"));
    })
    .filter(Boolean);

  function updateScrollState() {
    if (progress) {
      const scrollable = document.documentElement.scrollHeight - window.innerHeight;
      const amount = scrollable > 0 ? Math.min(window.scrollY / scrollable, 1) : 0;
      progress.style.transform = "scaleX(" + amount + ")";
    }

    let activeId = "";
    sections.forEach(function (section) {
      if (section.getBoundingClientRect().top <= 180) activeId = section.id;
    });
    navLinks.forEach(function (link) {
      const isActive = link.getAttribute("href") === "#" + activeId;
      link.classList.toggle("is-active", isActive);
      if (isActive) link.setAttribute("aria-current", "true");
      else link.removeAttribute("aria-current");
    });
  }

  let ticking = false;
  window.addEventListener(
    "scroll",
    function () {
      if (ticking) return;
      window.requestAnimationFrame(function () {
        updateScrollState();
        ticking = false;
      });
      ticking = true;
    },
    { passive: true }
  );
  updateScrollState();

  const filterButtons = Array.from(document.querySelectorAll("[data-role-filter]"));
  const workflowRows = Array.from(document.querySelectorAll(".public-workflow-row[data-roles]"));
  const lensStatus = document.getElementById("role-lens-status");
  function selectRole(role) {
    let selectedButton = null;
    filterButtons.forEach(function (button) {
      const selected = button.dataset.roleFilter === role;
      button.setAttribute("aria-pressed", String(selected));
      if (selected) selectedButton = button;
    });
    workflowRows.forEach(function (row) {
      const matches = role === "all" || row.dataset.roles.split(" ").includes(role);
      row.classList.toggle("is-dimmed", !matches);
      row.classList.toggle("is-focused", role !== "all" && matches);
    });
    if (lensStatus && selectedButton) lensStatus.textContent = selectedButton.dataset.status;
  }

  filterButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      selectRole(button.dataset.roleFilter);
    });
  });

  document.querySelectorAll("[data-role-jump]").forEach(function (button) {
    button.addEventListener("click", function () {
      selectRole(button.dataset.roleJump);
      const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      document.getElementById("workflow")?.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
    });
  });

  if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  document.documentElement.classList.add("public-motion-ready");
  const revealObserver = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-revealed");
        revealObserver.unobserve(entry.target);
      });
    },
    { threshold: 0.18 }
  );
  document.querySelectorAll("[data-reveal]").forEach(function (element) {
    revealObserver.observe(element);
  });
})();
