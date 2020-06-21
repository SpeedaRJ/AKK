function show_nickname(e) {
    document.getElementById("nickname_input").style.display = "block";
    if(e.target.innerHTML === "No")
        document.getElementById("nickname_input").style.display = "none";
    document.getElementById("next").removeAttribute("disabled")
}

$(document).ready(function() {
    document.getElementById("name_input").addEventListener("input", function(e) {
        dynamic_name(e);
    });
});