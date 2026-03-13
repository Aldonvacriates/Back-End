document.addEventListener("DOMContentLoaded", initLayout);

function initLayout() {
    const topbar = document.getElementById("topbar");
    const toggle = document.getElementById("menu-toggle");
    const menu = document.getElementById("topbar-menu");

    if (!topbar || !toggle || !menu) {
        return;
    }

    const closeMenu = () => {
        topbar.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
    };

    const openMenu = () => {
        topbar.classList.add("is-open");
        toggle.setAttribute("aria-expanded", "true");
    };

    toggle.addEventListener("click", () => {
        const isOpen = topbar.classList.contains("is-open");
        if (isOpen) {
            closeMenu();
            return;
        }

        openMenu();
    });

    menu.addEventListener("click", (event) => {
        const clickedLink = event.target.closest("a, button");
        if (!clickedLink) {
            return;
        }

        if (window.innerWidth <= 720) {
            closeMenu();
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 720) {
            closeMenu();
        }
    });
}
