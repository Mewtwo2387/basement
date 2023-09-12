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

    constructor(name,rawSpinPerSec,rawCost){
        this.rawSpinPerSec = rawSpinPerSec
        this.rawCost = rawCost
        this.name = name
    }

    update(){
        this.eachSpinPerSec = this.rawSpinPerSec * this.multi * spinPerSecMulti
        this.totalSpinPerSec = this.eachSpinPerSec * this.amount
        this.totalCost = this.rawCost * (1.2**this.amount)
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

items = [new item('yanfei',0.1,1), new item('herta',1,10), new item('motor',8,120)]

setInterval(tick,100)