var clicks = 1;

function spin(){
    clicks++
    document.getElementById('smug').style.animationDuration = `${10/clicks}s`
    document.getElementById('smugcount').innerHTML = `One spin per ${10/clicks}s`
}