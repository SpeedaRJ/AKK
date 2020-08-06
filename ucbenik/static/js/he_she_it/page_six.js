var solutions = {
    "I am" : "Jaz sem",
    "You are" : "Ti si",
    "We are" : "Mi smo",
    "He is" : "On je",
    "She is" : "Ona je",
    "It is" : "Ono je",
    "They are" : "Oni so"
}

function redo(e) {
    let table = document.getElementById("help-table");
    table.innerHTML="";
    var ns = [];
    var adj = [];
    for(var i in solutions)
        adj.push([i]);
    for(i=0; i < 5; i++) {
        var n = Math.round(Math.random() * (adj.length-1));
        while(ns.includes(n)) 
            n = Math.round(Math.random() * (adj.length-1));
        ns.push(n);
        let word = adj[n];
        let html ="";
        if(Math.random()>0.5) {
            html =  '<div class="help row"><button class="col-lg-6 tip" disabled>'+
                    '<input class="textarea" size="5" onchange="solution(this,'+"'"+word+"'"+
                    ')"/></button><button class="col-lg-6 tip c2"><p>'+solutions[word]+
                    '</p></button></div>';
        } else {
            html =  '<div class="help row"><button class="col-lg-6 tip" disabled><p>'+word+
                    '</p></button><button class="col-lg-6 tip c2">'+
                    '<input class="textarea" size="5" onchange="solution(this,'+"'"+solutions[word]+"'"+
                    ')"/></button></div>';
        }
        
        table.innerHTML+=html;
    }
}

function solution(el,solution) {
    let parent = el.parentElement;
    if (el.value.replace("Vi ste", "Ti si").toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution+'\.*\!*$')) {
        parent.classList.remove("incorrect");
        parent.classList.add("correct");
    } else {
        parent.classList.add("incorrect");
        parent.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("tip")
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