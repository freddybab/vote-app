function deleteTask(taskId) {
    taskElement = document.querySelectorAll(`[data-task-id="${taskId}"]`)[0];

    // Update Model
    fetch(`../api/todos/${taskId}`,
    {
        method: "DELETE"
    }).then(
        response => {
            if (response.status == 204) {
                // Delete success, update view:
                taskElement.remove();
            }
        }
    )

}


function updateViewWithListItem(view, modelElement) {
    view.innerHTML += 
    `
    <div class="list-group-item d-flex flex-row justify-content-between" data-task-id="${modelElement.id}">
        <div>
            <p>${modelElement.task}</p>
        </div>
        <div>
            <button class="btn" type="button" onclick="deleteTask(${modelElement.id})"><i class="bi bi-trash3"></i></button>
        </div>
    </div>
    `
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