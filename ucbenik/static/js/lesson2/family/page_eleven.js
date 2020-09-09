function toOrigin(el) {
    var origin1 = document.getElementById('origin');
    var origin2 = document.getElementById('origin2');
    if (origin1 === el.parentElement || origin2 === el.parentElement) return;
    if (origin1.children.length < 4)
        origin1.appendChild(el);
    else
        origin2.appendChild(el);
    el.classList.remove('incorrect');
    el.classList.remove('correct');
    checkCorrectness();
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev, el) {
    ev.dataTransfer.setData("Text", el.id);
}


function drop(ev, el, limit) {
    if(el.children.length > limit)
        return;
    var oId = el.id.replace("match","m").replace("m06","m08");
    ev.preventDefault();
    var data = ev.dataTransfer.getData("Text");
    var child = document.getElementById(data);
    if(child.id.replace("m06","m08") == oId){
        child.classList.add("correct");
        child.classList.remove("incorrect");
    } else {
        child.classList.add("incorrect");
        child.classList.remove("correct");
    }
    el.appendChild(child);
    checkCorrectness();
}

function redo() {
    Array.from(document.getElementsByClassName("draggable-portrait")).forEach(function(item) {
        toOrigin(item);
    });
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
    if(counter === 10) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}