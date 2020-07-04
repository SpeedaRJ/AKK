function toOrigin(el) {
    var origin = document.getElementById('drag-origin');
    if (origin === el.parentElement) return;
    origin.appendChild(el);
    el.classList.remove('connected');
    el.style="";
    el.children[0].classList.remove('incorrect');
    el.children[0].classList.remove('correct');
    checkCorrectness();
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("Text", ev.target.id);
}

var last = 1;

function drop(ev, el, limit) {
    if (el.children.length > limit) {
        try {
            children = el.children;
            for(var i = 0; i < children.length; i++) {
                if(children[i].classList !== undefined && children[i].className.includes("incorrect")) {
                    toOrigin1(children[i]);
                    break;
                }
            }
            if(i === children.length && i > 1)
                return;
        } catch {
            return;
        }
    }
    var origin = document.getElementById('drag-origin');

    ev.preventDefault();
    var data = ev.dataTransfer.getData("Text");
    correct = data.search(el.id.replace("0","")) > -1;
    var child = document.getElementById(data);
    if (correct) {
        child.children[0].classList.add('correct');
        last=parseInt(child.id[child.id.length-1]);
        child.children[0].classList.remove('incorrect');
    } else {
        child.children[0].classList.add('incorrect');
        child.children[0].classList.remove('correct');
    }
    el.classList.add('full');
    document.getElementById('placeholder').remove();
    el.appendChild(child);
    let children = el.children
    for(var i = 0; i < children.length; i++) {
        children[i].classList.add("connected");
        children[i].style.marginLeft=(6*i+2)+"vh";
    }
    children[0].style.marginTop="2vh";
    // add placeholder
    el.innerHTML+='<div class="domino" id="placeholder"></div>';
    // change id to match next domino
    oldId=el.id;
    el.id=oldId.slice(0,oldId.length-1)+(last+1)
    checkCorrectness();
}


function checkCorrectness() {
    let items = document.getElementsByClassName("domino-part")
    let counter = 0;
    for(let x = 0; x < items.length; x++) {
        if(items[x].classList !== undefined && items[x].className.includes("correct") && !items[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === items.length) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}


function redo(e) {
}


$(function () {
});
