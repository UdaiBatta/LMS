(function () {
  "use strict";

  document.querySelectorAll("[data-form-progress]").forEach(function (form) {
    const fields = Array.from(form.querySelectorAll("[required]")).filter(function (field) {
      return field.type !== "hidden";
    });
    const bar = form.querySelector("[data-progress-bar]");
    const label = form.querySelector("[data-progress-label]");

    function hasValue(field) {
      if (field.type === "checkbox" || field.type === "radio") {
        return field.checked;
      }
      return String(field.value || "").trim() !== "";
    }

    function updateProgress() {
      const completed = fields.filter(hasValue).length;
      const percentage = fields.length ? Math.round((completed / fields.length) * 100) : 100;
      if (bar) bar.style.width = percentage + "%";
      if (label) label.textContent = percentage + "%";
    }

    form.addEventListener("input", updateProgress);
    form.addEventListener("change", updateProgress);
    updateProgress();
  });

  document.querySelectorAll("[data-character-output-for]").forEach(function (output) {
    const field = document.getElementById(output.dataset.characterOutputFor);
    if (!field) return;
    function updateCount() {
      output.textContent = field.value.length + " " + (output.dataset.characterLabel || "characters");
    }
    field.addEventListener("input", updateCount);
    updateCount();
  });
})();
