const socket = window.socket;

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

let activeReceiverId = null;


/* =========================
   SOCKET DEBUG
========================= */

socket.on("connect", ()=>{

    console.log(
        "SOCKET CONNECTED:",
        socket.id
    );

    socket.emit("join");
});

socket.on("connect_error", (err)=>{

    console.error(
        "SOCKET ERROR:",
        err
    );
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
   SEND MESSAGE
========================= */

function sendMessage(){

    const message =

    chatMessageInput.value.trim();

    if(

        !message ||

        !activeReceiverId
    ){

        return;
    }

    console.log(
        "SENDING:",
        message
    );

    socket.emit(

        "send_message",

        {

            receiver_id:
            activeReceiverId,

            message:
            message
        }
    );

    chatMessageInput.value = "";
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

        console.log(
            "RECEIVED:",
            data
        );

        const senderId =
        Number(data.sender_id);

        const receiverId =
        Number(data.receiver_id);

        if(

            senderId !== activeReceiverId

            &&

            receiverId !== activeReceiverId
        ){

            return;
        }

        appendMessage(data);

        scrollMessages();
    }
);


/* =========================
   APPEND MESSAGE
========================= */

function appendMessage(data){

    const exists =

    document.querySelector(

        `[data-message-id="${data.id}"]`
    );

    if(exists){

        return;
    }

    const div =
    document.createElement("div");

    div.dataset.messageId =
    data.id;

    const isMine =

        Number(data.sender_id)

        ===

        Number(CURRENT_USER_ID);

    div.className =

        isMine

        ? "chat-message me"

        : "chat-message other";

    div.innerHTML = `

        <div class="chat-message-text">
            ${escapeHtml(data.message)}
        </div>

        <div class="chat-message-time">
            ${data.created_at}
        </div>
    `;

    chatMessages.appendChild(div);
}


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

    chatMessages.scrollTop =
    chatMessages.scrollHeight;
}