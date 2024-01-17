const img = document.getElementById('bodyImage');
const canvas = document.getElementById('canvas');
const slider = document.getElementById("myRange");

const width = img.naturalWidth;
const height = img.naturalHeight;
const ctx = canvas.getContext('2d');

const getColor = () => `rgb(${0},${0},${255}`
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
var imgData = [];

var sleepTime = 1;
var queueSize = 1;

var addSize = 1;
var subSize = 1;

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

function processImage() {

    const bodyArray = [];

    var canvas2 = document.createElement('canvas');
    var context = canvas2.getContext('2d');
    context.drawImage(img, 0, 0);


    imgData = context.getImageData(0, 0, width, height).data;
    
    for (let i = 0; i < imgData.length; i += 4) {
        if (Math.max(...imgData.slice(i, i + 3)) > 150) {
            bodyArray.push(i/4)
        } 
    }
    //console.log(bodyArray.length)
    return bodyArray
}

const drawDot = async (bodyArray) => {
    const recSize = 10;
    var x = 100; 
    var y = 100; 
    ctx.fillStyle = getColor();
    var randomIndex;
    const numPixels = bodyArray.length;
    var queue = [];
    queue.push([0,0]);

    while (true) {

        if (queue.length > queueSize) {
            addSize = 1;
            subSize = 2;
        }

        if (queue.length < queueSize) {
            addSize = 2;
            subSize = 1;
        }

        if (queue.length == queueSize) {
            if (queueSize < 1000) {
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
            x = point[0];
            y = point[1]
            ctx.clearRect(x-1, y-1, recSize + 2, recSize + 2)
        }

        for (let j = 0; j < addSize; j++) {
            randomIndex = getRandomInt(numPixels);
            randomPixel = bodyArray[randomIndex];
            y = Math.floor(randomPixel/width);
            x = randomPixel % height;

            ctx.fillRect(x, y, recSize, recSize);
            queue.push([x,y])
        }
        await sleep(sleepTime);

    }
}

window.addEventListener('load', () => {

    canvas.width = width;
    canvas.height = height;

    slider.oninput = function() {
        queueSize = parseInt(this.value);
        console.log(queueSize)
    }

    //canvas.addEventListener('click', drawDot)
  
    const bodyArray = processImage();
    drawDot(bodyArray);
  })

  