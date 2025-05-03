document.addEventListener('DOMContentLoaded', function() {
  const taskList = document.getElementById('task-list');

  let dragSrcEl = null;

  function handleDragStart(e) {
    dragSrcEl = this;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.outerHTML);
    this.classList.add('dragElem');
  }

  function handleDragOver(e) {
    if (e.preventDefault) {
      e.preventDefault();
    }
    this.classList.add('over');
    e.dataTransfer.dropEffect = 'move';
    return false;
  }

  function handleDragEnter(e) {
    // this / e.target is the current hover target.
  }

  function handleDragLeave(e) {
    this.classList.remove('over');
  }

  function handleDrop(e) {
    if (e.stopPropagation) {
      e.stopPropagation(); // stops the browser from redirecting.
    }

    if (dragSrcEl != this) {
      this.parentNode.removeChild(dragSrcEl);
      const dropHTML = e.dataTransfer.getData('text/html');
      this.insertAdjacentHTML('beforebegin', dropHTML);
      const dropElem = this.previousSibling;
      addDnDHandlers(dropElem);
      sendNewOrderToServer();
    }
    this.classList.remove('over');
    return false;
  }

  function handleDragEnd(e) {
    const items = document.querySelectorAll('#task-list .task-item');
    items.forEach(function(item) {
      item.classList.remove('over');
      item.classList.remove('dragElem');
    });
  }

  function addDnDHandlers(elem) {
    elem.addEventListener('dragstart', handleDragStart, false);
    elem.addEventListener('dragenter', handleDragEnter, false);
    elem.addEventListener('dragover', handleDragOver, false);
    elem.addEventListener('dragleave', handleDragLeave, false);
    elem.addEventListener('drop', handleDrop, false);
    elem.addEventListener('dragend', handleDragEnd, false);
  }

  function sendNewOrderToServer() {
    const items = document.querySelectorAll('#task-list .task-item');
    const orderedTaskIds = Array.from(items).map(item => item.querySelector('input.task-completed-checkbox').getAttribute('data-task-id'));

    fetch('/reorder_tasks/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ ordered_task_ids: orderedTaskIds }),
    })
    .then(response => response.json())
    .then(data => {
      if (!data.success) {
        alert('Failed to save new task order: ' + data.error);
      }
    })
    .catch(error => {
      alert('Error saving new task order.');
    });
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const items = document.querySelectorAll('#task-list .task-item');
  items.forEach(function(item) {
    item.setAttribute('draggable', 'true');
    addDnDHandlers(item);
  });
});
