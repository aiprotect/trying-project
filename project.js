const increseButton = document.querySelector('.counter_button--increase');
const decreseButton = document.querySelector('.counter_button--decrease');
const dispy_count = document.querySelector('.counter_value');
const reset_button = document.querySelector('.counter_reset-button');
const title_button = document.querySelector('.counter_title');


function fun_count(num, isincrese){
    const current_value = Number(dispy_count.textContent);
    let newValue;
    if(isincrese){
        if(current_value + num <= 30){
            dispy_count.textContent = current_value + num 
            if(current_value + num === 30){
                title_button.textContent = 'warning'
                dispy_count.classList.add('title-class')
                title_button.classList.add('counter_warning')
            }
        }
        }else{
            if(current_value - num >= 0){
                dispy_count.textContent = current_value - num


        }
    }
}


reset_button.addEventListener('click',function () {
    dispy_count.textContent = 0
    title_button.textContent = 'ghorbani counter'
    dispy_count.classList.remove('title-class')
    title_button.classList.remove('counter_warning')
})

const increse = () => {
    fun_count(3, true)
}
const decrease = () => {
    fun_count(3, false)
    dispy_count.classList.remove('title-class')
    title_button.classList.remove('counter_warning')
    title_button.textContent = 'ghorbani counter'

}
increseButton.addEventListener('click',increse)
decreseButton.addEventListener('click', decrease)
