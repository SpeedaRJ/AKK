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
        } else if (/cevlje/.test(el_list)) {
            el.setAttribute("style", "fill: " + colors['shoes_color']);
        } else if (/Obleka/.test(el_list)) {
            el.setAttribute("style", "fill: " + colors['dress_color']);
        } else if (/Majica/.test(el_list)) {
            el.setAttribute("style", "fill: " + colors['shirt_color']);
        } else if (/Hlace/.test(el_list)) {
            el.setAttribute("style", "fill: " + colors['pants_color']);
        }
    });
}

function update_session(d) {
    $.ajax({
        type: 'POST',
        url: "/update_session/" + Object.keys(d)[0],
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, "d": d}
    });
}

function changeSuite(el) {
    let svg = document.getElementById("character").contentDocument.children[0];
    if (el.id === "red_suite") {
        svg.querySelector("[id^=Pulover]").setAttribute("style", "fill:" + "rgb(145,44,70)");
        svg.querySelector("[id^=Hlace]").setAttribute("style", "fill:" + "rgb(210,186,183)");
        [].forEach.call(svg.querySelectorAll("[id^=Gumb]"), function (e) {
            e.setAttribute("style", "fill:" + "rgb(120,18,28)");
        });
    } else if (el.id === "blue_suite") {
        svg.querySelector("[id^=Pulover]").setAttribute("style", "fill:" + "rgb(0,84,166)");
        svg.querySelector("[id^=Hlace]").setAttribute("style", "fill:" + "rgb(123,175,222)");
        [].forEach.call(svg.querySelectorAll("[id^=Gumb]"), function (e) {
            e.setAttribute("style", "fill:" + "rgb(0,61,123)");
        });
    } else if (el.id === "green_suite") {
        svg.querySelector("[id^=Pulover]").setAttribute("style", "fill:" + "rgb(0,168,129)");
        svg.querySelector("[id^=Hlace]").setAttribute("style", "fill:" + "rgb(0,125,172)");
        [].forEach.call(svg.querySelectorAll("[id^=Gumb]"), function (e) {
            e.setAttribute("style", "fill:" + "rgb(72,144,134)");
        });
    }
}