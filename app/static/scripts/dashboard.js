import {
    createBook,
    getBooks,
    getCurrentMember,
    getLoans,
    loanBook,
} from "./api.js";
import {
    clearAuthSession,
    consumeFlashMessage,
    redirectToHome,
    requireAuth,
} from "./auth.js";

const state = {
    member: null,
    books: [],
    loans: [],
};

const elements = {};

document.addEventListener("DOMContentLoaded", init);

async function init() {
    if (!requireAuth()) {
        return;
    }

    collectElements();
    bindEvents();
    renderFlashMessage();
    setInitialLoadingState();
    await loadDashboard();
}

function collectElements() {
    elements.feedback = document.getElementById("dashboard-feedback");
    elements.logoutButton = document.getElementById("logout-button");
    elements.navMemberBadge = document.getElementById("nav-member-badge");

    elements.welcomeName = document.getElementById("welcome-name");
    elements.welcomeEmail = document.getElementById("welcome-email");
    elements.welcomeDob = document.getElementById("welcome-dob");
    elements.memberIdValue = document.getElementById("member-id-value");
    elements.booksCount = document.getElementById("books-count");
    elements.loansCount = document.getElementById("loans-count");

    elements.bookForm = document.getElementById("book-form");
    elements.bookTitle = document.getElementById("book-title");
    elements.bookAuthor = document.getElementById("book-author");
    elements.bookGenre = document.getElementById("book-genre");
    elements.bookDesc = document.getElementById("book-desc");
    elements.bookSubmit = document.getElementById("book-submit");
    elements.reloadBooks = document.getElementById("reload-books");
    elements.booksTable = document.getElementById("books-table");

    elements.loanForm = document.getElementById("loan-form");
    elements.loanDate = document.getElementById("loan-date");
    elements.loanBooks = document.getElementById("loan-books");
    elements.loanSubmit = document.getElementById("loan-submit");
    elements.reloadLoans = document.getElementById("reload-loans");
    elements.loansTable = document.getElementById("loans-table");
}

function bindEvents() {
    elements.logoutButton.addEventListener("click", onLogout);
    elements.reloadBooks.addEventListener("click", () => {
        loadBooks().catch((error) => handleDashboardError(error, "Could not refresh books."));
    });
    elements.reloadLoans.addEventListener("click", () => {
        loadLoans().catch((error) => handleDashboardError(error, "Could not refresh loans."));
    });
    elements.bookForm.addEventListener("submit", onBookSubmit);
    elements.loanForm.addEventListener("submit", onLoanSubmit);
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

function setInitialLoadingState() {
    elements.booksTable.innerHTML = `
        <div class="loading-state">
            <p>Loading books from the catalog...</p>
        </div>
    `;
    elements.loansTable.innerHTML = `
        <div class="loading-state">
            <p>Loading your active loans...</p>
        </div>
    `;
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

function handleDashboardError(error, fallbackMessage) {
    if (error?.status === 401) {
        clearAuthSession();
        redirectToHome("Your session expired. Please log in again.", "warning");
        return;
    }

    showFeedback(getErrorMessage(error, fallbackMessage), "error");
}

async function loadDashboard() {
    clearFeedback();

    try {
        const [member, books, loans] = await Promise.all([
            getCurrentMember(),
            getBooks(),
            getLoans(),
        ]);

        state.member = member;
        state.books = Array.isArray(books) ? books : [];
        state.loans = Array.isArray(loans) ? loans : [];

        renderMember();
        renderBooks();
        renderLoans();
        populateLoanOptions();
        updateSnapshot();
    } catch (error) {
        handleDashboardError(error, "Could not load the dashboard.");
    }
}

async function loadBooks() {
    const books = await getBooks();
    state.books = Array.isArray(books) ? books : [];
    renderBooks();
    populateLoanOptions();
    updateSnapshot();
}

async function loadLoans() {
    const loans = await getLoans();
    state.loans = Array.isArray(loans) ? loans : [];
    renderLoans();
    updateSnapshot();
}

function renderMember() {
    if (!state.member) {
        return;
    }

    elements.welcomeName.textContent = `Welcome, ${state.member.name}`;
    elements.welcomeEmail.textContent = state.member.email;
    elements.welcomeDob.textContent = `Date of birth: ${state.member.DOB || "Not set"}`;
    elements.memberIdValue.textContent = String(state.member.id);
    elements.navMemberBadge.textContent = state.member.name;
}

function renderBooks() {
    if (!state.books.length) {
        elements.booksTable.innerHTML = `
            <div class="empty-state">
                <p>No books have been added yet.</p>
            </div>
        `;
        return;
    }

    const rows = state.books.map((book) => `
        <tr>
            <td data-label="ID">${book.id}</td>
            <td data-label="Title">${escapeHtml(book.title)}</td>
            <td data-label="Author">${escapeHtml(book.author)}</td>
            <td data-label="Genre">${escapeHtml(book.genre)}</td>
            <td data-label="Description">${escapeHtml(book.desc)}</td>
        </tr>
    `).join("");

    elements.booksTable.innerHTML = buildTable(
        ["ID", "Title", "Author", "Genre", "Description"],
        rows,
    );
}

function renderLoans() {
    if (!state.loans.length) {
        elements.loansTable.innerHTML = `
            <div class="empty-state">
                <p>You do not have any active loans yet.</p>
            </div>
        `;
        return;
    }

    const rows = state.loans.map((loan) => `
        <tr>
            <td data-label="Loan ID">${loan.id}</td>
            <td data-label="Loan Date">${escapeHtml(loan.loan_date)}</td>
            <td data-label="Books">${renderBookTags(loan.book_ids)}</td>
        </tr>
    `).join("");

    elements.loansTable.innerHTML = buildTable(
        ["Loan ID", "Loan Date", "Books"],
        rows,
    );
}

function populateLoanOptions() {
    elements.loanBooks.innerHTML = state.books.map((book) => (
        `<option value="${book.id}">${escapeHtml(book.title)} by ${escapeHtml(book.author)}</option>`
    )).join("");
}

function updateSnapshot() {
    elements.booksCount.textContent = String(state.books.length);
    elements.loansCount.textContent = String(state.loans.length);
}

async function onBookSubmit(event) {
    event.preventDefault();
    clearFeedback();

    const payload = {
        title: elements.bookTitle.value.trim(),
        author: elements.bookAuthor.value.trim(),
        genre: elements.bookGenre.value.trim(),
        desc: elements.bookDesc.value.trim(),
    };

    setButtonBusy(elements.bookSubmit, true, "Add Book", "Adding...");

    try {
        await createBook(payload);
        elements.bookForm.reset();
        await loadBooks();
        showFeedback("Book added successfully.", "success");
    } catch (error) {
        handleDashboardError(error, "Could not add the book.");
    } finally {
        setButtonBusy(elements.bookSubmit, false, "Add Book", "Adding...");
    }
}

async function onLoanSubmit(event) {
    event.preventDefault();
    clearFeedback();

    const selectedBookIds = Array.from(elements.loanBooks.selectedOptions).map((option) => Number(option.value));
    if (!selectedBookIds.length) {
        showFeedback("Select at least one book before creating a loan.", "warning");
        return;
    }

    const payload = {
        loan_date: elements.loanDate.value,
        member_id: state.member?.id,
        book_ids: selectedBookIds,
    };

    setButtonBusy(elements.loanSubmit, true, "Loan Books", "Saving...");

    try {
        await loanBook(payload);
        elements.loanForm.reset();
        await loadLoans();
        showFeedback("Loan created successfully.", "success");
    } catch (error) {
        handleDashboardError(error, "Could not create the loan.");
    } finally {
        setButtonBusy(elements.loanSubmit, false, "Loan Books", "Saving...");
    }
}

function onLogout() {
    clearAuthSession();
    redirectToHome("You have been logged out.", "success");
}

function buildTable(headers, rows) {
    return `
        <table class="table table-hover align-middle mb-0">
            <thead>
                <tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>
    `;
}

function renderBookTags(bookIds = []) {
    if (!bookIds.length) {
        return '<span class="meta-text">No books linked</span>';
    }

    const tags = bookIds.map((bookId) => {
        const book = state.books.find((item) => item.id === bookId);
        const label = book ? book.title : `Book #${bookId}`;
        return `<span class="tag">${escapeHtml(label)}</span>`;
    }).join("");

    return `<div class="tag-list">${tags}</div>`;
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}
