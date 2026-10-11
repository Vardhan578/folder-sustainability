/**
 * ===================================================
 * SMART STUDY PLANNER - JAVASCRIPT
 * Handles task management, local storage, validation,
 * and user interactions in vanilla JavaScript.
 * ===================================================
 */

// Local Storage Key
const STORAGE_KEY = 'smart_study_planner_tasks';

// DOM Elements
const taskForm = document.getElementById('taskForm');
const taskInput = document.getElementById('taskInput');
const timeInput = document.getElementById('timeInput');
const formError = document.getElementById('formError');
const errorMessage = document.getElementById('errorMessage');

const taskList = document.getElementById('taskList');
const emptyState = document.getElementById('emptyState');
const listBadge = document.getElementById('listBadge');

const totalTasksEl = document.getElementById('totalTasks');
const completedTasksEl = document.getElementById('completedTasks');
const remainingTasksEl = document.getElementById('remainingTasks');

// In-memory state of tasks
let tasks = [];

/**
 * Initialize application: Load saved data and render initial view
 */
function init() {
  loadTasksFromStorage();
  render();
  setupEventListeners();
}

/**
 * Load tasks from the browser's localStorage
 */
function loadTasksFromStorage() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    tasks = saved ? JSON.parse(saved) : [];
  } catch (error) {
    console.error('Failed to load tasks from localStorage:', error);
    tasks = [];
  }
}

/**
 * Persist current tasks to localStorage
 */
function saveTasksToStorage() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  } catch (error) {
    console.error('Failed to save tasks to localStorage:', error);
  }
}

/**
 * Show error banner with a custom message
 * @param {string} message 
 */
function showError(message) {
  errorMessage.textContent = message;
  formError.classList.remove('hidden');
}

/**
 * Hide the error banner
 */
function hideError() {
  formError.classList.add('hidden');
  errorMessage.textContent = '';
}

/**
 * Escape HTML to prevent cross-site scripting (XSS)
 * @param {string} str 
 * @returns {string} Safe escaped string
 */
function escapeHTML(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/**
 * Add a new task after validation
 */
function handleAddTask(event) {
  event.preventDefault();

  const title = taskInput.value.trim();
  const timeValue = timeInput.value.trim();
  const minutes = parseInt(timeValue, 10);

  // Validation 1: Check for empty task title
  if (!title) {
    showError('Please enter a study task or subject name.');
    taskInput.focus();
    return;
  }

  // Validation 2: Check for valid study time in minutes
  if (!timeValue || isNaN(minutes) || minutes <= 0) {
    showError('Please enter a valid study time (greater than 0 minutes).');
    timeInput.focus();
    return;
  }

  // Validation 3: Prevent unrealistically huge numbers (limit: 1440 min = 24 hrs)
  if (minutes > 1440) {
    showError('Study time cannot exceed 1,440 minutes (24 hours).');
    timeInput.focus();
    return;
  }

  // Valid input: hide any error
  hideError();

  // Create new task object
  const newTask = {
    id: 'task_' + Date.now(),
    title: title,
    minutes: minutes,
    completed: false,
    createdAt: new Date().toISOString()
  };

  // Add task to array (newest first)
  tasks.unshift(newTask);

  // Save & update display
  saveTasksToStorage();
  render();

  // Reset input fields
  taskInput.value = '';
  timeInput.value = '';
  taskInput.focus();
}

/**
 * Toggle the completed status of a task
 * @param {string} taskId 
 */
function toggleTaskCompletion(taskId) {
  const task = tasks.find(t => t.id === taskId);
  if (task) {
    task.completed = !task.completed;
    saveTasksToStorage();
    render();
  }
}

/**
 * Delete a task by ID
 * @param {string} taskId 
 */
function deleteTask(taskId) {
  tasks = tasks.filter(t => t.id !== taskId);
  saveTasksToStorage();
  render();
}

/**
 * Update the statistical counters and list badge
 */
function updateStats() {
  const total = tasks.length;
  const completed = tasks.filter(t => t.completed).length;
  const remaining = total - completed;

  totalTasksEl.textContent = total;
  completedTasksEl.textContent = completed;
  remainingTasksEl.textContent = remaining;

  listBadge.textContent = total === 1 ? '1 task listed' : `${total} tasks listed`;
}

/**
 * Render the entire list and empty state
 */
function render() {
  // Update statistical numbers
  updateStats();

  // Handle empty state visibility
  if (tasks.length === 0) {
    emptyState.classList.remove('hidden');
    taskList.innerHTML = '';
    return;
  }

  emptyState.classList.add('hidden');

  // Build task items HTML
  const itemsHTML = tasks.map(task => {
    const isCompleted = task.completed ? 'completed' : '';
    const isChecked = task.completed ? 'checked' : '';
    const safeTitle = escapeHTML(task.title);

    return `
      <li class="task-item ${isCompleted}" data-id="${task.id}">
        <label class="task-checkbox-label" title="${task.completed ? 'Mark uncompleted' : 'Mark completed'}">
          <input 
            type="checkbox" 
            class="task-checkbox" 
            data-action="toggle" 
            ${isChecked}
            aria-label="Mark ${safeTitle} as completed"
          >
        </label>
        
        <div class="task-content">
          <span class="task-title">${safeTitle}</span>
          <div class="task-meta">
            <span class="time-badge">⏱️ ${task.minutes} min</span>
          </div>
        </div>

        <button 
          type="button" 
          class="delete-btn" 
          data-action="delete" 
          title="Delete task" 
          aria-label="Delete task: ${safeTitle}"
        >
          🗑️
        </button>
      </li>
    `;
  }).join('');

  taskList.innerHTML = itemsHTML;
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
  // Form submission
  taskForm.addEventListener('submit', handleAddTask);

  // Clear error message on typing
  taskInput.addEventListener('input', () => {
    if (!formError.classList.contains('hidden')) hideError();
  });

  timeInput.addEventListener('input', () => {
    if (!formError.classList.contains('hidden')) hideError();
  });

  // Checkbox toggle via 'change' event (handles clicks, labels, and keyboard Space)
  taskList.addEventListener('change', (event) => {
    if (event.target.classList.contains('task-checkbox')) {
      const taskItem = event.target.closest('.task-item');
      if (taskItem) {
        toggleTaskCompletion(taskItem.dataset.id);
      }
    }
  });

  // Delete button click via event delegation
  taskList.addEventListener('click', (event) => {
    const deleteBtn = event.target.closest('.delete-btn');
    if (deleteBtn) {
      const taskItem = deleteBtn.closest('.task-item');
      if (taskItem) {
        deleteTask(taskItem.dataset.id);
      }
    }
  });
}

// Start application once DOM is fully loaded
document.addEventListener('DOMContentLoaded', init);
