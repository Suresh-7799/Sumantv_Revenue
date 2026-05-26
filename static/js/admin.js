const roleSelect =
document.getElementById(
    "roleSelect"
);

const customRoleInput =
document.getElementById(
    "customRoleInput"
);

if(roleSelect && customRoleInput){

    roleSelect.addEventListener(
        "change",
        function(){

            if(this.value === "custom"){

                customRoleInput
                .classList
                .add("active");

                customRoleInput.focus();

            }else{

                customRoleInput
                .classList
                .remove("active");

                customRoleInput.value = "";
            }

        }
    );

}


/* =========================
   DOB PICKER
========================= */

const adminDobPicker =
document.getElementById(
    "admin_date_of_birth"
);

const adminDobButton =
document.querySelector(
    ".dob-calendar-btn"
);

if(

    adminDobPicker &&

    typeof flatpickr !== "undefined"

){

    const adminDobCalendar = flatpickr(

        adminDobPicker,

        {

            dateFormat:"d/m/Y",

            allowInput:true,

            clickOpens:false,

            disableMobile:true,

            weekNumbers:false
        }
    );

    adminDobButton?.addEventListener(

        "click",

        ()=>{

            adminDobCalendar.open();
        }
    );
}

const teamSearch =
document.getElementById(
    "teamSearch"
);

if(teamSearch){

    teamSearch.addEventListener(

        "keyup",

        function(){

            const value =
            this.value.toLowerCase();

            document
            .querySelectorAll(
                ".team-table tbody tr"
            )
            .forEach(row=>{

                row.style.display =

                row.innerText
                .toLowerCase()
                .includes(value)

                ? ""

                : "none";

            });

        }
    );
}

function openRequestsModal(){

    const modal = document.getElementById(
        "requestsModal"
    );

    if(modal){

        modal.classList.add(
            "active"
        );
    }
}

function closeRequestsModal(){

    const modal = document.getElementById(
        "requestsModal"
    );

    if(modal){

        modal.classList.remove(
            "active"
        );
    }
}



async function approveUser(userId){

    try{

        const csrfToken = document.getElementById(

            "csrfToken"

        ).value;

        const response = await fetch(

            `/admin/approve-user/${userId}`,

            {

                method:"POST",

                headers:{

                    "X-CSRFToken": csrfToken
                }
            }
        );

        if(response.ok){

            const userRow = document.querySelector(

                `[data-user-id="${userId}"]`

            );

            if(userRow){

                userRow.remove();
            }

            updateRequestCount();

            showRequestToast(

                "User approved successfully"
            );
        }

    }catch(error){

        console.error(error);
    }
}


async function rejectUser(userId){

    try{

        const csrfToken = document.getElementById(

            "csrfToken"

        ).value;

        const response = await fetch(

            `/admin/reject-user/${userId}`,

            {

                method:"POST",

                headers:{

                    "X-CSRFToken": csrfToken
                }
            }
        );

        if(response.ok){

            const userRow = document.querySelector(

                `[data-user-id="${userId}"]`

            );

            if(userRow){

                userRow.remove();
            }

            updateRequestCount();

            showRequestToast(

                "User rejected"
            );
        }

    }catch(error){

        console.error(error);
    }
}


function updateRequestCount(){

    const countElement = document.getElementById(

        "requestCount"

    );

    let currentCount = parseInt(

        countElement.innerText
    );

    currentCount--;

    if(currentCount < 0){

        currentCount = 0;
    }

    countElement.innerText = currentCount;

    if(currentCount === 0){

        const modalBody = document.querySelector(

            ".requests-modal-body"

        );

        if(

            !document.querySelector(
                ".no-requests"
            )
        ){

            modalBody.innerHTML += `

                <div class="no-requests">

                    No New Requests

                </div>

            `;
        }
    }
}


function showRequestToast(message){

    const toast = document.getElementById(

        "requestToast"

    );

    toast.innerText = message;

    toast.style.display = "block";

    setTimeout(()=>{

        toast.style.display = "none";

    },2500);
}