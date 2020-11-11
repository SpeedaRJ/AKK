function toOrigin1(el) {
    var origin = document.getElementById('drag-origin');
    if (origin === el.parentElement) return;
    origin.appendChild(el);
    sortItems();
    checkCorrectness();
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("Text", ev.target.id);
}

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
    console.log(correct);
    var child = document.getElementById(data);
    if (correct) {
        child.classList.add('correct');
        child.classList.remove('incorrect');
    } else {
        child.classList.add('incorrect');
        child.classList.remove('correct');
    }
    el.classList.add('full');
    el.appendChild(child);
    checkCorrectness();
}

function checkCorrectness() {
    let items = document.getElementsByClassName("draggable-word")
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

$(document).ready(function() {
    $.ajax({
        url: "/pictures",
        success: function(result) {
            var pictures = document.getElementById("drag-origin");
            var count = 0;
            for(var i in result.links) {
                if(i.includes("0")){
                    var list = i.split("0");
                    i = list[0] + list[1];
                }
                var child = document.createElement("div");
                child.classList.add("zaj");
                var obj = document.createElement("object");
                obj.classList.add("img-visual");
                obj.setAttribute("type", "image/svg+xml");
                obj.setAttribute("data", "/static/" + i)
                var p = document.createElement("p");
                p.innerHTML = result.links[i];
                p.setAttribute("hidden", "hidden");
                child.appendChild(obj);
                child.appendChild(p);
                child.setAttribute("ondragstart", "drag(event)");
                child.setAttribute("onclick", "toOrigin1(this)");
                child.setAttribute("id", "match" + count);
                child.setAttribute("draggable", "true");
                child.classList.add("draggable-word");
                pictures.appendChild(child);
                count++;
            }
        }
    });
});