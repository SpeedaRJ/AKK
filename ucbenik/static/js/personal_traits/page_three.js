var adj = [
    "smart",
    "stupid",
    "good",
    "bad",
    "hard-working",
    "lazy",
    "generous",
    "selfish",
    "kind",
    "mean",
    "funny",
    "boring",
    "outgoing",
    "shy"
];
var pri = [
    "pameten",
    "neumen",
    "dober",
    "slab",
    "deloven",
    "len",
    "radodaren",
    "sebičen",
    "prijazen",
    "neprijazen",
    "zabaven",
    "dolgočasen",
    "družaben",
    "sramežljiv"
];

function redo() {
    let ns = [];
    let fillin = document.getElementById('fillin');
    fillin.innerHTML="";
    for(let i=0; i < 5; i++) {
        var n = Math.round(Math.random() * (adj.length-1));
        while(ns.includes(n)) 
            n = Math.round(Math.random() * (adj.length-1));
        ns.push(n);
        if(Math.random() > 0.5) {
            var html = '<div class="msg user fill">'+
            '<input class=textarea onchange="solution(this,'+"'"+adj[n]+"'"+')"/>'+
            '= <p>'+pri[n]+'</p> </div>';
        }
        else {
            var html = '<div class="msg user fill">'+
            '<p>'+adj[n]+'</p>='+ 
            '<input class=textarea onchange="solution(this,'+"'"+pri[n]+"'"+')"/></div>';
        }
        fillin.innerHTML+=html;
    }
}

function solution(el,solution) {
    let parent = el.parentElement;
    if (el.value.replace('velikodušen','radodaren').replace('nesramen','neprijazen') == solution) {
        parent.classList.remove("incorrect");
        parent.classList.add("correct");
    } else {
        parent.classList.add("incorrect");
        parent.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("fill")
    let counter = 0;
    for(let x in paras) {
        if(paras[x].classList !== undefined && paras[x].className.includes("correct") && !paras[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === 5)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}


$(function(){
    redo();
})