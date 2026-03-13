import { loginMember, registerMember } from "./api.js";
import {
    consumeFlashMessage,
    redirectToDashboard,
    saveAuthSession,
} from "./auth.js";

const elements = {};

document.addEventListener("DOMContentLoaded", init);

function init() {
    collectElements();
    bindEvents();
    renderFlashMessage();
}

function collectElements() {
    elements.feedback = document.getElementById("home-feedback");

    elements.loginForm = document.getElementById("login-form");
    elements.loginEmail = document.getElementById("login-email");
    elements.loginPassword = document.getElementById("login-password");
    elements.loginSubmit = document.getElementById("login-submit");

    elements.registerForm = document.getElementById("register-form");
    elements.registerName = document.getElementById("register-name");
    elements.registerEmail = document.getElementById("register-email");
    elements.registerDob = document.getElementById("register-dob");
    elements.registerPassword = document.getElementById("register-password");
    elements.registerSubmit = document.getElementById("register-submit");
}

function bindEvents() {
    elements.loginForm.addEventListener("submit", onLoginSubmit);
    elements.registerForm.addEventListener("submit", onRegisterSubmit);
}

function renderFlashMessage() {
    const flash = consumeFlashMessage();
    if (!flash) {
        return;
    }

    showFeedback(flash.message, flash.variant);
}

function showFeedback(message, variant = "success") {
    elements.feedback.textContent = message;
    elements.feedback.className = `page-feedback ${variant}`;
}

function clearFeedback() {
    elements.feedback.textContent = "";
    elements.feedback.className = "page-feedback hidden";
}

function setButtonBusy(button, busy, idleLabel, busyLabel) {
    button.disabled = busy;
    button.classList.toggle("is-busy", busy);
    button.textContent = busy ? busyLabel : idleLabel;
}

function getErrorMessage(error, fallbackMessage) {
    if (error?.status === 429) {
        return "Too many requests. Please wait a moment and try again.";
    }

    if (error?.data && typeof error.data === "object" && !Array.isArray(error.data)) {
        const entries = Object.entries(error.data)
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : value}`);
        if (entries.length) {
            return entries.join(" | ");
        }
    }

    return error?.message || fallbackMessage;
}

async function onLoginSubmit(event) {
    event.preventDefault();
    clearFeedback();

    const credentials = {
        email: elements.loginEmail.value.trim(),
        password: elements.loginPassword.value,
    };

    setButtonBusy(elements.loginSubmit, true, "Log In", "Logging In...");

    try {
        const tokens = await loginMember(credentials);
        saveAuthSession(tokens);
        redirectToDashboard("Authenticated successfully. Welcome back.");
    } catch (error) {
        showFeedback(getErrorMessage(error, "Login failed."), "error");
    } finally {
        setButtonBusy(elements.loginSubmit, false, "Log In", "Logging In...");
    }
}

async function onRegisterSubmit(event) {
    event.preventDefault();
    clearFeedback();

    const payload = {
        name: elements.registerName.value.trim(),
        email: elements.registerEmail.value.trim(),
        password: elements.registerPassword.value,
    };

    if (elements.registerDob.value) {
        payload.DOB = elements.registerDob.value;
    }

    setButtonBusy(elements.registerSubmit, true, "Create Account", "Creating...");

    try {
        const member = await registerMember(payload);
        showFeedback(`Member created for ${member.name}. Attempting automatic login...`, "success");

        try {
            const tokens = await loginMember({
                email: payload.email,
                password: payload.password,
            });
            saveAuthSession(tokens);
            redirectToDashboard(`Welcome, ${member.name}. Your account is ready.`);
            return;
        } catch {
            elements.loginEmail.value = payload.email;
            elements.loginPassword.value = "";
            elements.loginEmail.focus();
            document.getElementById("login-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
            showFeedback(
                "Account created successfully. Automatic login was not available, so please sign in now.",
                "success",
            );
        }

        elements.registerForm.reset();
    } catch (error) {
        showFeedback(getErrorMessage(error, "Could not create the member account."), "error");
    } finally {
        setButtonBusy(elements.registerSubmit, false, "Create Account", "Creating...");
    }
}
