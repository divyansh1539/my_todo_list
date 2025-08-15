const form = document.querySelector("form");
const tableBody = document.getElementById("todoTable");

function fetchTasks() {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "http://localhost:8000/tasks", true);

    xhr.onload = function () {
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            tableBody.innerHTML = "";
            data.tasks.forEach((item, index) => {
                const todoLines = item.todo.split('\n');
                let todoHTML = "<ul>";
                todoLines.forEach(line => {
                    if (line.trim() !== "") todoHTML += `<li>${line}</li>`;
                });
                todoHTML += "</ul>";

                tableBody.innerHTML += `
                <tr>
                    <th scope="row">${index + 1}</th>
                    <td>${item.username}</td>
                    <td>${todoHTML}</td>
                    <td>
                        <button class="btn btn-danger btn-sm" data-id="${item.id}">Delete</button>
                    </td>
                </tr>`;
            });

            const deleteButtons = tableBody.querySelectorAll("button[data-id]");
            deleteButtons.forEach(btn => {
                btn.addEventListener("click", function () {
                    const id = this.getAttribute("data-id");
                    deleteTask(id);
                });
            });
        }
    };

    xhr.send();
}

function deleteTask(id) {
    const xhr = new XMLHttpRequest();
    xhr.open("DELETE", `http://localhost:8000/delete/${id}`, true);

    xhr.onload = function () {
        if (xhr.status === 200) {
            fetchTasks();
        }
    };

    xhr.send();
}
fetchTasks();

form.addEventListener("submit", function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const todo = document.getElementById("todos").value;

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "http://localhost:8000/add", true);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onload = function () {
        if (xhr.status === 200) {
            fetchTasks();
            form.reset();
        }
    };
    xhr.send(JSON.stringify({ username: username, todo: todo }));
});