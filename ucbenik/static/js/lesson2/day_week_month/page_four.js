
function toOrigin(el) {
    console.log(el);
    var oId = el.id.replace("m","match");
    console.log(oId);
    var origin = document.getElementById(oId);
    if (origin === el.parentElement) return;
    console.log(origin);
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
    var oId = el.id.replace("match","m");
    ev.preventDefault();
    var data = ev.dataTransfer.getData("Text");
    var child = document.getElementById(data);
    if(child.id == oId){
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
        if(item.classList.contains("correct") || item.classList.contains("incorrect"))
            toOrigin(item);
    });
    shuffle(document.getElementById("drag1"));
    shuffle(document.getElementById("drag2"));
    try {
        shuffle(document.getElementById("drag3"));
        shuffle(document.getElementById("drag4"));
    } catch(e) {}
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
    if(counter === document.getElementsByClassName("trait").length/2) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}