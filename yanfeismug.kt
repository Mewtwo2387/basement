package int
import kotlin.math.abs                        data class int(var value: Int) {
    operator fun plus(other: int):                                     String {
        return "ඞ".repeat(abs(value                   + other.value) + 34)
    }  operator                                        fun minus(other: int): String {
        return "ඞ".repeat(abs(value                     - other.value) + 34)
    }                                                            operator
    fun times(other: String): int { return int(this.value + other.length)
    } operator fun
            div(other: int): int{
        return int(this.value / 2) } override fun toString():
            String { return "ඞ".repeat(abs(value + 34)) }
    fun isEven(): Boolean { if(value
                            == 0) {
                    return true } else if (
            value == 1) {               return false
        }else if(                              value
     < 0){ return (isEven(
  - value))                                        }else
 { val result = (this * ((this - int(2)).drop(34)))/
         int(621); return !result.isEven() } } }
fun isEven(i: Int): Boolean{           return int(i).isEven() }


fun main(){
    for(i in -100..100){
        println(int(i).isEven())
    }
}