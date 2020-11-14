function toOrigin(el) {
    var origin = document.getElementById('drag-origin');
    if (origin === el.parentElement) return;
    var text = document.getElementById("sentence "+el.id);
    console.log(text);
    origin.appendChild(el);
    var div_with_sentences = document.getElementById("sentences");
    div_with_sentences.removeChild(text);
    var draghere = document.getElementById("draghere");
    console.log(draghere.children);
    if(draghere.children.length === 0){
        draghere.setAttribute("style","display: flex; align-items: center; justify-content: center;flex-direction: column;\n" +
            "                flex-wrap: wrap; height: 450px; border-radius: 25px");
        var text_2 = document.createElement("h3");
        text_2.innerText = "Drag here!";
        text_2.id ="DragHere";
        draghere.appendChild(text_2);
    }
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    console.log(ev);
    ev.dataTransfer.setData("Text", ev.target.id);
}

function drop(ev, el) {
    var dragehere = document.getElementById("DragHere");
    if(dragehere !== null){
        el.removeChild(dragehere);
        el.setAttribute("style","display: flex; flex-direction: column; height:  450px; border-radius: 25px;")
    }
    ev.preventDefault();
    var data = ev.dataTransfer.getData("Text");
    var child = document.getElementById(data);
    el.appendChild(child);
    var div_with_sentences = document.getElementById("sentences");
    var text = document.createElement("p");
    text.innerHTML = sentences[data];
    text.id = "sentence " + data;
    div_with_sentences.appendChild(text);
}
var sentences = {};
$(document).ready(function () {
    $.ajax({
        url: "/pictures",
        success: function (result) {
            var pictures = document.getElementById("drag-origin");
            var count = 0;
            for (var i in result.links) {
                var temp = i;
                if (i.includes("0")) {
                    var list = i.split("0");
                    temp = list[0] + list[1];
                }
                var obj = document.createElement("object");
                obj.classList.add("img-visual");
                obj.setAttribute("type", "image/svg+xml");
                obj.setAttribute("data", "/static/" + temp);
                obj.setAttribute("style","height:25px;");
                var p = document.createElement("p");
                p.appendChild(obj);
                p.setAttribute("ondragstart", "drag(event)");
                p.setAttribute("onclick", "toOrigin(this)");
                p.setAttribute("id", "match" + count);
                p.setAttribute("draggable", "true");
                p.classList.add("draggable-word");
                p.setAttribute("style","margin:0; width:100;");
                sentences[p.id] = result.links[i];
                pictures.appendChild(p);
                count++;
            }
        }
    });
});