(function(){

    const activeClass =
    "dropdown-open";

    function closeAllDropdowns(){

        document
        .querySelectorAll(
            "[data-dropdown].dropdown-open"
        )
        .forEach(dropdown=>{

            dropdown.classList.remove(
                activeClass
            );

        });

    }

    document.addEventListener(
        "click",
        function(event){

            const trigger =
            event.target.closest(
                "[data-dropdown-trigger]"
            );

            if(trigger){

                event.stopPropagation();

                const target =
                trigger.getAttribute(
                    "data-dropdown-trigger"
                );

                const dropdown =
                document.querySelector(
                    `[data-dropdown="${target}"]`
                );

                if(!dropdown) return;

                const alreadyOpen =
                dropdown.classList.contains(
                    activeClass
                );

                closeAllDropdowns();

                if(!alreadyOpen){

                    dropdown.classList.add(
                        activeClass
                    );

                }

                return;
            }

            if(
                !event.target.closest(
                    "[data-dropdown]"
                )
            ){

                closeAllDropdowns();

            }

        }
    );

    document.addEventListener(
        "keydown",
        function(event){

            if(event.key === "Escape"){

                closeAllDropdowns();

            }

        }
    );

})();