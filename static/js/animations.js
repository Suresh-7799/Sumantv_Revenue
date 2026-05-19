document.addEventListener(
    "DOMContentLoaded",
    function(){

        const animated =
        document.querySelectorAll(
            ".dashboard-panel, .stat-card"
        );

        animated.forEach((el,index)=>{

            el.style.opacity = "0";
            el.style.transform =
            "translateY(20px)";

            setTimeout(()=>{

                el.style.transition =
                "all 0.6s ease";

                el.style.opacity = "1";
                el.style.transform =
                "translateY(0)";

            }, index * 120);

        });

    }
);