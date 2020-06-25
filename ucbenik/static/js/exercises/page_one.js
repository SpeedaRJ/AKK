function toOrigin1(el) {
    var origin = document.getElementById('drag-origin');
    if (origin === el.parentElement) return;
    origin.appendChild(el);
    sortItems();
    checkCorrectness();
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

function drop(ev, el, limit) {
    if (el.children.length > limit) {
        try {
            element = el.children[1];
            toOrigin1(element)
        } catch {
            return;
        }
    }
    var origin = document.getElementById('drag-origin');
    
    /*
    for (let i = 0; i < origin.children.length; i++) {
        if (origin.children[i].id === ev.target.id) {
            origin.children[i].hidden = true;
        }
    }
    */
    ev.preventDefault();
    var data = ev.dataTransfer.getData("Text");
    //data.indexOf(el.id)
    correct = data.search('^' + el.id + '[0-9]$') > -1;
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
    //dragDropWordsMapping[data] = el.id;
    //saveWordDrag();
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