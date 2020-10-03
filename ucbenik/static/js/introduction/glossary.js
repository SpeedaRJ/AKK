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
    url: "/glossary/introduction",
    success: function(result) {
        let glossary = document.getElementById("glossary");
        for(var x in result){
            var node = document.createElement("li");
            var arrow = document.createElement("i");
            var span = document.createElement("span");
            arrow.setAttribute("class", "fa fa-arrow-right");
            arrow.setAttribute("aria-hidden", "true");
            node.innerHTML = x + " ";
            span.appendChild(arrow);
            node.appendChild(span);
            node.innerHTML += " " + result[x];
            node.classList.add("glossary_element");
            glossary.appendChild(node);
        }
    }
})
});