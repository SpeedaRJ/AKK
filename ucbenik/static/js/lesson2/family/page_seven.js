function next(el) {
    document.getElementById("first-part").style.display="none";
    document.getElementById("second-part").style.display="block";
    document.getElementById("next").removeAttribute("disabled");
    el.style.display="none";
}