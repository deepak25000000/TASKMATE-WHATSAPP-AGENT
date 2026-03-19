/**
 * TaskMate AI - Dashboard Application Script
 * Handles API communication, chat simulator, and dynamic UI rendering.
 */

const API_BASE = window.location.origin;
const AUTO_REFRESH_INTERVAL = 15000; // 15 seconds

// ─── State ────────────────────────────────────────────────
let isLoading = false;
let refreshTimer = null;
let selectedUserPhone = null;

// ─── Initialization ───────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadAllData();
    startAutoRefresh();

    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadAllData();
    });
});

// ─── Auto Refresh ─────────────────────────────────────────
function startAutoRefresh() {
    refreshTimer = setInterval(loadAllData, AUTO_REFRESH_INTERVAL);
}

// ─── Load All Data ────────────────────────────────────────
async function loadAllData() {
    try {
        await Promise.all([
            loadStats(),
            loadUsers(),
            loadActivity()
        ]);
        if (selectedUserPhone) {
            await loadUserDetails(selectedUserPhone);
        }
    } catch (err) {
        console.error('Error loading data:', err);
    }
}

// ─── Stats ────────────────────────────────────────────────
async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/api/stats`);
        const stats = await res.json();

        animateCounter('statUsers', stats.total_users);
        animateCounter('statMessages', stats.total_messages);
        animateCounter('statReminders', stats.active_reminders);
        animateCounter('statTasks', stats.pending_tasks);
        animateCounter('statCompleted', stats.completed_tasks);
        animateCounter('statActions', stats.total_agent_actions);
    } catch (err) {
        console.error('Stats error:', err);
    }
}

function animateCounter(elementId, targetValue) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const current = parseInt(el.textContent) || 0;
    if (current === targetValue) return;

    const duration = 600;
    const steps = 20;
    const increment = (targetValue - current) / steps;
    let step = 0;

    const timer = setInterval(() => {
        step++;
        if (step >= steps) {
            el.textContent = targetValue;
            clearInterval(timer);
        } else {
            el.textContent = Math.round(current + increment * step);
        }
    }, duration / steps);
}

// ─── Users & User Details ─────────────────────────────────
async function loadUsers() {
    try {
        const res = await fetch(`${API_BASE}/api/users`);
        const users = await res.json();

        const container = document.getElementById('usersList');
        document.getElementById('usersCount').textContent = `${users.length} users`;

        if (users.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No users registered yet.</p></div>';
            return;
        }

        container.innerHTML = users.map(u => `
            <div class="list-item user-list-item ${selectedUserPhone === u.phone_number ? 'active' : ''}" onclick="selectUser('${u.phone_number}')">
                <div class="list-item-icon">👤</div>
                <div class="list-item-content">
                    <div class="list-item-title">${u.name || maskPhone(u.phone_number)}</div>
                    <div class="list-item-detail">Active: ${timeAgo(u.last_active)}</div>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error('Users error:', err);
    }
}

async function selectUser(phone) {
    if (selectedUserPhone === phone) return;
    selectedUserPhone = phone;
    document.getElementById('instructionPanel').style.display = 'none';
    document.getElementById('userDetailsCard').style.display = 'block';

    // Update active class visually instantly
    document.querySelectorAll('.user-list-item').forEach(el => el.classList.remove('active'));
    event.currentTarget.classList.add('active');

    await loadUserDetails(phone);
}

async function loadUserDetails(phone) {
    try {
        const res = await fetch(`${API_BASE}/api/users`);
        const users = await res.json();
        const user = users.find(u => u.phone_number === phone);

        if (user) {
            document.getElementById('detailUserPhone').textContent = maskPhone(phone);
            document.getElementById('detailUserLastActive').textContent = `Last active: ${timeAgo(user.last_active)}`;

            document.getElementById('userAttributes').innerHTML = `
                <div class="attr-box">
                    <div class="attr-label">Phone Identity</div>
                    <div class="attr-value">${user.phone_number}</div>
                </div>
                <div class="attr-box">
                    <div class="attr-label">Name Identified</div>
                    <div class="attr-value">${user.name || 'Not Provided'}</div>
                </div>
                <div class="attr-box">
                    <div class="attr-label">Account Created</div>
                    <div class="attr-value">${formatDate(user.created_at)}</div>
                </div>
                <div class="attr-box">
                    <div class="attr-label">Total Engagements</div>
                    <div class="attr-value" id="detailChatCount">...</div>
                </div>
            `;
        }

        // Convs
        const convRes = await fetch(`${API_BASE}/api/conversations?user_phone=${encodeURIComponent(phone)}&limit=100`);
        const convs = await convRes.json();
        const chatContainer = document.getElementById('detailChatMessages');
        document.getElementById('detailChatCount').textContent = convs.length;

        if (convs.length === 0) {
            chatContainer.innerHTML = '<div class="empty-state"><p>No messages in history.</p></div>';
        } else {
            chatContainer.innerHTML = convs.map(conv => `
                <div class="chat-bubble ${conv.role === 'user' ? 'user' : 'bot'}">
                    <div class="bubble-content">${formatMessage(conv.content)}</div>
                    <span class="bubble-time">${formatDate(conv.timestamp)}</span>
                    ${conv.intent && conv.role === 'user' ? `<span class="bubble-intent">${conv.intent}</span>` : ''}
                </div>
            `).join('');
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Tasks
        const tasksRes = await fetch(`${API_BASE}/api/tasks?user_phone=${encodeURIComponent(phone)}`);
        const tasks = await tasksRes.json();
        const tasksContainer = document.getElementById('detailTasksList');
        if (tasks.length === 0) {
            tasksContainer.innerHTML = '<div class="empty-state"><p>No active tasks.</p></div>';
        } else {
            tasksContainer.innerHTML = tasks.map(task => `
                <div class="list-item">
                    <div class="list-item-icon">${task.status === 'completed' ? '✅' : '📋'}</div>
                    <div class="list-item-content">
                        <div class="list-item-title" style="${task.status === 'completed' ? 'text-decoration: line-through;' : ''}">${escapeHtml(task.title)}</div>
                        <div class="list-item-detail"><span class="status-tag ${task.status === 'pending' ? 'status-pending' : 'status-completed'}">${task.status}</span> · Priority: ${task.priority}</div>
                    </div>
                </div>
            `).join('');
        }

        // Reminders
        const remRes = await fetch(`${API_BASE}/api/reminders?user_phone=${encodeURIComponent(phone)}`);
        const rems = await remRes.json();
        const remContainer = document.getElementById('detailRemindersList');
        if (rems.length === 0) {
            remContainer.innerHTML = '<div class="empty-state"><p>No active reminders.</p></div>';
        } else {
            remContainer.innerHTML = rems.map(rem => `
                <div class="list-item">
                    <div class="list-item-icon">⏰</div>
                    <div class="list-item-content">
                        <div class="list-item-title">${escapeHtml(rem.title)}</div>
                        <div class="list-item-detail"><span class="status-tag ${rem.status === 'pending' ? 'status-pending' : 'status-completed'}">${rem.status}</span> · ${formatDate(rem.remind_at)}</div>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error("Error loading user details", e);
    }
}

// ─── Agent Activity ───────────────────────────────────────
async function loadActivity() {
    try {
        const res = await fetch(`${API_BASE}/api/logs?limit=30`);
        const logs = await res.json();

        const container = document.getElementById('activityList');
        document.getElementById('activityCount').textContent = `${logs.length} actions`;

        if (logs.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No agent activity recorded yet.</p></div>';
            return;
        }

        const actionIcons = {
            'reminder_created': '⏰',
            'task_created': '📋',
            'task_completed': '✅',
            'intent_reminder': '🎯',
            'intent_task_create': '🎯',
            'intent_weather': '🌤️',
            'intent_summarize': '📝',
            'intent_greeting': '👋',
            'intent_help': '❓',
            'intent_general': '💬',
            'error': '❌'
        };

        container.innerHTML = logs.map(log => `
            <div class="activity-row">
                <div class="activity-icon">${actionIcons[log.action] || '⚡'}</div>
                <div class="activity-action">${formatAction(log.action)}</div>
                <div class="activity-details" title="${escapeHtml(log.details)}">${escapeHtml(log.details).substring(0, 50)}</div>
                <div class="activity-time">${timeAgo(log.timestamp)}</div>
            </div>
        `).join('');
    } catch (err) {
        console.error('Activity error:', err);
    }
}



// ─── Utility Functions ────────────────────────────────────
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatMessage(text) {
    if (!text) return '';
    // Bold markdown
    text = text.replace(/\*([^*]+)\*/g, '<strong>$1</strong>');
    // Strikethrough
    text = text.replace(/~~([^~]+)~~/g, '<del>$1</del>');
    // Italic (underscore)
    text = text.replace(/_([^_]+)_/g, '<em>$1</em>');
    // Line breaks
    text = text.replace(/\n/g, '<br>');
    return text;
}

function formatAction(action) {
    return action
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase())
        .replace('Intent ', '🎯 ')
        .replace('Sim ', '🧪 ');
}

function maskPhone(phone) {
    if (!phone) return 'Unknown';
    const clean = phone.replace('whatsapp:', '');
    if (clean.length > 6) {
        return clean.substring(0, 4) + '***' + clean.substring(clean.length - 3);
    }
    return clean;
}

function timeAgo(timestamp) {
    if (!timestamp) return '';
    const now = new Date();
    const past = new Date(timestamp);
    const diffMs = now - past;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHr = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHr / 24);

    if (diffSec < 60) return 'Just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHr < 24) return `${diffHr}h ago`;
    if (diffDay < 7) return `${diffDay}d ago`;
    return past.toLocaleDateString();
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
        const date = new Date(dateStr);
        return date.toLocaleString([], {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return dateStr;
    }
}
