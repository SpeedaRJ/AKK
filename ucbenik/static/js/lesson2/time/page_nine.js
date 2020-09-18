
function toOrigin(el) {
    var oId = el.id.replace("m","drag");
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
    if(el.children.length > limit) {
        if(el.children[1].classList.contains("incorrect"))
            toOrigin(el.children[1])
        else
            return;
    }
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

function checkCorrectness() {
    let items = document.getElementsByClassName("trait")
    let counter = 0;
    for(let x = 0; x < items.length; x++) {
        if(items[x].classList !== undefined && items[x].className.includes("correct") && !items[x].className.includes("incorrect"))
            counter++;
    }
    if(counter == document.getElementsByClassName("trait").length/2) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}