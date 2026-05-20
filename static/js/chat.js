const socket = window.socket;

const csrfToken = document
.querySelector(
    'meta[name="csrf-token"]'
)
?.getAttribute("content");


const chatFab =
document.getElementById("chatFab");

const chatDrawer =
document.getElementById("chatDrawer");

const closeChatDrawer =
document.getElementById("closeChatDrawer");

const chatConversation =
document.getElementById("chatConversation");

const activeChatUser =
document.getElementById("activeChatUser");

const chatMessages =
document.getElementById("chatMessages");

const sendChatMessage =
document.getElementById("sendChatMessage");

const chatMessageInput =
document.getElementById("chatMessageInput");

const chatUserSearch =
document.getElementById("chatUserSearch");

const attachChatFile =
document.getElementById("attachChatFile");

const chatFileInput =
document.getElementById("chatFileInput");

let activeReceiverId = null;

let uploadedFile = null;


/* =========================
   SOCKET CONNECT
========================= */

socket.on("connect", ()=>{

    console.log(
        "SOCKET CONNECTED:",
        socket.id
    );

    if(activeReceiverId){

        socket.emit(
            "join_chat",
            {
                receiver_id:
                activeReceiverId
            }
        );
    }
});


/* =========================
   OPEN DRAWER
========================= */

chatFab?.addEventListener(

    "click",

    (e)=>{

        e.stopPropagation();

        chatDrawer.classList.toggle(
            "active"
        );
    }
);


/* =========================
   CLOSE DRAWER
========================= */

closeChatDrawer?.addEventListener(

    "click",

    ()=>{

        chatDrawer.classList.remove(
            "active"
        );

        chatConversation.style.display =
        "none";
    }
);


/* =========================
   SEARCH USERS
========================= */

chatUserSearch?.addEventListener(

    "input",

    ()=>{

        const value =

        chatUserSearch.value
        .toLowerCase();

        document
        .querySelectorAll(
            ".chat-user-item"
        )
        .forEach(item=>{

            const name =

            (
                item.dataset.name || ""
            ).toLowerCase();

            item.style.display =

                name.includes(value)

                ? "flex"

                : "none";
        });
    }
);


/* =========================
   OPEN USER CHAT
========================= */

document.addEventListener(

    "click",

    async (e)=>{

        const item =

        e.target.closest(
            ".chat-user-item"
        );

        if(!item){

            return;
        }

        activeReceiverId = Number(
            item.dataset.userId
        );

        activeChatUser.innerText =
        item.dataset.name;

        chatConversation.style.display =
        "flex";

        socket.emit(
            "join_chat",
            {
                receiver_id:
                activeReceiverId
            }
        );

        await loadMessages();
    }
);


/* =========================
   LOAD MESSAGES
========================= */

async function loadMessages(){

    if(!activeReceiverId){

        return;
    }

    try{

        const response = await fetch(

            `/chat/messages/${activeReceiverId}`
        );

        const messages =
        await response.json();

        chatMessages.innerHTML = "";

        messages.forEach(msg=>{

            appendMessage(msg);
        });

        scrollMessages();
    }

    catch(error){

        console.error(
            "LOAD FAILED:",
            error
        );
    }
}


/* =========================
   FILE ATTACH
========================= */

attachChatFile?.addEventListener(

    "click",

    ()=>{

        chatFileInput.click();
    }
);


chatFileInput?.addEventListener(

    "change",

    async ()=>{

        const file =
        chatFileInput.files[0];

        if(!file){

            return;
        }

        const formData =
        new FormData();

        formData.append(
            "file",
            file
        );

        try{

            const response =
            await fetch(

                "/chat/upload",

                {
                    method:"POST",
                    headers:{

                        "X-CSRFToken":
                        csrfToken
                },

                    body:formData
                }
            );

            const data =
            await response.json();

            if(!data.success){

                alert(
                    data.message ||
                    "Upload failed"
                );

                return;
            }

            uploadedFile =
            data.file;

            console.log(
                "FILE READY:",
                uploadedFile
            );
        }

        catch(error){

            console.error(error);

            alert(
                "Upload failed"
            );
        }
    }
);


fetch(

    "/chat/archive",

    {

        method:"POST",

        headers:{

            "Content-Type":
            "application/json",

            "X-CSRFToken":
            csrfToken
        },

        body:JSON.stringify(data)
    }
)

/* =========================
   SEND MESSAGE
========================= */

function sendMessage(){

    const message =

    chatMessageInput.value.trim();

    if(

        !message

        &&

        !uploadedFile
    ){

        return;
    }

    if(!activeReceiverId){

        return;
    }

    socket.emit(

        "send_message",

        {

            receiver_id:
            activeReceiverId,

            message:
            message,

            file:
            uploadedFile
        }
    );

    chatMessageInput.value = "";

    uploadedFile = null;

    chatFileInput.value = "";
}


sendChatMessage?.addEventListener(

    "click",

    sendMessage
);


chatMessageInput?.addEventListener(

    "keypress",

    (e)=>{

        if(e.key === "Enter"){

            e.preventDefault();

            sendMessage();
        }
    }
);


/* =========================
   RECEIVE MESSAGE
========================= */

socket.on(

    "receive_message",

    (data)=>{

        if(

            Number(data.sender_id)

            !==

            activeReceiverId

            &&

            Number(data.receiver_id)

            !==

            activeReceiverId
        ){

            return;
        }

        appendMessage(data);
    }
);


/* =========================
   DELETE MESSAGE
========================= */

socket.on(

    "message_deleted",

    (data)=>{

        const element =

        document.querySelector(

            `[data-message-id="${data.message_id}"]`
        );

        if(element){

            element.remove();
        }
    }
);


/* =========================
   CLEAR CHAT
========================= */

socket.on(

    "chat_cleared",

    ()=>{

        chatMessages.innerHTML = "";
    }
);


/* =========================
   APPEND MESSAGE
========================= */

function appendMessage(data){

    if(!data){

        return;
    }

    if(data.deleted){

        return;
    }

    const existing =

    document.querySelector(

        `[data-message-id="${data.id}"]`
    );

    if(existing){

        return;
    }

    const div =
    document.createElement("div");

    div.className =

        Number(data.sender_id)

        ===

        Number(CURRENT_USER_ID)

        ? "chat-message me"

        : "chat-message other";

    div.dataset.messageId =
    data.id;

    let fileHtml = "";

    if(data.file_url){

        const extension =

        (
            data.file_type || ""
        ).toLowerCase();

        const imageExtensions = [

            "png",
            "jpg",
            "jpeg",
            "gif",
            "webp"
        ];

        if(

            imageExtensions.includes(
                extension
            )
        ){

            fileHtml = `

                <img
                src="${data.file_url}"
                class="chat-image-preview">
            `;
        }

        else{

            fileHtml = `

                <a
                href="${data.file_url}"
                target="_blank"
                class="chat-file-link">

                    📎 ${escapeHtml(data.file_name)}

                </a>
            `;
        }
    }

    const actionsMenu =

        Number(data.sender_id)

        ===

        Number(CURRENT_USER_ID)

        ?

        `

        <div class="chat-message-actions">

            <button
            class="chat-message-menu-btn">

                <i data-lucide="chevron-down"></i>

            </button>

            <div class="chat-message-dropdown">

                <button
                onclick="copyMessage('${escapeHtml(data.message || "")}')">

                    Copy Message

                </button>

                <button
                onclick="deleteMessage(${data.id})">

                    Delete Message

                </button>

                <button>

                    Forward

                </button>

            </div>

        </div>

        `

        :

        "";

    div.innerHTML = `

        <div class="chat-message-bubble">

            ${actionsMenu}

            ${fileHtml}

            <div class="chat-message-text">

                ${escapeHtml(data.message || "")}

            </div>

            <div class="chat-message-footer">

                <div class="chat-message-time">

                    ${data.created_at}

                </div>

            </div>

        </div>
    `;

    chatMessages.appendChild(div);

    if(window.lucide){

        lucide.createIcons();
    }

    scrollMessages();
}

/* =========================
   MESSAGE DROPDOWN
========================= */

document.addEventListener(

    "click",

    (e)=>{

        const btn = e.target.closest(
            ".chat-message-menu-btn"
        );

        document
        .querySelectorAll(
            ".chat-message-dropdown"
        )
        .forEach(drop=>{

            if(

                !drop.contains(e.target)
            ){

                drop.classList.remove(
                    "active"
                );
            }
        });

        if(!btn){

            return;
        }

        e.stopPropagation();

        const dropdown =

        btn.parentElement.querySelector(
            ".chat-message-dropdown"
        );

        dropdown.classList.toggle(
            "active"
        );
    }
);


/* =========================
   COPY MESSAGE
========================= */

window.copyMessage = function(message){

    navigator.clipboard.writeText(
        message
    );
};


/* =========================
   BACK BUTTON
========================= */

document.getElementById(
    "backToUsers"
)?.addEventListener(

    "click",

    ()=>{

        chatConversation.style.display =
        "none";
    }
);

/* =========================
   DELETE MESSAGE
========================= */

window.deleteMessage = function(id){

    socket.emit(

        "delete_message",

        {
            message_id:id
        }
    );
};


/* =========================
   CLEAR CHAT FUNCTION
========================= */

window.clearCurrentChat = function(){

    if(!activeReceiverId){

        return;
    }

    const confirmed = confirm(
        "Clear this conversation?"
    );

    if(!confirmed){

        return;
    }

    socket.emit(

        "clear_chat",

        {
            receiver_id:
            activeReceiverId
        }
    );
};


/* =========================
   ESCAPE HTML
========================= */

function escapeHtml(text){

    const div =
    document.createElement("div");

    div.innerText = text;

    return div.innerHTML;
}


/* =========================
   AUTO SCROLL
========================= */

function scrollMessages(){

    requestAnimationFrame(()=>{

        chatMessages.scrollTop =
        chatMessages.scrollHeight;
    });
}


/* =========================
   CHAT MENU
========================= */

const chatMenuBtn =
document.getElementById(
    "chatMenuBtn"
);

const chatMenuDropdown =
document.getElementById(
    "chatMenuDropdown"
);

chatMenuBtn?.addEventListener(

    "click",

    (e)=>{

        e.stopPropagation();

        chatMenuDropdown.classList.toggle(
            "active"
        );
    }
);

document.addEventListener(

    "click",

    ()=>{

        chatMenuDropdown?.classList.remove(
            "active"
        );

        document
        .querySelectorAll(
            ".chat-message-dropdown"
        )
        .forEach(drop=>{

            drop.classList.remove(
                "active"
            );
        });
    }
);


const viewProfileBtn =
document.getElementById(
    "viewProfileBtn"
);

viewProfileBtn?.addEventListener(

    "click",

    async ()=>{

        const response = await fetch(

            `/chat/user/${activeReceiverId}`
        );

        const user =
        await response.json();

        document.getElementById(
            "chatProfileModal"
        ).classList.add("active");

        document.getElementById(
            "chatProfileAvatar"
        ).src =
        user.profile_image || "";

        document.getElementById(
            "chatProfileBanner"
        ).src =
        user.banner || "";

        document.getElementById(
            "chatProfileFullName"
        ).innerText =
        user.full_name || "";

        document.getElementById(
            "chatProfileFirstName"
        ).innerText =
        user.first_name || "";

        document.getElementById(
            "chatProfileLastName"
        ).innerText =
        user.last_name || "";

        document.getElementById(
            "chatProfileEmail"
        ).innerText =
        user.email || "";

        document.getElementById(
            "chatProfileEmployeeId"
        ).innerText =
        user.employee_id || "";

        document.getElementById(
            "chatProfileRole"
        ).innerText =
        user.role || "";
    }
);

document.getElementById(
    "closeChatProfile"
)?.addEventListener(

    "click",

    ()=>{

        document.getElementById(
            "chatProfileModal"
        ).classList.remove(
            "active"
        );
    }
);