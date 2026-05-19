(function(){

    const STORAGE_KEY = "app-theme";

    const root =
    document.documentElement;

    const toggleButtons =
    document.querySelectorAll(
        "[data-theme-toggle]"
    );

    function applyTheme(theme){

        root.setAttribute(
            "data-theme",
            theme
        );

        localStorage.setItem(
            STORAGE_KEY,
            theme
        );

        syncToggles(theme);

        window.dispatchEvent(
            new CustomEvent(
                "theme:changed",
                {
                    detail:{ theme }
                }
            )
        );
    }

    function syncToggles(theme){

        toggleButtons.forEach(btn=>{

            btn.setAttribute(
                "aria-pressed",
                theme === "dark"
            );

        });

    }

    function toggleTheme(){

        const current =
        root.getAttribute("data-theme")
        || "dark";

        applyTheme(
            current === "dark"
            ? "light"
            : "dark"
        );
    }

    function initializeTheme(){

        const saved =
        localStorage.getItem(STORAGE_KEY);

        applyTheme(
            saved || "dark"
        );

    }

    toggleButtons.forEach(btn=>{

        btn.addEventListener(
            "click",
            toggleTheme
        );

    });

    initializeTheme();

})();