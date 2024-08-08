async function reloadPhotos() {
    const response = await fetch('/photos');
    const list = await response.json();

    const ul = document.querySelector('#links ul');
    ul.innerHTML = '';

    for (let name of list) {
        const link = document.createElement("li");
        link.innerHTML = `<a href="/photo/${name}" target="_blank">${name}</a>`;
        ul.appendChild(link);
    }
}

async function resizeCanvas(canvas) {
    let parentRect = canvas.parentNode.getBoundingClientRect();
    let baseSide = parentRect.width >= parentRect.height * 1.3333 ? "height" : "width";
    if (baseSide === "width") {
        let base = parentRect.width * 0.8;
        canvas.style.width = Math.round(base) + "px";
        canvas.style.height = Math.round(base * 0.75) + "px";
    } else {
        let base = parentRect.height * 0.8;
        canvas.style.height = Math.round(base) + "px";
        canvas.style.width = Math.round(base * 1.33333) + "px";
    }
}

// Show loading notice
var canvas = document.getElementById('videoCanvas');
var ctx = canvas.getContext('2d');
ctx.fillStyle = 'white';
ctx.fillText('Loading...', canvas.width/2-30, canvas.height/3);

window.onresize = () => resizeCanvas(canvas);
resizeCanvas(canvas);

// Setup the WebSocket connection and start the player
var client = new WebSocket('ws://' + window.location.hostname + ':8084');
var player = new jsmpeg(client, {canvas:canvas});

var photoBtn = document.getElementById('photo-btn');
photoBtn.addEventListener('click', async function () {
    let sizeValue = document.querySelector("#form-size").value;
    let [_, width, height] = sizeValue.match(/(\d+)x(\d+)/);
    let shutterSpeedStr = document.querySelector("#form-shutter").value;
    let shutterSpeedF;
    if (shutterSpeedStr.match(/\//)) {
        let [_, numerator, denominator] = shutterSpeedStr.match(/(\d+)\/(\d+)/)
        shutterSpeedF = Number.parseFloat(numerator) / Number.parseFloat(denominator);
    } else {
        shutterSpeedF = Number.parseFloat(shutterSpeedStr);
    }
    let data = {
        "width": Number.parseInt(width),
        "height": Number.parseInt(height),
        "iso": Number.parseInt(document.querySelector("#form-iso").value),
        "shutter_speed_sec": shutterSpeedF
    };
    document.querySelector("#photo-btn").setAttribute("disabled", true);
    const response = await fetch('/make_photo', {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    });
    const respJson = await response.json();
    const name = respJson.name;
    alert(name);
    document.querySelector("#photo-btn").removeAttribute("disabled");

    reloadPhotos();
});

var videoBtn = document.getElementById('video-btn');
videoBtn.addEventListener('click', async function () {
    let data = {
        "iso": Number.parseInt(document.querySelector("#form-video-iso").value),
    };
    document.querySelector("#video-btn").setAttribute("disabled", true);
    const response = await fetch('/video_settings', {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    });
    const respJson = await response.json();
    const status = respJson.status;
    alert(status);
    document.querySelector("#video-btn").removeAttribute("disabled");
});
reloadPhotos();