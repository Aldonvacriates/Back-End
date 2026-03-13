import {
    clearAuthSession,
    getAccessToken,
    getRefreshToken,
    saveAuthSession,
} from "./auth.js";

function buildUrl(path) {
    return `${window.APP_CONFIG.apiBase || ""}${path}`;
}

async function parseResponse(response) {
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
        return response.json();
    }

    const text = await response.text();
    return text ? { message: text } : {};
}

function normalizeError(status, data) {
    const message = data?.error || data?.message || "Request failed.";
    return { status, data, message };
}

async function request(path, options = {}) {
    const {
        method = "GET",
        body,
        auth = true,
        retryOnAuthError = true,
        headers = {},
    } = options;

    const requestHeaders = new Headers(headers);
    requestHeaders.set("Accept", "application/json");

    if (body && !requestHeaders.has("Content-Type")) {
        requestHeaders.set("Content-Type", "application/json");
    }

    if (auth) {
        const accessToken = getAccessToken();
        if (accessToken) {
            requestHeaders.set("Authorization", `Bearer ${accessToken}`);
        }
    }

    const response = await fetch(buildUrl(path), {
        method,
        headers: requestHeaders,
        body: body ? JSON.stringify(body) : undefined,
    });

    const data = await parseResponse(response);

    if (
        response.status === 401 &&
        auth &&
        retryOnAuthError &&
        path !== "/auth/refresh" &&
        getRefreshToken()
    ) {
        await refreshToken();
        return request(path, { ...options, retryOnAuthError: false });
    }

    if (!response.ok) {
        if (response.status === 401) {
            clearAuthSession();
        }

        throw normalizeError(response.status, data);
    }

    return data;
}

export async function registerMember(payload) {
    return request("/members/", {
        method: "POST",
        auth: false,
        body: payload,
    });
}

export async function loginMember(payload) {
    return request("/auth/login", {
        method: "POST",
        auth: false,
        body: payload,
    });
}

export async function refreshToken() {
    const refreshTokenValue = getRefreshToken();
    if (!refreshTokenValue) {
        throw normalizeError(401, { message: "No refresh token available." });
    }

    const response = await fetch(buildUrl("/auth/refresh"), {
        method: "POST",
        headers: {
            Accept: "application/json",
            Authorization: `Bearer ${refreshTokenValue}`,
        },
    });

    const data = await parseResponse(response);
    if (!response.ok) {
        clearAuthSession();
        throw normalizeError(response.status, data);
    }

    saveAuthSession({
        access_token: data.access_token,
        refresh_token: refreshTokenValue,
    });

    return data;
}

export async function getCurrentMember() {
    return request("/members/me");
}

export async function getBooks() {
    return request("/books/");
}

export async function createBook(payload) {
    return request("/books/", {
        method: "POST",
        body: payload,
    });
}

export async function getLoans() {
    return request("/loans/me");
}

export async function loanBook(payload) {
    return request("/loans/", {
        method: "POST",
        body: payload,
    });
}
