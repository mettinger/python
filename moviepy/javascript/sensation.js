const img = document.getElementById('bodyImage');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');


const slider = document.getElementById("myRange");
const maxQueueSize = parseInt(slider.max);
var queueSize = slider.value;

const width = img.naturalWidth;
const height = img.naturalHeight;

var sleepTime = 1;
var addSize = 1;
var subSize = 1;

const recSize = 5;

var imgData = [];
var totalBodyPixels;

const getColor = () => `rgb(${0},${0},${255}`
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

function processImage() {

    const bodyArray = [];
    var canvas2 = document.createElement('canvas');
    var context = canvas2.getContext('2d');
    context.drawImage(img, 0, 0);
    imgData = [];
    imgData = context.getImageData(0, 0, width, height).data;
    
    for (let i = 0; i < imgData.length; i += 4) {
        if (Math.max(...imgData.slice(i, i + 3)) > 150) {
            bodyArray.push(i/4)
        } 
    }
    totalBodyPixels = bodyArray.length;
    return bodyArray
}

const drawDot = async (bodyArray) => {
    var x; 
    var y; 
    ctx.fillStyle = getColor();
    var randomIndex;
    //const numPixels = bodyArray.length;
    var queue = [];

    while (true) {

        if (queue.length > queueSize) {
            if (queueSize < maxQueueSize) {
                addSize = 1;
                subSize = 2;
            }
            else {
                addSize = 1;
                subSize = 0;
            }
        }

        if (queue.length < queueSize) {
            if (queue.length > 0) {
                addSize = 2;
                subSize = 1;
            }
            else {
                addSize = 1;
                subSize = 0;
            }
        }

        if (queue.length == queueSize) {
            if (queueSize < maxQueueSize) {
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

            if (queue.length > 0 || queueSize > 1) {
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

window.addEventListener('load', () => {

    canvas.width = width;
    canvas.height = height;

    slider.oninput = function() {
        queueSize = maxQueueSize - parseInt(this.value);
    }
  
    const bodyArray = processImage();
    drawDot(bodyArray);
  })

  