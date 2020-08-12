
function recolor() {
    let svg = document.getElementById("character").contentDocument.children[0];
    let colors = JSON.parse(document.getElementById("colors").textContent);
    let parts = JSON.parse(document.getElementById("parts").textContent);
    let querySelector = "";
    [].forEach.call(Object.keys(parts), function (el) {
        querySelector += parts[el] + ",";
    });
    [].forEach.call(svg.querySelectorAll(querySelector.substring(0, querySelector.length - 1)), function (el) {
        let el_list = el.id;
        if (/Koza/.test(el_list)) {
            el.setAttribute("style", "fill: " + colors['body_color']);
        } else if (/Vrat/.test(el_list)) {
            el.setAttribute("style", "fill: " + colors['neck']);
        } else if (/Lasje/.test(el_list)) {
            el.setAttribute("style", "fill: " + colors['hair_color']);
        } else if (/Brada/.test(el_list)) {
            el.setAttribute("style", "fill: " + colors['hair_color']);
        } else if (/Brki/.test(el_list)) {
            el.setAttribute("style", "fill: " + colors['hair_color']);
        } else if (/Obrve-4/.test(el_list)) {
            el.setAttribute("style", "fill: " + colors['hair_color']);
        } else if (/Obrve-2/.test(el_list)) {
            el.setAttribute("style", "fill: " + colors['hair_color']);
        } else if (/Obrve$/.test(el_list)) {
            try{
                el.children[0].setAttribute("style", "fill: " + colors['hair_color']);
            } catch(e) {
                el.setAttribute("style", "fill: " + colors['hair_color']);
            }
        } else if (/obrve$/.test(el_list)) {
            try{
                el.children[0].setAttribute("style", "fill: " + colors['hair_color']);
            } catch(e) {
                el.setAttribute("style", "fill: " + colors['hair_color']);
            }
        }
    });
}

$(window).on("load", function () {
    recolor();
})

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function update(d) {
    update_session(d)
    await(timeout(500));
    location.reload();
}

function update_session(d) {
    $.ajax({
        type: 'POST',
        url: "/update_session/" + Object.keys(d)[0],
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, "d": d}
    });
}