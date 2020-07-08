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
    console.log(el.id.substring(0, el.id.length-2))
    correct = data.search(el.id.substring(0, el.id.length-2)) > -1;
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

function sortItems() {
    var origin = document.getElementById('drag-origin');
    array = Array.prototype.slice.call(origin.children);
    array.sort(function (a, b) {
        return a.innerText.localeCompare(b.innerText);
    });

    for (var i = 0, len = array.length; i < len; i++) {
        var detatchedItem = origin.removeChild(array[i]);
        detatchedItem.classList = "draggable-word";
        origin.appendChild(detatchedItem);
    }
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





$(function () {
    sortItems();
});
