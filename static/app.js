function updateViewWithListItem(view, modelElement) {
    const li = document.createElement("div");
    li.dataset.todo_id = modelElement.id;

    const text = document.createTextNode(modelElement.task);
    li.classList.add("list-group-item");
    li.append(text);
    view.append(li);
}

// UPDATE MODEL
function submitTask() {
    const taskInput = document.getElementById("task-input");
    const list = document.getElementById('task-list');
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
                    updateViewWithListItem(list, json)
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

    fetch('../api/todos').then(
        response => {
            if (response.status === 200) {
                response.json().then(
                    json => {
                        list.innerHtml = ''; // reset list of tasks
                        json.forEach(function (element) {
                            updateViewWithListItem(list, element)
                    });
                });
            }
    });


}

window.onload = function (){setupTaskList()};