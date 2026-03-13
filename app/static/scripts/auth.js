const ACCESS_TOKEN_KEY = "library_access_token";
const REFRESH_TOKEN_KEY = "library_refresh_token";
const FLASH_MESSAGE_KEY = "library_flash_message";

// Read the stored access token used for protected API calls.
export function getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY) || "";
}

// Read the stored refresh token used to renew access tokens.
export function getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY) || "";
}

// Persist both tokens after login or refresh.
export function saveAuthSession(tokens) {
    if (tokens.access_token) {
        localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    }

    if (tokens.refresh_token) {
        localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
    }
}

// Remove authentication data during logout or session expiry.
export function clearAuthSession() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function isAuthenticated() {
    return Boolean(getAccessToken());
}

// Store a one-time message that can survive a redirect.
export function setFlashMessage(message, variant = "success") {
    sessionStorage.setItem(
        FLASH_MESSAGE_KEY,
        JSON.stringify({ message, variant }),
    );
}

export function consumeFlashMessage() {
    const raw = sessionStorage.getItem(FLASH_MESSAGE_KEY);
    if (!raw) {
        return null;
    }

    sessionStorage.removeItem(FLASH_MESSAGE_KEY);

    try {
        return JSON.parse(raw);
    } catch {
        return null;
    }
}

export function redirectToDashboard(message = "") {
    if (message) {
        setFlashMessage(message, "success");
    }

    window.location.assign(window.APP_CONFIG.routes.dashboard);
}

export function redirectToHome(message = "", variant = "info") {
    if (message) {
        setFlashMessage(message, variant);
    }

    window.location.assign(window.APP_CONFIG.routes.home);
}

// Client-side guard for the dashboard page.
export function requireAuth() {
    if (!isAuthenticated()) {
        redirectToHome("Please log in to open the dashboard.", "warning");
        return false;
    }

    return true;
}
