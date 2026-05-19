(function(){

    const lazyTargets =
    document.querySelectorAll(
        "[data-lazy]"
    );

    if(!lazyTargets.length) return;

    const observer =
    new IntersectionObserver(

        entries=>{

            entries.forEach(entry=>{

                if(
                    entry.isIntersecting
                ){

                    const el =
                    entry.target;

                    const src =
                    el.dataset.src;

                    if(src){

                        el.src = src;

                    }

                    el.classList.add(
                        "lazy-loaded"
                    );

                    observer.unobserve(el);

                }

            });

        },

        {
            threshold:0.12
        }

    );

    lazyTargets.forEach(el=>{

        observer.observe(el);

    });

})();