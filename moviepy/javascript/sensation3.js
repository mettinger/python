
var sleepTime = 1;
var addSize = 1;
var subSize = 1;

const recSize = 5;

var imgData = [];
var totalBodyPixels;
var gQueueSize

const getColor = () => `rgb(${0},${0},${255}`
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

function domInit() {
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const img = document.getElementById('bodyImage');
    const slider = document.getElementById("myRange");
    const maxQueueSize = parseInt(slider.max);
    const queueSize = slider.value;

    const width = img.naturalWidth;
    const height = img.naturalHeight;

    console.log({
        msg: "domInit",
        width,
        height
    })
    return {
        ctx,
        slider,
        img,
        width,
        height,
        queueSize,
        maxQueueSize,
    }
}

async function processImage({
  img,
  width,
  height
}) {

    const bodyArray = [];
    var canvas2 = document.createElement('canvas');
    canvas2.width = width;
    canvas2.height = height;
    var context = canvas2.getContext('2d');
    context.drawImage(img, 0, 0);
    const bodyImg = context.getImageData(0, 0, width, height);
    console.log({
        width: bodyImg.width,
        height: bodyImg.height,
        length: bodyImg.data.length
    })
    imgData = bodyImg.data

    for (let i = 0; i < imgData.length; i += 4) {
        if (Math.max(...imgData.slice(i, i + 3)) > 150) {
            bodyArray.push(i/4)
        }
    }

    totalBodyPixels = bodyArray.length;
    console.log({
        totalBodyPixels
    })
    return bodyArray
}

const drawDot = async (bodyArray, {
  ctx,
  width,
  height,
  maxQueueSize
}) => {
    var x;
    var y;
    ctx.fillStyle = getColor();
    var randomIndex;
    //const numPixels = bodyArray.length;
    var queue = [];

    while (true) {

        if (queue.length > gQueueSize) {
            if (gQueueSize < maxQueueSize) {
                addSize = 1;
                subSize = 2;
            }
            else {
                addSize = 1;
                subSize = 0;
            }
        }

        if (queue.length < gQueueSize) {
            if (queue.length > 0) {
                addSize = 2;
                subSize = 1;
            }
            else {
                addSize = 1;
                subSize = 0;
            }
        }

        if (queue.length == gQueueSize) {
            if (gQueueSize < maxQueueSize) {
                addSize = 1;
                subSize = 1;
            }
            else {
                addSize = 1;
                subSize = 0
            }
        }

        for (let j = 0; j < subSize; j++) {
            point = queue.shift();

            y = Math.floor(point/width);
            x = point % height;

            ctx.clearRect(x-1, y-1, recSize + 2, recSize + 2);
            bodyArray.push(point);
        }

        for (let j = 0; j < addSize; j++) {

            if (queue.length > 0 || gQueueSize > 1) {
                randomIndex = getRandomInt(bodyArray.length);
                randomPixel = bodyArray.splice(randomIndex, 1)[0];
                queue.push(randomPixel);
                y = Math.floor(randomPixel/width);
                x = randomPixel % height;
                ctx.fillRect(x, y, recSize, recSize);
            }
            else {
                x = getRandomInt(width);
                y = getRandomInt(height);
                ctx.fillRect(x, y, recSize, recSize);
                await sleep(sleepTime);
                ctx.clearRect(x-1, y-1, recSize + 2, recSize + 2);
            }

        }
        await sleep(sleepTime);

    }
}

window.addEventListener('load', async () => {
    const {
        ctx,
        slider,
        img,
        width,
        height,
        queueSize,
        maxQueueSize,
     } = domInit()
    gQueueSize = queueSize;
    canvas.width = width;
    canvas.height = height;

    slider.oninput = function() {
        gQueueSize = maxQueueSize - parseInt(this.value);
    }

    const bodyArray = await processImage({ img, width, height });
    drawDot(bodyArray, {
        ctx,
        width,
        height,
        maxQueueSize
    });
  })

