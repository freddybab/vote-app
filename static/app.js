function getStarIcon(isFav) {
    if (isFav) {
        return "bi-star-fill"
    } else {
        return "bi-star"
    }
}


function deleteTask(taskId) {
    const taskElement = document.querySelectorAll(`[data-task-id="${taskId}"]`)[0];

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

function updateStarred(taskId, oldValue) {
    // Update Model
    fetch(`../api/todos/${taskId}`,
    {
        method: "PUT",
        headers: new Headers({"Content-Type": "application/json"}),
        body: JSON.stringify({
            starred: !oldValue
        })
    }).then(
        response => {
            if (response.status == 200) {
                // Update success, update View:
                refreshTaskList(); // YOLO    
            }
        }
    )
}


function updateViewWithListItem(modelElement) {
    const list = document.getElementById('task-list');
    updateViewWithListItem(list, modelElement);
}

function updateDone(taskId, oldValue) {
     // Update Model
     fetch(`../api/todos/${taskId}`,
     {
         method: "PUT",
         headers: new Headers({"Content-Type": "application/json"}),
         body: JSON.stringify({
             done: !oldValue
         })
     }).then(
         response => {
             if (response.status == 200) {
                 // Update success, update View:
                 refreshTaskList(); // YOLO    
             }
         }
     )

}

function getTextClass(element) {
    let classes = "";
    if (element.done) {
        classes += "text-muted";
    }

    return classes;
}


function updateViewWithListItem(view, modelElement) {


    view.innerHTML += 
    `
    <div class="list-group-item d-flex flex-row justify-content-between" id="task-${modelElement.id}" data-task-id="${modelElement.id}" data-task-text="${modelElement.task}">
        <div>
            <p class="${getTextClass(modelElement)}">${modelElement.task}</p>
        </div>
        <div>
            <button class="btn" onclick="updateDone(${modelElement.id}, ${modelElement.done})"><i class="bi bi-check-circle"></i> </button>
        </div>

        <div>
            <button class="btn" type="button" onclick="updateStarred(${modelElement.id}, ${modelElement.fav})"><i class="bi ${getStarIcon(modelElement.fav)}"></i></button>
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

    fetch('../api/todos/',
        {
            method: "POST",
            headers: new Headers({"Content-Type": "application/json"}),
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
function refreshTaskList() {
    console.log("Fetching task list")
    const list = document.getElementById('task-list');
    const doneList = document.getElementById('done-list');

    fetch('../api/todos').then(
        response => {
            if (response.status === 200) {
                response.json().then(
                    json => {
                        list.innerHTML = ''; // reset list of tasks
                        doneList.innerHTML = '';
                        json.forEach(function (element) {
                            if (element.done) {
                                console.log("element done", element.id);
                                updateViewWithListItem(doneList, element);
                            } else {
                                console.log("element not done", element.id);
                                updateViewWithListItem(list, element)
                            }
                    });
                });
            }
    });


}

window.onload = function (){refreshTaskList()};