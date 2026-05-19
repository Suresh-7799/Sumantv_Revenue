(function(){

    document.addEventListener(
        "keydown",
        function(event){

            /* SEARCH FOCUS */
            if(
                (event.ctrlKey || event.metaKey)
                &&
                event.key.toLowerCase() === "k"
            ){

                event.preventDefault();

                const search =
                document.getElementById(
                    "sidebarSearch"
                );

                if(search){

                    search.focus();

                }

            }

            /* ESCAPE */
            if(event.key === "Escape"){

                if(window.Modal){

                    Modal.closeAll();

                }

            }

        }
    );

})();