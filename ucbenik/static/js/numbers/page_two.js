let colors = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"];
let hex_codes = ["1","2","3","4","5","6","7","8","9","10"];

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
    correct = data.search("color" + el.id.substring(el.id.length-1)) > -1;
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

function setColors() {
    let selected = [];
    while (selected.length !== 5) {
        let randomElement = colors[Math.floor(Math.random() * colors.length)];
        if(!selected.includes(randomElement)) selected.push(randomElement);
    }
    let hex = [];
    for(let color in selected) {
        hex.push(hex_codes[colors.findIndex((element) => element === selected[color])]);
    }
    document.getElementById("match01").innerHTML = hex[0];
    document.getElementById("match02").innerHTML = hex[1];
    document.getElementById("match03").innerHTML = hex[2];
    document.getElementById("match04").innerHTML = hex[3];
    document.getElementById("match05").innerHTML = hex[4];
    document.getElementById("match1").innerHTML = selected[0];
    document.getElementById("match2").innerHTML = selected[1];
    document.getElementById("match3").innerHTML = selected[2];
    document.getElementById("match4").innerHTML = selected[3];
    document.getElementById("match5").innerHTML = selected[4];
}

function redo(e) {
    let node = [].slice.call(document.getElementsByClassName("draggable-word"));
    if(node.some((el) => el.className.includes("correct")))
        [].forEach.call(node, function(el) {el.click(); console.log(el)});
    setColors();
}


$(function () {
    sortItems();
    setColors();
});
