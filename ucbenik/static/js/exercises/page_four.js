function hideHint() {
    hint1 = document.getElementById("hint1");
    hint2 = document.getElementById("hint2");
    hint3 = document.getElementById("hint3");
    table = document.getElementById("help-table");
    hint3.style.display = "none";
    hint1.style.display = "none";
    table.style.display = "block";
    hint2.style.display = "block";
}

function showHint() {
    hint1 = document.getElementById("hint1");
    hint2 = document.getElementById("hint2");
    table = document.getElementById("help-table");
    hint1.style.display = "block";
    hint2.style.display = "none";
    table.style.display = "none";
}
