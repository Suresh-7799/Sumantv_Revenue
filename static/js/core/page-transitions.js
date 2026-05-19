(function(){

    const body =
    document.body;

    window.addEventListener(
        "pageshow",
        function(){

            body.classList.add(
                "page-visible"
            );

        }
    );

    document.addEventListener(
        "click",
        function(event){

            const link =
            event.target.closest("a");

            if(!link) return;

            const href =
            link.getAttribute("href");

            if(
                !href ||
                href.startsWith("#") ||
                href.startsWith("javascript") ||
                link.target === "_blank"
            ){
                return;
            }

            event.preventDefault();

            body.classList.remove(
                "page-visible"
            );

            setTimeout(()=>{

                window.location.href =
                href;

            },180);

        }
    );

})();