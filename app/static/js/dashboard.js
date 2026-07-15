document.addEventListener("DOMContentLoaded", () => {

    /*=========================
        ATS CIRCLE ANIMATION
    =========================*/

    const progressCircle = document.querySelector(".progress-circle");

    if (progressCircle) {

        const radius = 90;
        const circumference = 2 * Math.PI * radius;

        progressCircle.style.strokeDasharray = circumference;

        let scoreElement = document.querySelector(".score-text h1");

        let score = 78;

        if (scoreElement) {
            score = parseInt(scoreElement.innerText) || 78;
        }

        const offset = circumference - (score / 100) * circumference;

        progressCircle.style.strokeDashoffset = circumference;

        setTimeout(() => {
            progressCircle.style.strokeDashoffset = offset;
        }, 400);
    }

    /*=========================
        NUMBER COUNTER
    =========================*/

    const counters = document.querySelectorAll(".summary-card h1");

    counters.forEach(counter => {

        const target = parseInt(counter.innerText);

        if (isNaN(target)) return;

        let current = 0;

        const speed = Math.max(10, target / 40);

        const updateCounter = () => {

            current += speed;

            if (current >= target) {
                counter.innerText = target;
            }
            else {
                counter.innerText = Math.floor(current);
                requestAnimationFrame(updateCounter);
            }

        };

        updateCounter();

    });

    /*=========================
        CARD HOVER EFFECT
    =========================*/

    document.querySelectorAll(".summary-card, .action-card").forEach(card => {

        card.addEventListener("mouseenter", () => {

            card.style.transform = "translateY(-8px) scale(1.02)";

        });

        card.addEventListener("mouseleave", () => {

            card.style.transform = "";

        });

    });

    /*=========================
        BUTTON RIPPLE EFFECT
    =========================*/

    document.querySelectorAll(".action-card").forEach(button => {

        button.addEventListener("click", function (e) {

            const ripple = document.createElement("span");

            const rect = this.getBoundingClientRect();

            ripple.style.left = (e.clientX - rect.left) + "px";
            ripple.style.top = (e.clientY - rect.top) + "px";

            ripple.classList.add("ripple");

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);

        });

    });

    /*=========================
        PAGE FADE-IN
    =========================*/

    const dashboard = document.querySelector(".dashboard");

    if (dashboard) {

        dashboard.style.opacity = "0";
        dashboard.style.transform = "translateY(20px)";

        setTimeout(() => {

            dashboard.style.transition = ".6s ease";

            dashboard.style.opacity = "1";

            dashboard.style.transform = "translateY(0px)";

        }, 100);

    }

/*=========================
        MOBILE SIDEBAR TOGGLE
    =========================*/

    const sidebar = document.querySelector(".sidebar");
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebarOverlay = document.getElementById("sidebarOverlay");

    function openSidebar() {
        if (sidebar) sidebar.classList.add("active");
        if (sidebarOverlay) sidebarOverlay.classList.add("active");
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove("active");
        if (sidebarOverlay) sidebarOverlay.classList.remove("active");
    }

    if (sidebarToggle) {

        sidebarToggle.addEventListener("click", () => {

            if (sidebar && sidebar.classList.contains("active")) {
                closeSidebar();
            } else {
                openSidebar();
            }

        });

    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener("click", closeSidebar);
    }

    // Close sidebar automatically when a menu link is tapped (mobile UX)
    if (sidebar) {

        sidebar.querySelectorAll(".menu li a").forEach(link => {

            link.addEventListener("click", () => {

                if (window.innerWidth <= 992) {
                    closeSidebar();
                }

            });

        });

    }

});

const hamburgerBtn = document.getElementById('hamburgerBtn');
const navMenu = document.getElementById('navMenu');

if (hamburgerBtn && navMenu) {
    hamburgerBtn.addEventListener('click', () => {
        const isOpen = navMenu.classList.toggle('open');
        hamburgerBtn.setAttribute('aria-expanded', isOpen);
    });
}