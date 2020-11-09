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

    document.getElementById("rButton").addEventListener("click", function() {
        var glossary = document.getElementById("rules");
        if(glossary.hasAttribute("hidden")){
                glossary.removeAttribute("hidden");
            }
        else {
                glossary.setAttribute("hidden", true);
            }
    });

    $.ajax({
        url: "/glossary/clothes",
        success: function(result) {
            let glossary = document.getElementById("glossary");
            let rule_set = document.getElementById("rules");
            let vocab = result["vocabulary"];
            let rules = result["rules"];
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
            for(var x in rules){
                var node = document.createElement("li");
                node.innerHTML = rules[x];
                node.classList.add("glossary_element");
                rule_set.appendChild(node);
            }
        }
    });
});