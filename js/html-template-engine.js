document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[require-file]").forEach(async el => {
    const file = el.getAttribute("require-file");
    try {
      const res = await fetch(file);
      const html = await res.text();
      el.outerHTML = html;
    } catch (err) {
      console.error(`❌ Error cargando ${file}:`, err);
    }
  });
});
