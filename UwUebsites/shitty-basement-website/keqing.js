var spinPerSec = 0.1
var smugPerSpin = 1
var smugPerSec = 0.1
var smug = 0
var spinPerSecMulti = 1
const suffix = ['K','M','B','T','Qa','Qi','Sx','Sp','Oc','No','De','UD','DD','TD','QaD','QiD','SxD','SpD','OcD','NoD','Vi','UV','DV','TV','QaV','QiV','SxV','SpV','OcV','NoV','Tg']

function d(id){
    return document.getElementById(id)
}

function toText(num,int){
    if(num>=1){
        digits = Math.floor(Math.log10(num)) + 1;
        if(digits<=5){
            if(int){
                return num.toPrecision(digits);
            }else{
                return num.toPrecision(digits + 1);
            }
        }else{
            suffixlevel = Math.floor((digits - 1)/3);
            num = num / 10**(suffixlevel*3);
            digits = Math.floor(Math.log10(num)) + 1;
            return num.toPrecision(digits + 3) + ' ' + suffix[suffixlevel - 1];
        }
    }else{
        if(int){
            return Math.round(num);
        }else{
            return num.toPrecision(1);
        }
    }
}

function tick(){
    smug += smugPerSec/10
    update()
}

function update(){
    var a = 0;
    items.forEach((item) => {item.update(); a+=item.totalSpinPerSec });
    spinPerSec = a + 0.1;

    smugPerSec = spinPerSec * smugPerSpin

    d('smug').style.animationDuration = `${1/spinPerSec}s`

    d('spinPerSecCount').innerHTML = `Spins per second: ${toText(spinPerSec,false)}`
    d('smugPerSpinCount').innerHTML = `Smugs per spin: ${toText(smugPerSpin,false)}`
    d('smugCount').innerHTML = `Smugs: ${toText(smug,false)}`
}

class item{
    amount = 0
    multi = 1
    eachSpinPerSec = 0
    totalSpinPerSec = 0
    totalCost = 0

    constructor(name,rawSpinPerSec,rawCost,id){
        this.rawSpinPerSec = rawSpinPerSec
        this.rawCost = rawCost
        this.name = name
        this.id = id
    }

    update(){
        this.eachSpinPerSec = this.rawSpinPerSec * this.multi * spinPerSecMulti
        this.totalSpinPerSec = this.eachSpinPerSec * this.amount
        this.totalCost = this.rawCost * (1.2**this.amount)
        d(`c${this.id}`).innerHTML = `Cost: ${toText(this.totalCost,false)}`
        d(`sps${this.id}`).innerHTML = `Spins Per Second: ${toText(this.eachSpinPerSec,false)}`
        d(`tsps${this.id}`).innerHTML = `Total Spins Per Second: ${toText(this.totalSpinPerSec,false)}`
    }

    buy(){
        if(smug>=this.totalCost){
            smug -= this.totalCost
            this.amount++
            return true
        }else{
            return false
        }
    }
}

items = [new item('yanfei',0.1,1,0), new item('herta',1,10,1), new item('motor',8,120,2), new item('turbine',32,1600,3), new item('typhoon',128,24000,4), new item('hurricane',500,400000,5), new item('vortex',2000,8e6,6), new item('spiral galaxy',8888,160e6,7), new item('pulsar',27777,3.33e9,8), new item('black hole',77777,66.6e9,9)]

setInterval(tick,100)