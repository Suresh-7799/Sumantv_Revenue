(function(){

    /* =========================
       PASSIVE EVENTS
    ========================== */

    const passiveEvents = [
        "touchstart",
        "touchmove",
        "wheel"
    ];

    passiveEvents.forEach(type=>{

        window.addEventListener(
            type,
            ()=>{},
            {
                passive:true
            }
        );

    });

    /* =========================
       REDUCED MOTION
    ========================== */

    const prefersReducedMotion =
    window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    );

    if(prefersReducedMotion.matches){

        document.documentElement
        .classList.add(
            "reduced-motion"
        );

    }

    /* =========================
       VISIBILITY API
    ========================== */

    document.addEventListener(
        "visibilitychange",
        function(){

            if(document.hidden){

                console.log(
                    "[APP PAUSED]"
                );

            }

        }
    );

})();