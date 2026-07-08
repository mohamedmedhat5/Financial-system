on($("#reportCsv"),"click",()=>downloadCsv("financial-report.csv",$$("table tr").map(r=>$$("th,td",r).map(c=>c.textContent.trim()))));
