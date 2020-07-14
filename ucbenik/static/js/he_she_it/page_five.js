var solutions = {
    "Jaz":"I",
    "Ti":"You(ed.)",
    "Vi":"You(mn.)",
    "On":"He",
    "Ona":"She",
    "Ono":"It",
    "Oni":"They",
    "Mi":"We",
}
function toOrigin(el) {
    var oId = el.id.replace("m","match");
    var origin = document.getElementById(oId);
    if (origin === el.parentElement) return;
    origin.appendChild(el);
    el.classList.remove('incorrect');
    el.classList.remove('correct');
    checkCorrectness();
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("Text", ev.target.id);
}


function drop(ev, el, limit) {
    if(el.children.length > limit)
        return;
    var oId = el.id.replace("m","match");
    var origin = document.getElementById(oId);
    ev.preventDefault();
    var data = ev.dataTransfer.getData("Text");
    var child = document.getElementById(data);
    if(solutions[child.innerText] == el.children[0].innerText || solutions[el.children[0].innerText] == child.innerText){
        child.classList.add("correct");
        child.classList.remove("incorrect")
    } else {
        child.classList.add("incorrect");
        child.classList.remove("correct")
    }
    el.appendChild(child);
    checkCorrectness();
}

function redo() {
    Array.from(document.getElementsByClassName("trait")).forEach(function(item) {
        toOrigin(item);
    });
    shuffle(document.getElementById("drag1"));
    shuffle(document.getElementById("drag2"));
}



$(function(){
    redo();
})

function shuffle(el) {
    if(el.children == 0) return;
    for (var i = el.children.length; i >= 0; i--) {
        el.appendChild(el.children[Math.random() * i | 0]);
    }
}

function checkCorrectness() {
    let items = document.getElementsByClassName("trait")
    let counter = 0;
    for(let x = 0; x < items.length; x++) {
        if(items[x].classList !== undefined && items[x].className.includes("correct") && !items[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === 8) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}