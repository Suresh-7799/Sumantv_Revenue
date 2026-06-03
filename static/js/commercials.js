document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initializeCommercials();
    }
);

function initializeCommercials(){

    loadChannels();

    initializeAddChannel();

    initializeAddClient();

    initializeImagePreview();

    initializeChannelLink();

    initializeModalHandlers();

    initializeCommercialScan();

    initializeCommercialScanButtons();
}



function initializeModalHandlers(){

    const addChannelBtn =
    document.getElementById(
        "openAddChannelBtn"
    );

    const addClientBtn =
    document.getElementById(
        "openAddClientBtn"
    );

    const manageChannelBtn =
    document.getElementById(
        "openManageChannelBtn"
    );

    const manageClientBtn =
    document.getElementById(
        "openManageClientBtn"
    );

    addChannelBtn?.addEventListener(

        "click",

        ()=>{

            document
            .getElementById(
                "addChannelForm"
            )
            .reset();

            delete document
            .getElementById(
                "addChannelForm"
            )
            .dataset.editId;

            document
            .getElementById(
                "addChannelModal"
            )
            .classList.add(
                "active"
            );
        }
    );

    addClientBtn?.addEventListener(

        "click",

        ()=>{
            document
            .getElementById(
                "addClientForm"
            )
            .reset();

            delete document
            .getElementById(
                "addClientForm"
            )
            .dataset.editId;

            document
            .getElementById(
                "addClientModal"
            )
            .classList.add(
                "active"
            );
        }
    );

    manageChannelBtn?.addEventListener(

        "click",

        async ()=>{

            await loadManageChannels();

            document
            .getElementById(
                "manageChannelModal"
            )
            .classList.add(
                "active"
            );
        }
    );

    manageClientBtn?.addEventListener(

        "click",

        async ()=>{

            await loadManageClients();

            document
            .getElementById(
                "manageClientModal"
            )
            .classList.add(
                "active"
            );
        }
    );

    document
    .querySelectorAll(
        ".close-modal"
    )
    .forEach(

        button=>{

            button.addEventListener(

                "click",

                closeAllCommercialModals
            );
        }
    );
}

window.addEventListener(

    "click",

    event=>{

        if(
            event.target.classList.contains(
                "commercial-modal"
            )
        ){

            closeAllCommercialModals();
        }
    }
);


async function loadChannels(){

    const response =
    await fetch(
        "/workspace/commercials/channels"
    );

    const channels =
    await response.json();

    const select =
    document.getElementById(
        "channelSelect"
    );

    select.innerHTML =
    '<option value="">Select Channel</option>';

    channels.forEach(

        channel=>{

            select.innerHTML += `

            <option
            value="${channel.id}"
            data-url="${channel.channel_url}"
            >

            ${channel.channel_name}

            </option>

            `;
        }
    );
}

function initializeAddChannel(){

    const form =
    document.getElementById(
        "addChannelForm"
    );

    form?.addEventListener(

        "submit",

        async event=>{

            event.preventDefault();

            const channelName =
            document.getElementById(
                "channelName"
            ).value.trim();

            const channelUrl =
            document.getElementById(
                "channelUrl"
            ).value.trim();

            if(
                !channelName ||
                !channelUrl
            ){

                showToast(
                    "Fill all fields"
                );

                return;
            }

            try{

                const editId =
                form.dataset.editId;

                const response =
                await fetch(

                    editId

                    ?

                    `/workspace/commercials/channel/${editId}`

                    :

                    "/workspace/commercials/add-channel",

                    {

                        method:

                        editId

                        ?

                        "PUT"

                        :

                        "POST",

                        headers:{
                            "Content-Type":"application/json",

                            "X-CSRFToken":
                            document.querySelector(
                                'meta[name="csrf-token"]'
                            )?.content || ""
                        },

                        body:JSON.stringify({

                            channel_name:
                            channelName,

                            channel_url:
                            channelUrl
                        })
                    }
                );

                const result =
                await response.json();

                if(
                    !result.success
                ){

                    showToast(
                        "Failed to save channel"
                    );

                    return;
                }

                form.reset();

                delete form.dataset.editId;

                await loadChannels();

                await loadManageChannels();
                showToast(
                    editId
                    ?
                    "Channel Updated"
                    :
                    "Channel Added"
                );

                closeAllCommercialModals();

            }

            catch(error){

                console.error(
                    error
                );

                showToast(
                    "Something went wrong"
                );
            }
        }
    );
}



/* =========================
   IMAGE PREVIEW
========================= */

function initializeImagePreview(){

    const imageInput =
    document.getElementById(
        "clientImages"
    );

    const previewContainer =
    document.getElementById(
        "imagePreviewContainer"
    );

    if(
        !imageInput ||
        !previewContainer
    ){
        return;
    }

    imageInput.addEventListener(

        "change",

        ()=>{

            previewContainer.innerHTML = "";

            Array.from(
                imageInput.files
            ).forEach(

                file=>{

                    const reader =
                    new FileReader();

                    reader.onload =
                    event=>{

                        const wrapper =
                        document.createElement(
                            "div"
                        );

                        wrapper.style.position =
                        "relative";

                        wrapper.style.display =
                        "inline-block";

                        const image =
                        document.createElement(
                            "img"
                        );

                        image.src =
                        event.target.result;

                        const removeBtn =
                        document.createElement(
                            "button"
                        );

                        removeBtn.innerHTML =
                        "✕";

                        removeBtn.type =
                        "button";

                        removeBtn.style.position =
                        "absolute";

                        removeBtn.style.top =
                        "0";

                        removeBtn.style.right =
                        "0";

                        removeBtn.style.zIndex =
                        "10";

                        removeBtn.onclick =
                        ()=>{

                            wrapper.remove();
                        };

                        wrapper.appendChild(
                            image
                        );

                        wrapper.appendChild(
                            removeBtn
                        );

                        previewContainer.appendChild(
                            wrapper
                        );
                    };

                    reader.readAsDataURL(
                        file
                    );
                }
            );
        }
    );
}

/* =========================
   OPEN CHANNEL LINK
========================= */

function initializeChannelLink(){

    const openLinkBtn =
    document.getElementById(
        "openChannelLink"
    );

    const channelSelect =
    document.getElementById(
        "channelSelect"
    );

    openLinkBtn?.addEventListener(

        "click",

        ()=>{

            const selectedOption =
            channelSelect.options[
                channelSelect.selectedIndex
            ];

            const channelUrl =
            selectedOption?.dataset?.url;

            if(
                !channelUrl
            ){

                showToast(
                    "Select a channel first"
                );

                return;
            }

            window.open(

                channelUrl,

                "_blank"
            );
        }
    );
}

/* =========================
   HELPERS
========================= */

function closeAllCommercialModals(){

    document
    .querySelectorAll(
        ".commercial-modal"
    )
    .forEach(

        modal=>{

            modal.classList.remove(
                "active"
            );
        }
    );
}

/* =========================
   ADD CLIENT
========================= */

function initializeAddClient() {

    const form =
    document.getElementById(
        "addClientForm"
    );

    if (!form) {
        return;
    }

    form.addEventListener(

        "submit",

        async function(event) {

            event.preventDefault();

            const editId =
            form.dataset.editId;

            const formData =
            new FormData();

            formData.append(
                "ad_name",
                document.getElementById(
                    "adName"
                ).value
            );

            formData.append(
                "ad_type",
                document.getElementById(
                    "adType"
                ).value
            );

            formData.append(
                "client_name",
                document.getElementById(
                    "clientName"
                ).value
            );

            formData.append(
                "client_acquisition",
                document.getElementById(
                    "clientAcquisition"
                ).value
            );

            const fileInput =
            document.getElementById(
                "clientImages"
            );

            if(fileInput){

                const files =
                fileInput.files;

                for(
                    let i = 0;
                    i < files.length;
                    i++
                ){

                    formData.append(
                        "sample_images",
                        files[i]
                    );
                }
            }

            try{

                const response =
                await fetch(

                    editId

                    ?

                    `/workspace/commercials/client/${editId}`

                    :

                    "/workspace/commercials/add-client",

                    {

                        method:

                        editId

                        ?

                        "PUT"

                        :

                        "POST",

                        headers:{

                            "X-CSRFToken":

                            document.querySelector(
                                'meta[name="csrf-token"]'
                            )?.content || ""
                        },

                        body:
                        formData
                    }
                );

                const result =
                await response.json();

                if(result.success){

                    form.reset();

                    delete form.dataset.editId;

                    await loadManageClients();

                    showToast(

                        editId

                        ?

                        "Client Updated"

                        :

                        "Client Added"
                    );

                    closeAllCommercialModals();
                }

                else{

                    showToast(
                        "Operation Failed"
                    );
                }

            }

            catch(error){

                console.error(
                    error
                );

                showToast(
                    "Operation Failed"
                );
            }
        }
    );
}

async function loadManageClients(){

    const response =
    await fetch(
        "/workspace/commercials/clients"
    );

    const clients =
    await response.json();

    const tbody =
    document.getElementById(
        "manageClientsTable"
    );

    tbody.innerHTML = "";

    if(
        !clients.length
    ){

        tbody.innerHTML = `

        <tr>

            <td colspan="5">

                No Clients

            </td>

        </tr>

        `;

        return;
    }

    clients.forEach(

        client=>{

            tbody.innerHTML += `

            <tr>

                <td>
                    ${client.ad_name}
                </td>

                <td>
                    ${client.ad_type}
                </td>

                <td>
                    ${client.client_name}
                </td>

                <td>
                    ${client.client_acquisition}
                </td>

                <td>

                    <button
                    onclick="editClient(
                    ${client.id}
                    )"
                    >
                    Edit
                    </button>

                    <button
                    onclick="deleteClient(
                    ${client.id}
                    )"
                    >
                    Delete
                    </button>

                </td>

            </tr>

            `;
        }
    );
}

async function loadManageChannels(){

    const response =
    await fetch(
        "/workspace/commercials/channels"
    );

    const channels =
    await response.json();

    const tbody =
    document.getElementById(
        "manageChannelsTable"
    );

    tbody.innerHTML = "";

    if(
        !channels.length
    ){

        tbody.innerHTML = `

        <tr>

            <td colspan="4">

                No Channels

            </td>

        </tr>

        `;

        return;
    }

    channels.forEach(

        channel=>{

            tbody.innerHTML += `

            <tr>

                <td>
                    ${channel.channel_name}
                </td>

                <td>
                    ${channel.channel_url}
                </td>

                <td>
                    -
                </td>

                <td>

                    <button
                    onclick="editChannel(
                    ${channel.id}
                    )"
                    >
                    Edit
                    </button>

                    <button
                    onclick="deleteChannel(
                    ${channel.id}
                    )"
                    >
                    Delete
                    </button>

                </td>

            </tr>

            `;
        }
    );
}

let pendingDeleteAction =
null;

function showDeleteConfirm(
    message,
    callback
){

    pendingDeleteAction =
    callback;

    const existing =
    document.getElementById(
        "deleteConfirmModal"
    );

    if(existing){

        existing.remove();
    }

    const modal =
    document.createElement(
        "div"
    );

    modal.id =
    "deleteConfirmModal";

    modal.style.position =
    "fixed";

    modal.style.top =
    "0";

    modal.style.left =
    "0";

    modal.style.width =
    "100%";

    modal.style.height =
    "100%";

    modal.style.background =
    "rgba(0,0,0,0.6)";

    modal.style.display =
    "flex";

    modal.style.alignItems =
    "center";

    modal.style.justifyContent =
    "center";

    modal.style.zIndex =
    "999999";

    modal.innerHTML = `

        <div
        style="
        background:#111827;
        padding:24px;
        border-radius:12px;
        min-width:300px;
        text-align:center;
        color:white;
        ">

            <h3>
                ${message}
            </h3>

            <div
            style="
            display:flex;
            gap:10px;
            justify-content:center;
            margin-top:20px;
            ">

                <button
                id="confirmDeleteBtn"
                style="
                padding:10px 20px;
                cursor:pointer;
                ">
                    Delete
                </button>

                <button
                id="cancelDeleteBtn"
                style="
                padding:10px 20px;
                cursor:pointer;
                ">
                    Cancel
                </button>

            </div>

        </div>
    `;

    document.body.appendChild(
        modal
    );

    document
    .getElementById(
        "cancelDeleteBtn"
    )
    .onclick =
    ()=>{

        modal.remove();
    };

    document
    .getElementById(
        "confirmDeleteBtn"
    )
    .onclick =
    ()=>{

        modal.remove();

        if(
            pendingDeleteAction
        ){

            pendingDeleteAction();
        }
    };
}


async function editChannel(id){
    const response =
    await fetch(
        "/workspace/commercials/channels"
    );

    const channels =
    await response.json();

    const channel =
    channels.find(
        x=>Number(x.id)===Number(id)
    );

    console.log(channel);

    if(!channel){
        return;
    }

    const name =
    channel.channel_name;

    const url =
    channel.channel_url;

    document.getElementById(
        "channelName"
    ).value = name;

    document.getElementById(
        "channelUrl"
    ).value = url;

    closeAllCommercialModals();
    document
    .getElementById(
        "addChannelModal"
    )
    .classList.add(
        "active"
    );

    document
    .getElementById(
        "addChannelForm"
    )
    .dataset.editId = id;

    showToast(
        "Edit modal opened"
    );
}

async function editClient(id){

    const response =
    await fetch(
        "/workspace/commercials/clients"
    );

    const clients =
    await response.json();

    const client =
    clients.find(
        x=>Number(x.id)===Number(id)
    );

    console.log(client);

    if(!client){
        return;
    }

    const adName =
    client.ad_name;

    const adType =
    client.ad_type;

    const clientName =
    client.client_name;

    const acquisition =
    client.client_acquisition;

    document.getElementById(
        "adName"
    ).value = adName;

    document.getElementById(
        "adType"
    ).value = adType;

    document.getElementById(
        "clientName"
    ).value = clientName;

    document.getElementById(
        "clientAcquisition"
    ).value = acquisition;

    closeAllCommercialModals();

    document
    .getElementById(
        "addClientModal"
    )
    .classList.add(
        "active"
    );

    document
    .getElementById(
        "addClientForm"
    )
    .dataset.editId = id;

    showToast(
        "Edit modal opened"
    );
}


function showToast(message){

    const existing =
    document.getElementById(
        "commercialToast"
    );

    if(existing){

        existing.remove();
    }

    const toast =
    document.createElement(
        "div"
    );

    toast.id =
    "commercialToast";

    toast.innerText =
    message;

    toast.style.position =
    "fixed";

    toast.style.top =
    "20px";

    toast.style.left =
    "50%";

    toast.style.transform =
    "translateX(-50%)";

    toast.style.zIndex =
    "99999";

    toast.style.padding =
    "12px 20px";

    toast.style.borderRadius =
    "8px";

    toast.style.background =
    "#1f2937";

    toast.style.color =
    "#fff";

    document.body.appendChild(
        toast
    );

    setTimeout(

        ()=>{

            toast.remove();

        },

        3000
    );
}

function initializeCommercialScan(){

    const runBtn =
    document.getElementById(
        "runCommercialScanBtn"
    );

    if(!runBtn){
        return;
    }

    runBtn.addEventListener(

        "click",

        async ()=>{

            const channelId =
            document.getElementById(
                "channelSelect"
            )?.value;

            const videoCount =
            document.getElementById(
                "videoCount"
            )?.value;

            if(!channelId){

                showToast(
                    "Select Channel"
                );

                return;
            }

            try{

                const response =
                await fetch(

                    "/workspace/commercials/run-scan",

                    {

                        method:"POST",

                        headers:{

                            "Content-Type":
                            "application/json",

                            "X-CSRFToken":

                            document.querySelector(
                                'meta[name="csrf-token"]'
                            )?.content || ""
                        },

                        body:JSON.stringify({

                            channel_id:
                            channelId,

                            video_count:
                            parseInt(
                                videoCount
                            ) || 10
                        })
                    }
                );

                const result =
                await response.json();

                if(result.success){

                    showToast(
                        "Commercial Scan Started"
                    );
                }

                else{

                    showToast(
                        result.message ||
                        "Scan Failed"
                    );
                }

            }

            catch(error){

                console.error(
                    error
                );

                showToast(
                    "Scan Failed"
                );
            }
        }
    );
}

function initializeCommercialScanButtons(){

    const runBtn =
    document.getElementById(
        "runCommercialScanBtn"
    );

    const stopBtn =
    document.getElementById(
        "stopCommercialScanBtn"
    );

    runBtn.addEventListener(

        "click",

        async ()=>{

            runBtn.style.display =
            "none";

            stopBtn.style.display =
            "inline-flex";
        }
    );

    stopBtn.addEventListener(

        "click",

        async ()=>{

            await fetch(

                "/workspace/commercials/stop-scan",

                {

                    method:"POST",

                    headers:{

                        "X-CSRFToken":

                        document.querySelector(
                            'meta[name="csrf-token"]'
                        )?.content || ""
                    }
                }
            );

            stopBtn.style.display =
            "none";

            runBtn.style.display =
            "inline-flex";
        }
    );
}