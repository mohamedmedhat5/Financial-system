const table=$("#transactionsTable"),search=$("#transactionSearch"),type=$("#typeFilter"),category=$("#categoryFilter");
const applyTransactionFilters=()=>{const q=search.value.toLowerCase();$$("tbody tr",table).forEach(r=>{const okText=r.textContent.toLowerCase().includes(q),okType=type.value==="all"||r.dataset.type===type.value,okCat=category.value==="all"||r.dataset.category===category.value;r.hidden=!(okText&&okType&&okCat)})};
[search,type,category].forEach(el=>on(el,"input",applyTransactionFilters));
$$("th[data-sort]",table).forEach(th=>on(th,"click",()=>{const rows=$$("tbody tr",table).sort((a,b)=>a.children[th.cellIndex].textContent.localeCompare(b.children[th.cellIndex].textContent,undefined,{numeric:true}));rows.forEach(r=>table.tBodies[0].appendChild(r))}));
on($("#exportCsv"),"click",()=>downloadCsv("transactions.csv",$$("tr",table).map(r=>$$("th,td",r).slice(0,5).map(c=>c.textContent.trim()))));
