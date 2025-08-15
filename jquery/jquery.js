
$(function() {
    const $tableBody = $('#todoTable');
    const apiBase = 'http://localhost:8000';
  
    function renderTasks(tasks) {
      $tableBody.empty();
      tasks.forEach((item, index) => {
        const lines = item.todo.split('\n').filter(line => line.trim() !== '');
        const listHtml = lines.map(line => `<li>${line}</li>`).join('');
        const $row = $(`
          <tr>
            <th scope="row">${index + 1}</th>
            <td>${item.username}</td>
            <td><ul>${listHtml}</ul></td>
            <td>
              <button class="btn btn-danger btn-sm delete-btn" data-id="${item.id}">
                Delete
              </button>
            </td>
          </tr>
        `);
        $tableBody.append($row);
      });
    }
  
    function fetchTasks() {
      $.getJSON(`${apiBase}/tasks`, data => {
        renderTasks(data.tasks);
      });
    }
  
    function deleteTask(id) {
      $.ajax({
        url: `${apiBase}/delete/${id}`,
        method: 'DELETE',
        success: fetchTasks
      });
    }
  
    // Handle form submission
    $('#todoForm').on('submit', function(e) {
      e.preventDefault();
      const payload = {
        username: $('#username').val(),
        todo: $('#todos').val()
      };
      $.ajax({
        url: `${apiBase}/add`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: function() {
          fetchTasks();
          $('#todoForm')[0].reset();
        }
      });
    });
  
    // Delegate delete button clicks
    $tableBody.on('click', '.delete-btn', function() {
      const id = $(this).data('id');
      deleteTask(id);
    });
  
    // Initial load
    fetchTasks();
  });
  