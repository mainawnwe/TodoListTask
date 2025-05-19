document.addEventListener('DOMContentLoaded', function() {
  // Create notification container if not exists
  let container = document.getElementById('notification-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'notification-container';
    document.body.appendChild(container);
  }

  // Function to show notification
  function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;

    container.appendChild(notification);

    // Hide after 5 seconds
    setTimeout(() => {
      notification.classList.add('hide');
      setTimeout(() => {
        container.removeChild(notification);
      }, 300);
    }, 5000);
  }

  // WebSocket connection for real-time notifications
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const wsUrl = `${protocol}://${window.location.host}/ws/notifications/`;
  const socket = new WebSocket(wsUrl);

  socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.message) {
      showNotification(data.message);
    }
  };

  socket.onclose = function(e) {
    console.error('WebSocket closed unexpectedly');
  };

  // Poll the server every 30 seconds for new notifications (fallback)
  setInterval(() => {
    fetch('/notifications/check_new/')
      .then(response => response.json())
      .then(data => {
        if (data.new_notifications && data.new_notifications.length > 0) {
          data.new_notifications.forEach(notification => {
            showNotification(notification.message);
          });
        }
      })
      .catch(error => console.error('Error fetching notifications:', error));
  }, 30000);
});
