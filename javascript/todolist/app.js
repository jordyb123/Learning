const form = document.getElementById("todo-form");
const input = document.getElementById("todo-input");
const list = document.getElementById("todo-list");
const taskCount = document.getElementById("task-count");

const STORAGE_KEY = "todo-items";

function saveTasks() {
    const items = Array.from(list.querySelectorAll("li")).map((li) => {
        const taskTextEl = li.querySelector(".task-text");
        return {
            text: taskTextEl.textContent,
            completed: taskTextEl.classList.contains("completed"),
        };
    });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

function loadTasks() {
    try {
        const data = localStorage.getItem(STORAGE_KEY);
        return data ? JSON.parse(data) : [];
    } catch {
        return [];
    }    
}

function updateTaskCount() {
    const allTasks = list.querySelectorAll("li");
    const completedTasks = list.querySelectorAll(".task-text.completed");
    const activeTasks = allTasks.length - completedTasks.length;

    taskCount.textContent = `${activeTasks} task${activeTasks !== 1 ? "s" : ""} left`;
}

function createTaskItem(text, completed = false) {
    const li = document.createElement("li");
    const taskText = document.createElement("span");
    taskText.textContent = text;
    taskText.classList.add("task-text");
    if (completed) taskText.classList.add("completed");

    // delete button
    const delbtn = document.createElement("button");
    delbtn.textContent = "Delete";
    delbtn.classList.add("delete-btn");
    delbtn.addEventListener("click", () => {
        li.remove();
        updateTaskCount();
        saveTasks();
    });

    // completed button

    const compbtn = document.createElement("button");
    compbtn.textContent = "Complete";
    compbtn.classList.add("comp-btn");
    compbtn.addEventListener("click", () => {
        taskText.classList.toggle("completed");
        updateTaskCount();
        saveTasks();
    });

    const editbtn = document.createElement("button");
    editbtn.textContent = "Edit";
    editbtn.classList.add("edit-btn");
    editbtn.addEventListener("click", () => {
        const updatedText = prompt("Edit task:", taskText.textContent);
        if (updatedText === null) return;

        const cleaned = updatedText.trim();
        if (cleaned === "") return;

        taskText.textContent = cleaned;
        saveTasks();
    });

    li.appendChild(taskText);
    li.appendChild(delbtn);
    li.appendChild(compbtn);
    li.appendChild(editbtn);
    list.appendChild(li);
    
}

form.addEventListener("submit", (event) => {
    event.preventDefault();

    const text = input.value.trim();
    if (text === "") return;

    createTaskItem(text, false);
    updateTaskCount();
    saveTasks();

    input.value = "";
    input.focus();
});

// load once at startup

loadTasks().forEach((item) => {
    createTaskItem(item.text, item.completed);
});

updateTaskCount(); 