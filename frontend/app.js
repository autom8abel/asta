// === ASTA Frontend Logic ===

const BASE_URL = "http://localhost:8000";
const USER_ID = 1;

const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");
const tasksTable = document.getElementById("tasksTable");
const logOutput = document.getElementById("logOutput");
const alertBox = document.getElementById("alertBox");

// Helper: Show alert messages
function showAlert(message, type = "success") {
  alertBox.textContent = message;
  alertBox.className = `mb-6 p-3 rounded-lg text-white ${
    type === "success" ? "bg-green-500" : "bg-red-500"
  }`;
  alertBox.classList.remove("hidden");

  // Auto-hide after 3s
  setTimeout(() => {
    alertBox.classList.add("hidden");
  }, 3000);
}

// Helper: Render tasks table
function renderTasks(tasks) {
  tasksTable.innerHTML = "";

  tasks.forEach((task) => {
    // Format due date
    let dueDateDisplay = "—";
    if (task.due_date) {
      const parsedDate = new Date(task.due_date);
      if (task.all_day) {
        dueDateDisplay = `${parsedDate.toLocaleDateString(undefined, {
          weekday: "long",
          month: "short",
          day: "numeric",
        })} (All Day)`;
      } else {
        dueDateDisplay = parsedDate.toLocaleString(undefined, {
          weekday: "long",
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        });
      }
    }

    // Status display
    const statusBadge =
      task.status === "completed"
        ? `<span class="px-2 py-1 bg-green-200 text-green-800 rounded-full text-sm">Completed</span>`
        : `<span class="px-2 py-1 bg-gray-200 text-gray-800 rounded-full text-sm">Pending</span>`;

    // Build row
    const row = document.createElement("tr");
    row.innerHTML = `
      <td class="px-4 py-2">${task.id}</td>
      <td class="px-4 py-2">${task.title}</td>
      <td class="px-4 py-2">${dueDateDisplay}</td>
      <td class="px-4 py-2">${statusBadge}</td>
      <td class="px-4 py-2">
        ${
          task.status === "pending"
            ? `<button class="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600 mr-2"
                onclick="completeTask(${task.id})">Complete</button>`
            : ""
        }
        <button class="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
          onclick="deleteTask(${task.id})">Delete</button>
      </td>
    `;
    tasksTable.appendChild(row);
  });
}

// Helper: Render log
function renderLog(log) {
  if (!log) {
    logOutput.textContent = "No log yet.";
    return;
  }
  logOutput.textContent = `[${log.event_type}] ${log.content}`;
}

// Fetch tasks for current user
async function loadTasks() {
  try {
    const res = await fetch(`${BASE_URL}/users/${USER_ID}/tasks`);
    if (!res.ok) throw new Error("Failed to fetch tasks");
    const tasks = await res.json();
    renderTasks(tasks);
  } catch (err) {
    console.error("Load tasks failed:", err);
    logOutput.textContent = "⚠️ Could not load tasks.";
  }
}

// Fetch last log for current user
async function loadLastLog() {
  try {
    const res = await fetch(`${BASE_URL}/users/${USER_ID}/logs?limit=1`);
    if (!res.ok) throw new Error("Failed to fetch logs");
    const logs = await res.json();
    renderLog(logs.length ? logs[0] : null);
  } catch (err) {
    console.error("Load log failed:", err);
    logOutput.textContent = "⚠️ Could not load log.";
  }
}

// Send user input to backend
async function sendCommand() {
  const text = userInput.value.trim();
  if (!text) return;

  try {
    const res = await fetch(`${BASE_URL}/nlp/act`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: USER_ID, text }),
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error("Error:", errorText);
      logOutput.textContent = `Error: ${errorText}`;
      showAlert("❌ Failed to process command", "error");
      return;
    }

    const data = await res.json();

    // Update UI
    renderTasks(data.tasks || []);
    renderLog(data.log);

    // Success alert
    showAlert("✅ Command processed successfully", "success");

    // Clear input
    userInput.value = "";
  } catch (err) {
    console.error("Request failed:", err);
    logOutput.textContent = "Request failed. Is backend running?";
    showAlert("⚠️ Request failed. Check backend.", "error");
  }
}

function completeTask(taskId) {
  fetch(`${BASE_URL}/tasks/${taskId}/complete`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
  })
    .then((res) => {
      if (!res.ok) throw new Error("Failed to complete task");
      return res.json();
    })
    .then((data) => {
      showAlert(`Task "${data.title}" marked as completed`, "success");
      loadTasks(); // refresh list
      loadLastLog(); // refresh logs
    })
    .catch((err) => {
      console.error("Error completing task:", err);
      showAlert("Error completing task", "error");
    });
}

// Delete a task
async function deleteTask(taskId) {
  try {
    const res = await fetch(`${BASE_URL}/nlp/act`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: USER_ID, text: `delete task ${taskId}` }),
    });

    const data = await res.json();
    renderTasks(data.tasks || []);
    renderLog(data.log);

    // Success alert for delete
    showAlert(`🗑️ Task ${taskId} deleted`, "success");
  } catch (err) {
    console.error("Delete failed:", err);
    showAlert("❌ Failed to delete task", "error");
  }
}

// Event listeners
sendBtn.addEventListener("click", sendCommand);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendCommand();
});

// Auto-load tasks and logs on page open
window.addEventListener("DOMContentLoaded", () => {
  loadTasks();
  loadLastLog();
});
