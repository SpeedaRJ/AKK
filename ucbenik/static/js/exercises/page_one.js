let counter = 0;
let added = [];

function toOrigin1(el) {
    var origin = document.getElementById('drag-origin');
    if (origin === el.parentElement) return;
    origin.appendChild(el);
    sortItems();
    if (added.includes(el.id))
        counter--;
    delete added[added.indexOf(el.id)];
    if (counter < 12)
        document.getElementById("next").setAttribute("disabled", "disabled");

    //delete dragDropWordsMapping[el.id];
    //saveWordDrag();
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("Text", ev.target.id);
    //var ow = $('#drop-name');
    //ow.find('#nedokoncano').hide();
    //ow.addClass('opora-done');
}

function drop(ev, el) {
    if (el.children.length > 4) {
        alert("Div is full")
        return;
    }
    var origin = document.getElementById('drag-origin');
    for (let i = 0; i < origin.children.length; i++) {
        if (origin.children[i].id === ev.target.id) {
            origin.children[i].hidden = true;
        }
    }
    ev.preventDefault();
    var data = ev.dataTransfer.getData("Text");
    //data.indexOf(el.id)
    correct = data.search('^' + el.id + '[0-9]$') > -1;
    var child = document.getElementById(data);
    if (correct) {
        if (!added.includes(data)) {
            counter++;
            added.push(data);
        }
        child.classList.add('correct');
        child.classList.remove('incorrect');
    } else {
        if (added.includes(data)) {
            counter--;
            delete added[added.indexOf(data)];
        }
        child.classList.add('incorrect');
        child.classList.remove('correct');
    }
    el.classList.add('full');
    el.appendChild(child);
    if (counter === 12)
        document.getElementById("next").removeAttribute("disabled")
    //dragDropWordsMapping[data] = el.id;
    //saveWordDrag();
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
    console.log(document.getElementById("drag-origin"));
}

$(function () {
    sortItems();
});