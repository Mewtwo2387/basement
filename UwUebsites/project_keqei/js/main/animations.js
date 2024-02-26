function newAnimatedImg(x,y,src){
    const template = document.getElementById('animatedImg').content.cloneNode(true);
    const element = template.querySelector('.animatedImg');
    element.style.left = x + '%';
    element.style.top = y + '%';
    element.src = src;
    document.getElementById('body').appendChild(element);
    setTimeout(function(){
        element.remove();
    },5000);
}
function newAnimatedDamage(x,y,damage){
    const template = document.getElementById('animatedDamage').content.cloneNode(true);
    const element = template.querySelector('.animatedDamage');
    element.style.left = x + '%';
    element.style.top = y + '%';
    element.innerHTML = damage;
    document.getElementById('body').appendChild(element);
    setTimeout(function(){
        element.remove();
    },5000);
}