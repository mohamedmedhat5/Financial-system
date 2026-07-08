$$(".notification-item button").forEach(btn=>on(btn,"click",()=>btn.closest(".notification-item").remove()));
