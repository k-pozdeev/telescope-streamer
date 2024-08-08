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

var photoBtn = document.getElementById('photo-btn');
photoBtn.addEventListener('click', async function () {
    let sizeValue = document.querySelector("#form-size").value;
    let [_, width, height] = sizeValue.match(/(\d+)x(\d+)/);
    let shutterSpeedStr = document.querySelector("#form-shutter").value;
    let data = {
        "width": Number.parseInt(width),
        "height": Number.parseInt(height),
        "iso": Number.parseInt(document.querySelector("#form-iso").value),
        "shutter_speed_sec": shutterSpeedStr
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

var config, client, player;

async function setUp() {
    config = await fetch('/config');
    config = await config.json();

    document.querySelector('#form-video-iso').value = config['camera_video_iso'];
    document.querySelector('#form-size').value = config['camera_photo_resolution_x'] + 'x' + config['camera_photo_resolution_y'];
    document.querySelector('#form-iso').value = config['camera_photo_iso'];
    document.querySelector('#form-shutter').value = config['camera_photo_shutter_speed_sec'];

    // Setup the WebSocket connection and start the player
    client = new WebSocket('ws://' + window.location.hostname + ':' + config["server_ws_port"]);
    player = new jsmpeg(client, {canvas:canvas});

    reloadPhotos();
}

setUp();