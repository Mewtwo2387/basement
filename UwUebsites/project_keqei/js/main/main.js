var gameData = [];

var charactersData = [];
$.getJSON("characters.json?1", function(json) {
    charactersData = json;
  });
  
var currentChar = 0;
function login(){
    if(document.getElementById('usernameInput').value.length>=2 && document.getElementById('passwordInput').value.length>=2){
        if(/^[A-Za-z0-9]*$/.test(document.getElementById('usernameInput').value) && /^[A-Za-z0-9]*$/.test(document.getElementById('passwordInput').value)){
            if(ws.readyState==ws.OPEN){
                ws.send('login~' + document.getElementById('usernameInput').value + '~' + document.getElementById('passwordInput').value)
            }else{
                document.getElementById('signupError').style.color = 'red';
                document.getElementById('signupError').innerHTML = 'Unable to connect to server'
            }      
        }else{
            document.getElementById('loginError').style.color = 'red';
            document.getElementById('loginError').innerHTML = 'Usernames and passwords can only contain numbers and letters'
        }
    }else{
        document.getElementById('loginError').style.color = 'red';
        document.getElementById('loginError').innerHTML = 'Usernames and passwords cannot be shorter than 2 characters'
    }
}
function signup(){
    if(document.getElementById('usernameInputS').value.length>=2 && document.getElementById('passwordInputS').value.length>=2){
        if(/^[A-Za-z0-9]*$/.test(document.getElementById('usernameInputS').value) && /^[A-Za-z0-9]*$/.test(document.getElementById('passwordInputS').value && /^[A-Za-z0-9]*$/.test(document.getElementById('repasswordInputS').value))){
            if(document.getElementById('passwordInputS').value==document.getElementById('repasswordInputS').value){
                if(ws.readyState==ws.OPEN){
                    ws.send('signup~' + document.getElementById('usernameInputS').value + '~' + document.getElementById('passwordInputS').value)
                }else{
                    document.getElementById('signupError').style.color = 'red';
                    document.getElementById('signupError').innerHTML = 'Unable to connect to server'
                }
            }else{
                document.getElementById('signupError').style.color = 'red';
                document.getElementById('signupError').innerHTML = 'Passwords does not match smh';
            }
        }else{
            document.getElementById('signupError').style.color = 'red';
            document.getElementById('signupError').innerHTML = 'Usernames and passwords can only contain numbers and letters'
        }
    }else{
        document.getElementById('signupError').style.color = 'red';
        document.getElementById('signupError').innerHTML = 'Usernames and passwords cannot be shorter than 2 characters'
    }
}
function switchlogin(){
    if(document.getElementById('loginDisplay').style.display == 'none'){
        document.getElementById('loginDisplay').style.display = 'block';
        document.getElementById('signupDisplay').style.display = 'none'
    }else{
        document.getElementById('loginDisplay').style.display = 'none';
        document.getElementById('signupDisplay').style.display = 'block'
    }
}
function chat(){
    if(document.getElementById('chatBar').value!="" && /^[A-Za-z0-9 ]*$/.test(document.getElementById('chatBar').value)){
        ws.send('chat~' + document.getElementById('chatBar').value)
        document.getElementById('chatBar').value = '';
    }
}
function openScreen(screen){
    var elements = document.getElementsByClassName('mainDisplay')
    for (var i = 0; i < elements.length; i++) {
        elements[i].style.display = 'none';
    }
    document.getElementById(screen).style.display = 'block';
}
function switchTab(tab){
    var elements = document.getElementsByClassName('charactersScreenMainRight')
    for (var i = 0; i < elements.length; i++) {
        elements[i].style.display = 'none';
    }
    document.getElementById(tab).style.display = 'block';
}
function update(){
    document.getElementById('coinLabel').innerHTML = gameData.coin;
    document.getElementById('coinLabelC').innerHTML = gameData.coin;
    document.getElementById('plutoniumLabel').innerHTML = gameData.plutonium;
    document.getElementById('plutoniumLabelC').innerHTML = gameData.plutonium;
    document.getElementById('rainbowOrbLabel').innerHTML = gameData.orb[0];
    loadteam();
    loadchar(currentChar);
}
function loadteam(){
    for(var i=0;i<=5;i++){
        if(gameData.team[i]==-1){
            var nsid = 'placeholder'
            var r = 1
            var l = ''
        }else{
            var nsid = charactersData[gameData.characters[gameData.team[i]].id].NamespaceID
            var r = charactersData[gameData.characters[gameData.team[i]].id].Rarity
            var l = 'Lv' + gameData.characters[gameData.team[i]].level
        }

        document.getElementById('t' + i).innerHTML = `<img class="s${r} icon-img" src="assets/images/characters/${nsid}.png"><p class="icon-text">${l}</p>`
    }
}
function loadchar(num){
    if(gameData.team[num]!=-1){
        currentChar = num;
        var id = gameData.characters[gameData.team[num]].id;
        document.getElementById('characterName').innerHTML = charactersData[id].Name;
        document.getElementById('characterRarity').innerHTML = charactersData[id].Rarity + ' Stars';
        document.getElementById('characterType').innerHTML = charactersData[id].Type;

        document.getElementById('characterATK').innerHTML =  gameData.characters[num].ATK.final;
        document.getElementById('characterHP').innerHTML =  gameData.characters[num].HP.final;
        document.getElementById('characterDEF').innerHTML =  gameData.characters[num].DEF.final;
        document.getElementById('characterPower').innerHTML =  gameData.characters[num].power;

        document.getElementById('res1').innerHTML =  charactersData[id].Res1Desc;
        document.getElementById('res2').innerHTML =  charactersData[id].Res2Desc;
        document.getElementById('res3').innerHTML =  charactersData[id].Res3Desc;

        document.getElementById('attackQTitle').innerHTML =  charactersData[id].NameQ;
        document.getElementById('attackQDesc').innerHTML =  charactersData[id].DescQ;
        document.getElementById('attackQType').innerHTML =  charactersData[id].TypeQ;
        document.getElementById('attackQAcc').innerHTML =  charactersData[id].AccQ;
        document.getElementById('attackQAtk').innerHTML =  charactersData[id].AtkQ;
        document.getElementById('attackQCrate').innerHTML =  gameData.characters[num].CrateQ.final;
        document.getElementById('attackQCdmg').innerHTML =  gameData.characters[num].CdmgQ.final;
        
        document.getElementById('attackETitle').innerHTML =  charactersData[id].NameE;
        document.getElementById('attackEDesc').innerHTML =  charactersData[id].DescE;
        document.getElementById('attackEType').innerHTML =  charactersData[id].TypeE;
        document.getElementById('attackEAcc').innerHTML =  charactersData[id].AccE;
        document.getElementById('attackEAtk').innerHTML =  charactersData[id].AtkE;
        document.getElementById('attackECrate').innerHTML =  gameData.characters[num].CrateE.final;
        document.getElementById('attackECdmg').innerHTML =  gameData.characters[num].CdmgE.final;
        
        document.getElementById('lore').innerHTML =  gameData.characters[num].Lore;

        document.getElementById('characterImg').src = `assets/images/characters/${charactersData[id].NamespaceID}.png`
    }else{
        console.log('no char')
    }
}
/*
function test(){
    newAnimatedImg(100,130)
    newAnimatedImg(100,330)
    newAnimatedImg(100,530)
    newAnimatedImg(300,130)
    newAnimatedImg(300,330)
    newAnimatedImg(300,530)
    setTimeout(function(){
    newDamage(600,130)
    newDamage(600,330)
    newDamage(600,530)
    newDamage(800,130)
    newDamage(800,330)
    newDamage(800,530)

    for(let i=1;i<=6;i++){
        document.getElementById('c'+i).style.width = '20px';
    }
    },2500)
}
*/