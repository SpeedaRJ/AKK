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
    url: "/glossary/personal_traits",
    success: function(result) {
        let glossary = document.getElementById("glossary");
        let vocab = result["vocabulary"]
        for(var x in vocab){
            var node = document.createElement("li");
            var arrow = document.createElement("i");
            var span = document.createElement("span");
            arrow.setAttribute("class", "fa fa-arrow-right");
            arrow.setAttribute("aria-hidden", "true");
            node.innerHTML = x + " ";
            span.appendChild(arrow);
            node.appendChild(span);
            node.innerHTML += " " + vocab[x];
            node.classList.add("glossary_element");
            glossary.appendChild(node);
        }
    }
})
});