
function toOrigin(el) {
    var oId = el.id.replace("m","origin");
    var origin = document.getElementById(oId);
    if (origin === el.parentElement) return;
    origin.appendChild(el);
    el.classList.remove('incorrect');
    el.classList.remove('correct');
    el.classList.add("unmatched");
    checkCorrectness();
}

function toSchedule(el) {
    var oId = el.id.replace("m","match");
    var origin = document.getElementById(oId);
    if (origin === el.parentElement) return;
    origin.appendChild(el);
    el.classList.remove('incorrect');
    el.classList.remove('correct');
    el.classList.remove("unmatched");
    checkCorrectness();
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("Text", ev.target.id);
}


function drop(ev, el, limit) {
    if(el.children.length >= limit){
        if (el.children[0].classList.contains('incorrect'))
            toOrigin(el.children[0])
        else
            return;
    }
    var oId = el.id.replace("match","m");
    ev.preventDefault();
    var data = ev.dataTransfer.getData("Text");
    var child = document.getElementById(data);
    if(child.id == oId){
        child.classList.add("correct");
        child.classList.remove("incorrect");
    } else {
        child.classList.add("incorrect");
        child.classList.remove("correct");
    }
    child.classList.remove("unmatched")
    el.appendChild(child);
    checkCorrectness();
}

function redo() {
    Array.from(document.getElementsByClassName("trait")).forEach(function(item) {
        toOrigin(item);
    });
    Array.from(document.getElementsByClassName("trait")).forEach(function(item) {
        if(Math.random() > 0.5)
            toSchedule(item)
    });
    shuffle(document.getElementById("drags"));
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
    if(document.getElementsByClassName("unmatched").length < 1 && document.getElementsByClassName("incorrect").length == 0) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}