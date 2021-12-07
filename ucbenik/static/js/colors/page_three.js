let colors = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Pink", "Black", "Grey", "White", "Brown", "Gold", "Silver"];
let hex_codes = ["#EE202E", "#F26524", "#F7ED38", "#099E43", "#3097C3", "#7A2A90", "#EF509C", "#231F20", "#85837D", "#F8F8F8", "#653614", "#FBAD18", "#aaa9ad"];

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
            for (var i = 0; i < children.length; i++) {
                if (children[i].classList !== undefined && children[i].className.includes("incorrect")) {
                    toOrigin1(children[i]);
                    break;
                }
            }
            if (i === children.length && i > 1)
                return;
        } catch {
            return;
        }
    }
    var origin = document.getElementById('drag-origin');

    ev.preventDefault();
    var data = ev.dataTransfer.getData("Text");
    correct = data.search("color" + el.id.substring(el.id.length - 1)) > -1;
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
    for (let x = 0; x < items.length; x++) {
        if (items[x].classList !== undefined && items[x].className.includes("correct") && !items[x].className.includes("incorrect"))
            counter++;
    }
    if (counter === items.length) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
        document.getElementById("next").setAttribute("disabled", "disabled");
    }
}

function setColors() {
    let selected = [];
    while (selected.length !== 5) {
        let randomElement = colors[Math.floor(Math.random() * colors.length)];
        if (!selected.includes(randomElement)) selected.push(randomElement);
    }
    let hex = [];
    for (let color in selected) {
        hex.push(hex_codes[colors.findIndex((element) => element === selected[color])]);
    }
    document.getElementById("color01").style.backgroundColor = hex[0];
    document.getElementById("color02").style.backgroundColor = hex[1];
    document.getElementById("color03").style.backgroundColor = hex[2];
    document.getElementById("color04").style.backgroundColor = hex[3];
    document.getElementById("color05").style.backgroundColor = hex[4];
    document.getElementById("color1").innerHTML = selected[0];
    document.getElementById("color2").innerHTML = selected[1];
    document.getElementById("color3").innerHTML = selected[2];
    document.getElementById("color4").innerHTML = selected[3];
    document.getElementById("color5").innerHTML = selected[4];
}

function redo(e) {
    let node = [].slice.call(document.getElementsByClassName("draggable-word"));
    if (node.some((el) => el.className.includes("correct")))
        [].forEach.call(node, function (el) { el.click(); console.log(el) });
    setColors();
}


$(function () {
    sortItems();
    setColors();
});
