const TODO_ID_PREFIX = "todo-"

function updateViewWithListItem(view, inputSpan, modelElement) {
    const li = document.createElement("li");
    li.id = `${TODO_ID_PREFIX}${modelElement.id}`;
    const text = document.createTextNode(modelElement.task);
    li.classList.add("list-group-item");
    li.append(text);
    view.insertBefore(li, inputSpan);
}

// UPDATE MODEL
function submitTask() {
    const taskInput = document.getElementById("task-input");
    const list = document.getElementById('task-list');
    const inputSpan = document.getElementById('task-input-span');
    const headers = new Headers();
    headers.append("Content-Type", "application/json");

    fetch('../api/todos/',
        {
            method: "POST",
            headers: headers,
            body: JSON.stringify({
                task: taskInput.value
            })
        }
    ).then(response => {
        // UPDATE VIEW
        if (response.status === 201) {
            response.json().then(
                json => {
                    updateViewWithListItem(list, inputSpan, json)
                }
            )
            taskInput.value = "";
        }
    });
}

// UPDATE VIEW
function setupTaskList() {
    console.log("Fetching task list")
    const list = document.getElementById('task-list');
    const inputSpan = document.getElementById('task-input-span');

    fetch('../api/todos').then(
        response => {
            if (response.status === 200) {
                response.json().then(
                    json => {
                        list.innerHtml = ''; // reset list of tasks
                        json.forEach(function (element) {
                            updateViewWithListItem(list, inputSpan, element)
                    });
                });
            }
    });


}

window.onload = function (){setupTaskList()};