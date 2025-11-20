/**
 * FILE: UI/modules/thread-manager/thread-manager-welcome.js
 * PURPOSE: Welcome system for ThreadManager
 * 
 * DEPENDENCIES:
 * - UI/modules/thread-manager/thread-manager-core.js (must load first)
 * 
 * EXPORTS:
 * - Extends window.ThreadManager with welcome methods
 * 
 * USED BY:
 * - UI/business-ai-platform-v2.html (main application)
 * 
 * RELATED FILES:
 * - UI/modules/thread-manager/thread-manager-core.js (core object)
 * 
 * NOTES:
 * - Handles welcome screen and initial user experience
 * - Updated module from previous version
 * 
 * LAST MODIFIED: 2025-11-20 - Initial file creation
 */

// Welcome system methods will be defined here
// Awaiting code paste from user



// ==================== THREAD MANAGER - WELCOME MODULE ====================
/**
 * Welcome System - Time-based greetings and rotating tips
 * Extracted from updated version - works great!
 */

window.ThreadManagerWelcome = {
    // Welcome message variations per time period
    welcomeVariations: {
        morning: [
            { title: "Good Morning!", subtitle: "Ready to tackle today's tasks? Start a new chat or continue where you left off.", icon: "fa-sun", color: "#fbbf24" },
            { title: "Rise & Shine!", subtitle: "A fresh day, fresh possibilities. What shall we build together today?", icon: "fa-sunrise", color: "#f59e0b" },
            { title: "Morning, Champion!", subtitle: "The early bird catches the worm! Let's make today productive.", icon: "fa-coffee", color: "#fb923c" },
            { title: "New Day, New Ideas!", subtitle: "Your morning boost is here. Ready to turn ideas into reality?", icon: "fa-lightbulb", color: "#fbbf24" },
            { title: "Start Strong!", subtitle: "Morning energy is the best energy. What's first on your agenda?", icon: "fa-bolt", color: "#facc15" }
        ],
        afternoon: [
            { title: "Good Afternoon!", subtitle: "Making great progress! Need help with anything? I'm here to assist.", icon: "fa-cloud-sun", color: "#60a5fa" },
            { title: "Midday Check-In!", subtitle: "Halfway through the day. Let's power through together!", icon: "fa-chart-line", color: "#3b82f6" },
            { title: "Afternoon Momentum!", subtitle: "Keep the energy flowing. What's next on your list?", icon: "fa-fire", color: "#6366f1" },
            { title: "Productive Afternoon!", subtitle: "The day's rhythm is strong. Let's maintain that momentum!", icon: "fa-rocket", color: "#60a5fa" },
            { title: "Power Hour!", subtitle: "Peak productivity time. Let's make the most of it together.", icon: "fa-gem", color: "#8b5cf6" }
        ],
        evening: [
            { title: "Good Evening!", subtitle: "Finishing up for the day? Let's wrap up those final tasks together.", icon: "fa-moon", color: "#79c0ff" },
            { title: "Evening Wrap-Up!", subtitle: "Time to tie up loose ends. What needs your attention before wrapping up?", icon: "fa-check-circle", color: "#8b5cf6" },
            { title: "Sunset Session!", subtitle: "The golden hour of productivity. Let's end the day strong!", icon: "fa-cloud-moon", color: "#a855f7" },
            { title: "Evening Wind-Down!", subtitle: "Finishing touches time. Need help closing out your day?", icon: "fa-star", color: "#c084fc" },
            { title: "Last Sprint!", subtitle: "Final push before rest. Let's make these last hours count!", icon: "fa-flag-checkered", color: "#79c0ff" }
        ],
        night: [
            { title: "Working Late?", subtitle: "Burning the midnight oil? I'm here 24/7 to help you achieve your goals.", icon: "fa-moon", color: "#818cf8" },
            { title: "Night Owl Mode!", subtitle: "The world sleeps, but great ideas never do. Let's create magic!", icon: "fa-star", color: "#6366f1" },
            { title: "Late Night Hustle!", subtitle: "Dedication level: Expert. I'm with you all the way!", icon: "fa-rocket", color: "#7c3aed" },
            { title: "Midnight Momentum!", subtitle: "The quiet hours are perfect for deep work. What's the mission?", icon: "fa-moon", color: "#8b5cf6" },
            { title: "After Hours!", subtitle: "No rest for the ambitious! Let's knock this out together.", icon: "fa-certificate", color: "#a855f7" }
        ]
    },

    quickTips: [
        "Drag & drop threads from the sidebar to move conversations between agents. All formatting, context, and history stays intact!",
        "Use Ctrl+Enter to send messages quickly, or Shift+Enter to add new lines without sending.",
        "Click the thread ID badge to copy it - perfect for sharing specific conversations.",
        "Double-click any thread title to edit it inline. Give your conversations memorable names!",
        "Archive old threads to keep your workspace clean. Archived threads are still searchable and can be restored anytime.",
        "Use the session loader (ID input) to instantly jump to any thread by pasting its ID.",
        "Tag your threads for easy filtering! Add tags like 'urgent', 'research', or 'client-work' to organize conversations.",
        "Right-click thread cards for quick actions: archive, delete, copy ID, or export conversation history.",
        "Press '/' to focus the message input and start typing immediately. Small shortcuts = big productivity gains!"
    ],

    currentTipIndex: -1,

    getTimeBasedGreeting(agentName = null) {
        const hour = new Date().getHours();
        let variations;

        if (hour >= 5 && hour < 12) {
            variations = this.welcomeVariations.morning;
        } else if (hour >= 12 && hour < 17) {
            variations = this.welcomeVariations.afternoon;
        } else if (hour >= 17 && hour < 21) {
            variations = this.welcomeVariations.evening;
        } else {
            variations = this.welcomeVariations.night;
        }

        const greeting = variations[Math.floor(Math.random() * variations.length)];

        if (agentName && agentName !== 'Prime') {
            greeting.title = `${agentName} Ready!`;
            greeting.subtitle = greeting.subtitle.replace(/I'm|I am/gi, `${agentName} is`);
        }

        return greeting;
    },

    getNextQuickTip() {
        if (this.currentTipIndex === -1 || this.currentTipIndex >= this.quickTips.length - 1) {
            this.quickTips = this.quickTips.sort(() => Math.random() - 0.5);
            this.currentTipIndex = 0;
        } else {
            this.currentTipIndex++;
        }
        return this.quickTips[this.currentTipIndex];
    },

    initWelcomeMessage(location = 'prime') {
        const container = document.getElementById(`${location}-welcome-container`);
        if (!container) return;

        const greeting = this.getTimeBasedGreeting();
        const tip = this.getNextQuickTip();

        const titleEl = document.getElementById(`${location}-welcome-title`);
        const subtitleEl = document.getElementById(`${location}-welcome-subtitle`);
        const iconEl = container.querySelector('.welcome-icon i');

        if (titleEl) titleEl.textContent = greeting.title;
        if (subtitleEl) subtitleEl.textContent = greeting.subtitle;
        if (iconEl) {
            iconEl.className = `fas ${greeting.icon}`;
            iconEl.style.color = greeting.color;
        }

        const tipTextEl = container.querySelector('.quick-tip-text');
        if (tipTextEl) tipTextEl.textContent = tip;

        console.log(`✅ [Welcome] Initialized for ${location}: ${greeting.title}`);
    },

    getCurrentSeason() {
        const month = new Date().getMonth() + 1;
        if (month >= 12 || month <= 2) return 'Summer';
        if (month >= 3 && month <= 5) return 'Autumn';
        if (month >= 6 && month <= 8) return 'Winter';
        return 'Spring';
    }
};

console.log('✅ ThreadManager-Welcome module loaded');