// === ASTA Frontend Logic ===

// Adjust this if your backend runs on a different host/port
const BASE_URL = "http://localhost:8000";

// DOM references
const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");
const tasksTable = document.getElementById("tasksTable");
const logOutput = document.getElementById("logOutput");

// Default user for MVP demo
const USER_ID = 1;

// Helper: Render tasks table
function renderTasks(tasks) {
  tasksTable.innerHTML = "";

  if (!tasks || tasks.length === 0) {
    tasksTable.innerHTML = `
      <tr><td colspan="4" class="px-4 py-2 text-gray-500">No tasks yet</td></tr>
    `;
    return;
  }

  tasks.forEach((task) => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td class="px-4 py-2">${task.id}</td>
      <td class="px-4 py-2">${task.title}</td>
      <td class="px-4 py-2">${task.due_date || "—"}</td>
      <td class="px-4 py-2">
        <button
          onclick="deleteTask(${task.id})"
          class="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
        >
          Delete
        </button>
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
      return;
    }

    const data = await res.json();

    // Update UI
    renderTasks(data.tasks || []);
    renderLog(data.log);

    // Clear input
    userInput.value = "";
  } catch (err) {
    console.error("Request failed:", err);
    logOutput.textContent = "Request failed. Is backend running?";
  }
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
  } catch (err) {
    console.error("Delete failed:", err);
  }
}

// Event listeners
sendBtn.addEventListener("click", sendCommand);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendCommand();
});
