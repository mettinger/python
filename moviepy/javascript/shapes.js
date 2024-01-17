window.addEventListener('load', () => {
    const canvas = document.getElementById('canvas')
    const width = canvas.width
    const height = canvas.height
    const ctx = canvas.getContext('2d')
    const random255 = () => Math.floor(Math.random() * 255)
    const randomColor = () => `rgba(${random255()},${random255()},${random255()},0.5`
    const randomX = () => (Math.random() * width) - 50
    const randomY = () => (Math.random() * height) - 50
    const randomSide = () => (Math.random() * 100) + 20
    const randomRadius = () => (Math.random() * 50) + 20
  
    const drawShapes = () => {
      ctx.clearRect(0, 0, width, height)
      for (let i = 0; i < 50; i += 1) {
        ctx.fillStyle = randomColor()
        ctx.fillRect(randomX(), randomY(), randomSide(), randomSide())
        ctx.fillStyle = randomColor()
        ctx.beginPath()
        ctx.arc(randomX(), randomY(), randomRadius(), 0, Math.PI * 2, true)
        ctx.closePath()
        ctx.fill()
      }
    }
  
    canvas.addEventListener('click', drawShapes)
  
    drawShapes()
  })