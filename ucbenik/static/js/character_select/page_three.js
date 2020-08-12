const pSBC = (p, c0, c1, l) => {
    let r, g, b, P, f, t, h, i = parseInt, m = Math.round, a = typeof (c1) == "string";
    if (typeof (p) != "number" || p < -1 || p > 1 || typeof (c0) != "string" || (c0[0] != 'r' && c0[0] != '#') || (c1 && !a)) return null;
    if (!this.pSBCr) this.pSBCr = (d) => {
        let n = d.length, x = {};
        if (n > 9) {
            [r, g, b, a] = d = d.split(","), n = d.length;
            if (n < 3 || n > 4) return null;
            x.r = i(r[3] == "a" ? r.slice(5) : r.slice(4)), x.g = i(g), x.b = i(b), x.a = a ? parseFloat(a) : -1
        } else {
            if (n == 8 || n == 6 || n < 4) return null;
            if (n < 6) d = "#" + d[1] + d[1] + d[2] + d[2] + d[3] + d[3] + (n > 4 ? d[4] + d[4] : "");
            d = i(d.slice(1), 16);
            if (n == 9 || n == 5) x.r = d >> 24 & 255, x.g = d >> 16 & 255, x.b = d >> 8 & 255, x.a = m((d & 255) / 0.255) / 1000;
            else x.r = d >> 16, x.g = d >> 8 & 255, x.b = d & 255, x.a = -1
        }
        return x
    };
    h = c0.length > 9, h = a ? c1.length > 9 ? true : c1 == "c" ? !h : false : h, f = this.pSBCr(c0), P = p < 0, t = c1 && c1 != "c" ? this.pSBCr(c1) : P ? {
        r: 0,
        g: 0,
        b: 0,
        a: -1
    } : {
        r: 255,
        g: 255,
        b: 255,
        a: -1
    }, p = P ? p * -1 : p, P = 1 - p;
    if (!f || !t) return null;
    if (l) r = m(P * f.r + p * t.r), g = m(P * f.g + p * t.g), b = m(P * f.b + p * t.b);
    else r = m((P * f.r ** 2 + p * t.r ** 2) ** 0.5), g = m((P * f.g ** 2 + p * t.g ** 2) ** 0.5), b = m((P * f.b ** 2 + p * t.b ** 2) ** 0.5);
    a = f.a, t = t.a, f = a >= 0 || t >= 0, a = f ? a < 0 ? t : t < 0 ? a : a * P + t * p : 0;
    if (h) return "rgb" + (f ? "a(" : "(") + r + "," + g + "," + b + (f ? "," + m(a * 1000) / 1000 : "") + ")";
    else return "#" + (4294967296 + r * 16777216 + g * 65536 + b * 256 + (f ? m(a * 255) : 0)).toString(16).slice(1, f ? undefined : -2)
};

const prepend = "http://127.0.0.1:8000/";
        function select(el) {
            let colors = document.getElementsByClassName("color");
            for (var item of colors) {
                if("unselected" in item.classList)
                    continue
                else
                    item.classList.add("unselected")
                    item.classList.remove("selected");
            }
            el.classList.remove("unselected");
            el.classList.add("selected");
            recolorHair();
        }
        function recolor() {
            try {
                var svg = document.getElementById("character").contentDocument.children[0];
            } catch(e) {
                setTimeout(function (){
                    recolor()
                }, 500);
                return
            }
            let colors = JSON.parse(document.getElementById("colors").textContent);
            let parts = JSON.parse(document.getElementById("parts").textContent);
            let querySelector = "";
            [].forEach.call(Object.keys(parts), function (el) {
                querySelector += parts[el] + ",";
            });
            [].forEach.call(svg.querySelectorAll(querySelector.substring(0, querySelector.length - 1)), function (el) {
                let el_list = el.id;
                if (/Koza/.test(el_list)) {
                    el.setAttribute("style", "fill: "+colors['body_color']);
                }else if(/Vrat/.test(el_list)){
                    el.setAttribute("style", "fill: "+ colors['neck']);
                }
            });
            recolorHair();
        }
        function recolorHair(){
            try {
                var svg = document.getElementById("character").contentDocument.children[0];
            } catch(e) {
                setTimeout(function (){
                    recolorHair()
                }, 500);
                return
            }
            let color = document.getElementsByClassName("selected")[0].style.backgroundColor;

            [].forEach.call(svg.querySelectorAll("[id^=Lasje]"),function (el) {
                el.setAttribute("style","fill:"+color);
            });

            [].forEach.call(svg.querySelectorAll("[id^=Obrve]"),function (el) {
                try{
                    el.children[0].setAttribute("style", "fill: " + color);
                } catch(e) {
                    el.setAttribute("style", "fill: " + color);
                }
            });

            [].forEach.call(svg.querySelectorAll("[id^=obrve]"),function (el) {
                try{
                    el.children[0].setAttribute("style", "fill: " + color);
                } catch(e) {
                    el.setAttribute("style", "fill: " + color);
                }
            });

            [].forEach.call(svg.querySelectorAll("[id^=Obrve-2]"),function (el) {
                el.setAttribute("style","fill:"+color);
            });

            [].forEach.call(svg.querySelectorAll("[id^=Obrve-4]"),function (el) {
                el.setAttribute("style","fill:"+color);
            });
        }
        $(window).on( "load",function(){
            recolor();
        })

        function changeHairStyle(el, sex) {
            let svg = document.getElementById("character");
            let url = svg.data.split("/");
            const predict = (element) => element === "static";
            let index = url.findIndex(predict);
            let new_url = "";
            if (url[url.findIndex((element) => element === "short_hair" || element === "long_hair" || element === "bald" || element === "patch" || element === "bun.svg" || element === "curly.svg" || element === "long.svg" || element === "medium.svg")] === el.id) {
                //console.log("Hairstyle already selected");
                return;
            }
            if (sex === "M") {
                for (let i = index; i < url.length; i++) {
                    if (url[i] === "short_hair" || url[i] === "long_hair" || url[i] === "bald" || url[i] === "patch") {
                        new_url += el.id + "/";
                    } else {
                        if (i === url.length - 1) {
                            new_url += url[i];
                        } else {
                            new_url += url[i] + "/";
                        }
                    }
                }
            } else {
                for (let i = index; i < url.length; i++) {
                    if (i === url.length - 1) {
                        new_url += el.id + ".svg";
                    } else {
                        new_url += url[i] + "/";
                    }
                }
            }
            svg.data = prepend + new_url;
            svg.addEventListener("reload", function () {
                recolor();
            });
        }

function changeSkinColor(e) {
    let svg = document.getElementById("character").contentDocument.children[0];
    [].forEach.call(svg.querySelectorAll(".cls-4"), function (el) {
        el.setAttribute("style", "fill:" + e.style.backgroundColor + ";");
    });
    [].forEach.call(svg.querySelectorAll(".cls-2"), function (el) {
        el.setAttribute("style", "fill:" + pSBC(0.15, e.style.backgroundColor) + ";");
    });
    let data = {
        "neck": pSBC(0.15, e.style.backgroundColor),
    };
    update_session(data);
    data = {
        "body_color": e.style.backgroundColor
    };
    update_session(data);

}

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

