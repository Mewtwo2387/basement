const jsdom = require('jsdom')
const dom = new jsdom.JSDOM("")
const jquery = require('jquery')(dom.window)
const WebSocket = require('ws');

const webSocketServer = new WebSocket.Server({ port: 8080 }), webSockets = {};

const elements = ['none','fire','water','grass','ice','rock','celestial','abyssmal','glitched'];
const elementalTable = [[1,1,1,1,1,1,1,1,1],[1,0.7,0.7,1.4,1.4,0.7,1,1,1],[1,1.4,0.7,0.7,0.7,1.4,1,1,1],[1,0.7,1.4,0.7,1,1,1,1,1],[1,0.7,1.4,1,0.7,1,1,1,1],[1,1.4,0.7,1,1,0.7,1,1,1],[1,1,1,1,1,1,0.7,1.4,1],[1,1,1,1,1,1,1.4,0.7,1],[1,1,1,1,1,1,1,1,1.4]] // [atker][defer]
const hangmanWords =
['akagi','aircraft carrier','akager','ijn akagi','herrscher of carriers','azur lane','keqs dum sis','ace person in horni server',
'fit','fit fits in the akagi','herrscher of non herrscher','fit x akagi','second normalest person','dont drown','dont die',
'eat grass','touch grass','herrscher of grasseating','mutualistic grasseating','allergic to grass','grass allergy',
'keq','keqqus','shitpost','shitposter','herrscher of shitposts','fumo','fumo keq','polska','keqislaw keqoski','keqing','lav','lavender','smol','smol oomfie',
'keq x ei','keqei','project keqei','fly me to the moon','ei','missingei','herrscher of horny','horny','horni','keq simp','i love keq',
'degen server','genshin replace','degen','degenerate','degeneration','ace','aroace',
'genshinplace','tgp','admin abooz','bought keepers','honorary travellers','horny travellers','moderators','trail mod','event mod','lore mod','design team','genshinplace newsletter',
'mod abuse','mod abooz','admin abuse','admin abooz','mod abooz pls demot','ban hammer',
'iras','admirs','herrscher of karezi love','karezi simp','karezi love','lord commander',
'mika','yelanbeloved','yelan simp','yelan','armpit','armpit impact','master of sigils','hand of the king',
'renvi','kay','polandball','renvikay','master of artistry','herrscher of scaramouche','scaramouche',
'lhbread','lefthandedbread','master of mechanics','bread','rhbread','righthandedbread','slug','slugpickle','pickle',
'noodle','purplebread','noodlebreadmoment','shop nooble panting','show noodle painting',
'doge','doggy','dog','venfei','aaaaaaaa','venti','yanfei','doge x venfei','fischl','fischl simp','fate','fate gifs','yow',
'aris','herrscher of eternity','eternity','town in greece','arista',
'gamebang','shameful writer','venti pp','venti simp','gamebang and the end of femboys','gamebang and the shameful voices','fanfic',
'blacke','blacke the sleep derived','astolfo','astolfo simp',
'potato','potat','smiling potato','baked potato',
'zykkard','zygarde','zebstrikkk','sussy','sussy baka','baka','sussy mod','demoted mod',
'karezi','karussy','redbread','karezi x iras','karezi x redbread','greenbread','bluebread','yellowbread','childe','childe simp','hydro bondage','herrscher of childe',
'ayaka','ayaka simp','mystic','mystichunterz','masterred','master of whispers','mommy mystic','hugswithmystic','hugswithmystic invasion',
'collective hivemind','hivemind','genshinplace hivemind','family tree','family bush','family matrix','incest','incestuous family',
'qiqi','qiqifallen','qiqi bumped into a tree','i forgot','i forgor','best mod','scammed out of mod','herrscher of roles',
'keiko','kei','nut','nuts','kokomi','kokoseggs','kokosimp','kokomi simp','keikoseggs',
'astro','astroworld','astronomy','nomy','elisa sinclair','egirl','egirl invasion','yoimiya','yoimiya dick sucker','astrology','oomfie',
'implicit none','implicit','explicit all','explicit','herrscher of none','venezuela','miquel','miquelvzla','billionare',
'kaslanass','kaslantits','kaslanas ass','kimaya','ayamik','ayaka milk',
'battle cats','battle cats guy','kingepic','herrscher of battle cats','quiet','quietmoment','moment cult',
'mommy','benji','mommy benji','sword through head','benji x astro','herrscher of friendship','herrscher of hate',
'elec','elecwizer','maso','masoscist','zen','amber','amber mains','baron bunny',
'anemo','pyro','electro','dendro','geo','hydro','cryo','fire','water','grass','ice','rock','abyssmal','celestial','glitched',
'mondstadt','liyue','inazuma','sumeru','fontaine','natlan','snezhnaya','celestia',
'brick','herrscher of simping','char','herrscher of events','master of tournaments',
'sideways','sidewaysdude','yae miko simp','raiden simp','raiden','yae','yae miko','raiden shogun','raiden ei','ganyu simp','cocogoat','cocogoat milk',
'master of coin','coast','mona','grand maester','exesa','sexesa','erosion','seggs','miku',
'jaydon','herrscher of nothing','winter','hubble','hubble telescope','floor','floofy','floorfy','father come home',
'collei','coleu bot','hu tao','hu tao bot','hu tao simp','sentient','sentient bot','carl','karl','carl bot','turtle bot','steam the turtle',
'steam the crab','maryland','maryland crab','gacha','gacha alliance','gacha games','honkai','honkai impact','genshin','genshin impact','genshrek','genshit','sexshrek',
'allies','alliance representatives','united gacha hub','osu','osuplace','blue archive','project sekai','polandball gacha','fate grand order',
'ubatcha','uncle uba','venfei under ubatcha','btmc','hime','rplace','placing pixels','pixels',
]
let connected = 0;
var gameData = [];
var charactersData = [];
setTimeout(function(){
  readData();
},1000)
var acc = [];
jquery.getJSON("../characters.json?1", function(json) {
  charactersData = json;
});


webSocketServer.on('connection', function (webSocket) {
  // a random 6dig ID (not sauce) is given to the client per connection. yea it's not a good idea to use a do while loop like this, don't kill me
  do{
    var userID = Math.floor(Math.random() * 1000000)
    console.log(userID)
  }while(webSockets[userID]!=undefined)
  webSockets[userID] = webSocket
  connected++;
  console.log('NEW CONNECTION - ID (not sauce):' + userID + ' , Total connections:' + connected)

  // messages are in the form of 'type~arg1~arg2~...', such as 'login~[insert username]~[insert password]' or 'upgrade~akagi'
  webSocket.on('message', function(message) {
    message = message + ''
    console.log('received from ' + userID + ': ' + message)
    let cutMessage = message.split('~')
    switch(cutMessage[0]){
        case 'test':
            webSocket.send(message);
            console.log('sent to ' + userID +': ' + message)
            return;
        case 'broadcast':
            broadcast(message);
            return;
        case 'signup':
            for(var i=0;i<gameData.length;i++){
              if(gameData[i].username==cutMessage[1]){
                  webSocket.send('signuperror');
                  console.log('sent to ' + userID +': signuperror')
                return;
              }
            }
            gameData[gameData.length] = {username:cutMessage[1],password:cutMessage[2],level:1,coin:1000,plutonium:100,regularFate:0,goldenFate:0,regularPulls:0,goldenPulls:0,characters:[{id:103,level:1,XP:0,reqXP:100,ascension:0,HP:{upgradeMulti:1,ascensionMulti:1,equipmentMulti:[1,1,1,1,1,1],degenMulti:1,exMulti:1,final:900},ATK:{upgradeMulti:1,ascensionMulti:1,equipmentMulti:[1,1,1,1,1,1],degenMulti:1,exMulti:1,final:150},DEF:{upgradeMulti:1,ascensionMulti:1,equipmentMulti:[1,1,1,1,1,1],degenMulti:1,exMulti:1,final:75},CrateE:{upgradeMulti:1,ascensionMulti:1,equipmentMulti:[1,1,1,1,1,1],degenMulti:1,exMulti:1,final:0.1},CdmgE:{upgradeMulti:1,ascensionMulti:1,equipmentMulti:[1,1,1,1,1,1],degenMulti:1,exMulti:1,final:0.5},CrateQ:{upgradeMulti:1,ascensionMulti:1,equipmentMulti:[1,1,1,1,1,1],degenMulti:1,exMulti:1,final:0.1},CdmgQ:{upgradeMulti:1,ascensionMulti:1,equipmentMulti:[1,1,1,1,1,1],degenMulti:1,exMulti:1,final:0.5},power:1530,equipments:[-1,-1,-1,-1,-1,-1],degenlevel:0}],team:[0,-1,-1,-1,-1,-1],orb:[0,0,0,0,0,0,0,0,0]}
            webSocket.send('signupsuccess');
            console.log('sent to ' + userID +': signupsuccess')
            saveData(gameData);
            return;
        case 'login':
          for(var i=0;i<gameData.length;i++){
            if(gameData[i].username==cutMessage[1]){
                if(gameData[i].password==cutMessage[2]){
                  var UID = i;
                  webSocket.send('loginsuccess~' + JSON.stringify(gameData[UID]));
                  console.log('sent to ' + userID +': loginsuccess~' + JSON.stringify(gameData[UID]))
                  console.log(userID + ' logged into account "' + cutMessage[1] +'" (UID:' + UID +')')
                  acc[userID] = i;
                }else{
                  webSocket.send('loginerror');
                  console.log('sent to ' + userID +': loginerror')
                }
                return;
            }
          }
          webSocket.send('loginerror');
          console.log('sent to ' + userID +': loginerror')
          return;
        case 'chat':
          broadcast('chat~' + gameData[acc[userID]].username + ' (' + gameData[acc[userID]].level + '): ~' + cutMessage[1])
          return;
        case 'ping':
          webSocket.send('pong')
          console.log('sent to ' + userID +': pong')
          return;
        default:
            webSocket.send('what the hell happened?')
            console.log('sent to ' + userID +': ' + 'what the hell happened?')
            return;
    }
  })

  webSocket.on('close', function () {
    acc[userID] = null;
    delete webSockets[userID]
    connected--;
    console.log('CLOSED CONNECTION - ID (not sauce):' + userID + ' , Total connections left:' + connected)
  })
})

// sends the message to everyone
function broadcast(data) { 
  webSocketServer.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(data);
    }
  });
  console.log('broadcasted to everyone: ' + data);
}

// save and load stuff in a json file... i feel like this is gonna go wrong
var fs = require('fs');

function saveData(data){
  fs.writeFile("data.json", JSON.stringify(data), function(err) {
      if(err) {
          return console.log(err);
      }
      console.log("saved: " + JSON.stringify(data));
  }); 
}
function readData(){
  fs.readFile('data.json', (err, data) => {
    if (err) throw err;
    let results = JSON.parse(data);
    console.log(results)
    gameData = results;
  });
}

