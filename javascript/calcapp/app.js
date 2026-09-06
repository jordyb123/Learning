const display = document.getElementById("display");
const keypad = document.getElementById("keypad");

let firstNumber = "";
let operator = "";

let currentInput = "";

keypad.addEventListener("click", (event) => {
    const button = event.target;
    const action = button.dataset.action;
    const value = button.dataset.value;
    const op = button.dataset.op;

    if (button.tagName !== "BUTTON") return;

    if (value !== undefined) {
        currentInput += value;
        display.textContent = currentInput;
    }
    else if (op) {
        console.log(op);
        if (currentInput === "") return;
        firstNumber = currentInput;
        operator = op;
        currentInput = "";

        display.textContent = operator;
    }
    else if (action) {
        console.log(action);
        if (action === "clear") {
            currentInput = "";
            firstNumber = "";
            operator = "";
            display.textContent = "0";
        }

        if (action === "equals"){
            if (firstNumber === "") return;
            if (operator === "") return;
            if (currentInput === "") return;

            const a = Number(firstNumber);
            const b = Number(currentInput);
            let result;

            if (operator === "+") result = a + b;
            else if (operator === "-") result = a - b;
            else if (operator === "*") result = a * b;
            else if (operator === "/")  {
                if (b === 0){
                    display.textContent = "Cannot divide by 0";
                    currentInput = "";
                    firstNumber = "";
                    operator = "";
                    return;
                }
                result = a / b;
            }

            display.textContent = String(result);
            currentInput = String(result);
            firstNumber = "";
            operator = "";
        }
            

    }



})