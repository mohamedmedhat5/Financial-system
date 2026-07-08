$$(".setting-row input,.setting-row select").forEach(el=>on(el,"change",()=>el.closest(".setting-card").classList.add("is-updated")));
