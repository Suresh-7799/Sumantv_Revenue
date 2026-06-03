const csrfToken = document.querySelector(
    'input[name="csrf_token"]'
)?.value;

        /* =========================
           TOAST
        ========================= */

        function showToast(message){

            const ytToast =
            document.getElementById(
                "ytToast"
            );

            if(!ytToast){
                return;
            }

            ytToast.innerText =
            message;

            ytToast.classList.add(
                "show"
            );

            setTimeout(

                ()=>{

                    ytToast.classList.remove(
                        "show"
                    );

                },

                2200
            );
        }


document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        const headerCheckbox =
        document.getElementById(
            "headerCheckbox"
        );

        const rowCheckboxes =
        document.querySelectorAll(
            ".row-checkbox"
        );

        const selectedActions =
        document.getElementById(
            "selectedActions"
        );

        const editBtn =
        document.getElementById(
            "editBtn"
        );

        const deleteBtn =
        document.getElementById(
            "deleteBtn"
        );

        const exportBtn =
        document.getElementById(
            "exportBtn"
        );


        /* =========================
           ROW CHECKBOX
        ========================= */

        rowCheckboxes.forEach(

            (checkbox)=>{

                checkbox.addEventListener(

                    "change",

                    ()=>{

                        updateActions();
                    }
                );
            }
        );

        headerCheckbox?.addEventListener(

            "change",

            ()=>{

                rowCheckboxes.forEach(

                    (checkbox)=>{

                        checkbox.checked =

                        headerCheckbox.checked;
                    }
                );

                updateActions();
            }
        );

        /* =========================
           UPDATE ACTIONS
        ========================= */

        function updateActions(){

            if(!selectedActions){
                return;
            }

            const checked =
            document.querySelectorAll(

                ".row-checkbox:checked"
            );

            if(
                checked.length === 0
            ){

                selectedActions.style.display =
                "none";

                return;
            }

            selectedActions.style.display =
            "flex";

            if(

                checked.length === 1 &&

                editBtn

            ){

                editBtn.style.display =
                "inline-flex";

            }else if(editBtn){

                editBtn.style.display =
                "none";
            }
        }

/* =========================
   DELETE
========================= */

if(deleteBtn){

    deleteBtn.addEventListener(

        "click",

        async ()=>{

            const checked =
            document.querySelectorAll(

                ".row-checkbox:checked"
            );

            const ids = [];

            checked.forEach(

                (checkbox)=>{

                    ids.push(

                        checkbox.dataset.id
                    );
                }
            );

            if(ids.length === 0){

                showToast(
                    "No rows selected"
                );

                return;
            }

            try{

                const response =
                await fetch(

                    "/workspace/delete-strip-results",

                    {

                        method:"POST",

                        headers:{

                            "Content-Type":
                            "application/json",

                            "X-CSRFToken":
                            csrfToken

                        },

                        body:JSON.stringify({

                            ids:ids
                        })
                    }
                );

                const data =
                await response.json();

                if(data.success){

                    checked.forEach(

                        (checkbox)=>{

                            checkbox
                            .closest("tr")
                            ?.remove();
                        }
                    );

                    showToast(

                        "Selected results deleted"
                    );

                    updateActions();
                    selectedActions.style.display =
                        "none";

                }else{

                    showToast(
                        "Delete failed"
                    );
                }

            }catch(error){

                console.error(error);

                showToast(
                    "Server error"
                );
            }
        }
    );
}


/* =========================
   EDIT
========================= */

if(editBtn){

    editBtn.addEventListener(

        "click",

        ()=>{

            const checked =
            document.querySelectorAll(

                ".row-checkbox:checked"
            );

            if(
                checked.length !== 1
            ){

                showToast(
                    "Select one row only"
                );

                return;
            }

            const checkbox =
            checked[0];

            const row =
            checkbox.closest(
                "tr"
            );

            const stripCell =
            row.querySelector(
                ".strip-cell"
            );

            const input =
            row.querySelector(
                ".strip-edit-input"
            );

            const textSpan =
            row.querySelector(
                ".strip-text"
            );

            if(

                !stripCell ||

                !input ||

                !textSpan

            ){

                showToast(
                    "Strip column missing"
                );

                return;
            }

            stripCell.classList.add(
                "editing"
            );

            input.focus();

            input.onkeydown = async (

                event
            )=>{

                if(
                    event.key === "Enter"
                ){

                    const newValue =
                    input.value.trim();

                    if(!newValue){

                        showToast(
                            "Strip cannot be empty"
                        );

                        return;
                    }

                    try{

                        const response =
                        await fetch(

                            "/workspace/update-strip-result",

                            {

                                method:"POST",

                                headers:{

                                    "Content-Type":
                                    "application/json",

                                    "X-CSRFToken":
                                    csrfToken

                                },

                                body:JSON.stringify({

                                    id:
                                    checkbox.dataset.id,

                                    strip_name:
                                    newValue
                                })
                            }
                        );

                        const data =
                        await response.json();

                        if(data.success){

                            textSpan.innerText =
                            newValue;

                            stripCell.classList.remove(
                                "editing"
                            );

                            showToast(
                                "Strip updated"
                            );

                        }else{

                            showToast(
                                "Update failed"
                            );
                        }

                    }catch(error){

                        console.error(error);

                        showToast(
                            "Server error"
                        );
                    }
                }
            };
        }
    );
}

        /* =========================
           EXPORT
        ========================= */

        if(exportBtn){

            exportBtn.addEventListener(

                "click",

                ()=>{

                    showToast(
                        "Export not configured"
                    );
                }
            );
        }
    }
);


const openChannelModal =
document.getElementById(
    "openChannelModal"
);

const closeChannelModal =
document.getElementById(
    "closeChannelModal"
);

const channelModal =
document.getElementById(
    "channelModal"
);

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

window.addEventListener(

    "click",

    (event)=>{

        if(
            event.target ===
            channelModal
        ){

            channelModal.style.display =
            "none";
        }
    }
);


const runScanBtn =
document.getElementById(
    "runScanBtn"
);

const stopScanBtn =
document.getElementById(
    "stopScanBtn"
);

async function updateScanButtons(){

    try{

        const response =
        await fetch(
            "/workspace/scan-status"
        );

        const data =
        await response.json();

        if(data.running){

            if(stopScanBtn){

                stopScanBtn.style.display =
                "inline-flex";
            }

            if(runScanBtn){

                runScanBtn.style.display =
                "none";
            }

        }else{

            if(stopScanBtn){

                stopScanBtn.style.display =
                "none";
            }

            if(runScanBtn){

                 runScanBtn.style.display =
                "inline-flex";
            }
        }

    }catch(error){

        console.error(error);
    }
}

updateScanButtons();

setInterval(

    updateScanButtons,

    5000
);

if(

    stopScanBtn

){

    stopScanBtn.addEventListener(

        "click",

        async ()=>{

            try{

                await fetch(

                    "/workspace/stop-channel-scan",

                    {

                        method:"POST",

                        headers:{
                            "X-CSRFToken":
                            csrfToken
                        }

                    }
                );

                showToast(
                    "Scan stopped"
                );

                updateScanButtons();

            }catch(error){

                console.error(error);

                showToast(
                    "Failed to stop scan"
                );
            }
        }
    );
}

runScanBtn?.addEventListener(

    "click",

    ()=>{

        setTimeout(

            ()=>{

                updateScanButtons();

            },

            1000
        );
    }
);

