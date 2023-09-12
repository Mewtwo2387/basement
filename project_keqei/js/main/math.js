function calculateCharacterPower(atk,def,hp,cvalE,atkE,accE,crateE,cdmgE,cvalQ,atkQ,accQ,crateQ,cdmgQ){
    let a = hp * Math.sqrt(def)
    let b = cvalE * atkE * atk * accE * (1 + crateE * cdmgE)
    let c = cvalQ * atkQ * atk * accQ * (1 + crateQ * cdmgQ)
    return Math.sqrt(a * (b/2 + c/2))
}

// I wrote this a long time ago when making a clicker game, I forgot how this works, but it does
// It converts a number into a form like "69.420 T"
// when 'decimal' is false, it will round off to the nearest integer, "12.34" will become "12". Note that decimals in "12.34K" will still be there as 12.34K is still an integer (12340). It's uses in cases like XP.
// when 'decimal' is true, it will round off to 1 d.p., "12.34" will become "12.3". These are for cases like crit rate and crit dmg.
// when shorten is true, it will use suffixes, when it's false it will use the word (not recommended)
const suffix = ['K','M','B','T','Qa','Qi','Sx','Sp','Oc','No','De','UD','DD','TD','QaD','QiD','SxD','SpD','OcD','NoD','Vi','UV','DV','TV','QaV','QiV','SxV','SpV','OcV','NoV','Tg']
const word = ['Thousand','Million','Billion','Trillion','Quadrillion','Quintillion','Sextillion','Septillion','Octillion','Nonillion','Decillion','Uundecillion','Duodecillion','Tredecillion','Quattourdecillion','Quindecillion','Sexdecillion','Septendecillion','Octodecillion','Novemdecillion','Vigintillion','Unvigintillion','Duovigintillion','Trevigintillion','Quattourvigintillion','Quinvigintillion','Sexvigintillion','Septenvigintillion','Octovigintillion','Novemvigintillion','Trigintillion']
function toText(num,decimal,shorten){
    if(shorten){
        suffixused = suffix;
    }else{
        suffixused = word;
    }
    if(num>=1){
        digits = Math.floor(Math.log10(num)) + 1;
        if(digits<=5){
            if(decimal){
                return num.toPrecision(digits + 1);
            }else{
                return num.toPrecision(digits);
            }
        }else{
            suffixlevel = Math.floor((digits - 1)/3);
            num = num / 10**(suffixlevel*3);
            digits = Math.floor(Math.log10(num)) + 1;
            return num.toPrecision(digits + 3) + ' ' + suffixused[suffixlevel - 1];
        }
    }else{
        if(decimal){
            return num.toPrecision(1);
        }else{
            return Math.round(num);
        }
    }
}