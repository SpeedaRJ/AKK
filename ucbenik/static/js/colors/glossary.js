$( document ).ready(function() {
    document.getElementById("gButton").addEventListener("click", function() {
        var glossary = document.getElementById("glossary");
        if(glossary.hasAttribute("hidden")){
                glossary.removeAttribute("hidden");
            }
        else {
                glossary.setAttribute("hidden", true);
            }
    });

    $.ajax({
    url: "/glossary/colors",
    success: function(result) {
        let glossary = document.getElementById("glossary");
        for(var x in result){
            for(var y in result[x]) {
                var node = document.createElement("li");
                var arrow = document.createElement("i");
                var span = document.createElement("span");
                arrow.setAttribute("class", "fa fa-arrow-right");
                arrow.setAttribute("aria-hidden", "true");
                node.innerHTML = y + " ";
                span.appendChild(arrow);
                node.appendChild(span);
                node.innerHTML += " " + result[x][y];
                node.classList.add("glossary_element");
                glossary.appendChild(node);
                console.log(result);
            }
            if(x == "vocabulary") glossary.appendChild(document.createElement("hr"));
        }
    }
})
});