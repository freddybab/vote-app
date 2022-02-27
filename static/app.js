function updateViewWithListItem(view, inputSpan, item) {
    const li = document.createElement("li");
    const text = document.createTextNode(item.task);
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
        response.json().then(
            json => {
                updateViewWithListItem(list, inputSpan, json)
            }
        )
    });
    taskInput.value = "";
}

// UPDATE VIEW
function setupTaskList() {
    console.log("Fetching task list")
    const list = document.getElementById('task-list');
    const inputSpan = document.getElementById('task-input-span');

    fetch('../api/todos').then(
        response => {
            response.json().then(
                json => {
                    list.innerHtml = ''; // reset list of tasks
                    json.forEach(function (element) {
                        updateViewWithListItem(list, inputSpan, element)
                });
            }
        )
    });


}

window.onload = function (){setupTaskList()};