(function(){

    const body =
    document.body;

    function openModal(id){

        const modal =
        document.querySelector(
            `[data-modal="${id}"]`
        );

        if(!modal) return;

        modal.classList.add(
            "modal-open"
        );

        body.style.overflow = "hidden";

        window.dispatchEvent(
            new CustomEvent(
                "modal:open",
                {
                    detail:{ id }
                }
            )
        );
    }

    function closeModal(id){

        const modal =
        document.querySelector(
            `[data-modal="${id}"]`
        );

        if(!modal) return;

        modal.classList.remove(
            "modal-open"
        );

        body.style.overflow = "";

        window.dispatchEvent(
            new CustomEvent(
                "modal:close",
                {
                    detail:{ id }
                }
            )
        );
    }

    function closeAllModals(){

        document
        .querySelectorAll(
            "[data-modal]"
        )
        .forEach(modal=>{

            modal.classList.remove(
                "modal-open"
            );

        });

        body.style.overflow = "";
    }

    document.addEventListener(
        "click",
        function(event){

            const openTrigger =
            event.target.closest(
                "[data-open-modal]"
            );

            if(openTrigger){

                openModal(
                    openTrigger.getAttribute(
                        "data-open-modal"
                    )
                );

            }

            const closeTrigger =
            event.target.closest(
                "[data-close-modal]"
            );

            if(closeTrigger){

                closeModal(
                    closeTrigger.getAttribute(
                        "data-close-modal"
                    )
                );

            }

            if(
                event.target.matches(
                    "[data-modal-overlay]"
                )
            ){

                closeAllModals();

            }

        }
    );

    document.addEventListener(
        "keydown",
        function(event){

            if(event.key === "Escape"){

                closeAllModals();

            }

        }
    );

    window.Modal = {
        open:openModal,
        close:closeModal,
        closeAll:closeAllModals
    };

})();