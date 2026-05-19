(function(){

    const input =
    document.getElementById(
        "sidebarSearch"
    );

    if(!input) return;

    input.addEventListener(
        "input",
        function(){

            const value =
            input.value
            .toLowerCase()
            .trim();

            const links =
            document.querySelectorAll(
                ".sidebar-link"
            );

            links.forEach(link=>{

                const text =
                link.innerText
                .toLowerCase();

                if(
                    text.includes(value)
                ){

                    link.style.display =
                    "flex";

                }else{

                    link.style.display =
                    "none";

                }

            });

        }
    );

})();