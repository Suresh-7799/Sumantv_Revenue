const sidebar =
document.getElementById("appSidebar");

const overlay =
document.getElementById("sidebarOverlay");

const toggle =
document.getElementById("sidebarToggle");

/* =========================
   OPEN SIDEBAR
========================= */

function openSidebar(){

    if(!sidebar) return;

    sidebar.classList.add("mobile-open");

    if(overlay){
        overlay.classList.add("active");
    }

    document.body.style.overflow = "hidden";
}

/* =========================
   CLOSE SIDEBAR
========================= */

function closeSidebar(){

    if(!sidebar) return;

    sidebar.classList.remove("mobile-open");

    if(overlay){
        overlay.classList.remove("active");
    }

    document.body.style.overflow = "";
}

/* =========================
   TOGGLE
========================= */

if(toggle){

    toggle.addEventListener(
        "click",
        function(){

            if(
                sidebar.classList.contains("mobile-open")
            ){
                closeSidebar();
            }else{
                openSidebar();
            }

        }
    );
}

/* =========================
   OVERLAY CLOSE
========================= */

if(overlay){

    overlay.addEventListener(
        "click",
        closeSidebar
    );
}

/* =========================
   WINDOW RESIZE RESET
========================= */

window.addEventListener(
    "resize",
    function(){

        if(window.innerWidth > 991){

            closeSidebar();
        }

    }
);



const sidebar =
document.getElementById(
    "appSidebar"
);

const overlay =
document.getElementById(
    "sidebarOverlay"
);

const toggle =
document.getElementById(
    "sidebarToggle"
);

/* =========================
   OPEN SIDEBAR
========================= */

function openSidebar(){

    if(!sidebar) return;

    sidebar.classList.add(
        "mobile-open"
    );

    if(overlay){

        overlay.classList.add(
            "active"
        );
    }

    document.body.style.overflow =
    "hidden";
}

/* =========================
   CLOSE SIDEBAR
========================= */

function closeSidebar(){

    if(!sidebar) return;

    sidebar.classList.remove(
        "mobile-open"
    );

    if(overlay){

        overlay.classList.remove(
            "active"
        );
    }

    document.body.style.overflow =
    "";
}

/* =========================
   TOGGLE
========================= */

if(toggle){

    toggle.addEventListener(

        "click",

        function(){

            if(
                sidebar.classList.contains(
                    "mobile-open"
                )
            ){

                closeSidebar();

            }else{

                openSidebar();
            }
        }
    );
}

/* =========================
   OVERLAY
========================= */

if(overlay){

    overlay.addEventListener(

        "click",

        closeSidebar
    );
}

/* =========================
   RESIZE
========================= */

window.addEventListener(

    "resize",

    function(){

        if(window.innerWidth > 991){

            closeSidebar();
        }
    }
);