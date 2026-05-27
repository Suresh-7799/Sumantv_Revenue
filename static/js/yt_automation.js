const openChannelModal = document.getElementById(
    "openChannelModal"
);

const closeChannelModal = document.getElementById(
    "closeChannelModal"
);

const channelModal = document.getElementById(
    "channelModal"
);

const filterToggleBtn = document.getElementById(
    "filterToggleBtn"
);

const filterPanel = document.getElementById(
    "filterPanel"
);

const tableMenuBtn = document.getElementById(
    "tableMenuBtn"
);

const tableDropdown = document.getElementById(
    "tableDropdown"
);

const headerCheckbox = document.getElementById(
    "headerCheckbox"
);

const rowCheckboxes = document.querySelectorAll(
    ".row-checkbox"
);


/* =========================
   CHANNEL MODAL
========================= */

openChannelModal?.addEventListener(

    "click",

    ()=>{

        channelModal.style.display =
        "flex";
    }
);

closeChannelModal?.addEventListener(

    "click",

    ()=>{

        channelModal.style.display =
        "none";
    }
);


/* =========================
   FILTER TOGGLE
========================= */

filterToggleBtn?.addEventListener(

    "click",

    ()=>{

        if(

            filterPanel.style.display ===
            "none"

        ){

            filterPanel.style.display =
            "flex";

        }else{

            filterPanel.style.display =
            "none";
        }
    }
);


/* =========================
   TABLE DROPDOWN
========================= */

tableMenuBtn?.addEventListener(

    "click",

    (event)=>{

        event.stopPropagation();

        if(

            tableDropdown.style.display ===
            "flex"

        ){

            tableDropdown.style.display =
            "none";

        }else{

            tableDropdown.style.display =
            "flex";
        }
    }
);


/* =========================
   SELECT ALL CHECKBOX
========================= */

headerCheckbox?.addEventListener(

    "change",

    ()=>{

        rowCheckboxes.forEach(

            (checkbox)=>{

                checkbox.checked =
                headerCheckbox.checked;
            }
        );
    }
);


/* =========================
   WINDOW CLICK EVENTS
========================= */

window.addEventListener(

    "click",

    (event)=>{

        /* CLOSE CHANNEL MODAL */

        if(
            event.target === channelModal
        ){

            channelModal.style.display =
            "none";
        }

        /* CLOSE TABLE DROPDOWN */

        if(

            !tableMenuBtn?.contains(
                event.target
            )

            &&

            !tableDropdown?.contains(
                event.target
            )

        ){

            tableDropdown.style.display =
            "none";
        }
    }
);