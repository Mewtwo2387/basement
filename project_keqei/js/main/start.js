const dev = false;
if(dev){
    setTimeout(function(){
        document.getElementById("logoScreen").style.display = 'none'
        document.getElementById("loginScreen").style.display = 'none'
        document.getElementById("menuScreen").style.display = 'block'
    },3000)
}else{
    setTimeout(function(){
        document.getElementById("logoScreen").style.opacity = 0;
        document.getElementById("loginScreen").style.display = 'block'
        document.getElementById("menuScreen").style.display = 'none'
    },3000)
    setTimeout(function(){
        document.getElementById("logoScreen").style.display = 'none'
    },6000)
}
var time;
function ping(){
    time = new Date().getTime()
    ws.send('ping')
    console.log('ping')
}
function pong(){
    document.getElementById('ping').innerHTML = (new Date().getTime() - time) + ' ms'
    console.log('pong')
    setTimeout(function(){ping()},1000)
}
