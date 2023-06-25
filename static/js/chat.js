const all = document.querySelector(".content");
const content = document.querySelector(".conversation-wrapper");
const message = document.querySelector("#message-text");
let messageCount = 0;

const addChatBubble = (message, sender, type) => {
  messageCount += 1;
  let messageSent = document.createElement("div");
  let messageSentBubble = document.createElement("div");
  let messageSentTime = document.createElement("div");
  let messageSentAvatar = document.createElement("div");
  let messageSentTimestamp = document.createElement("div");
  let messageSentStatus = document.createElement("div");

  messageSent.className = type;
  messageSentBubble.className = "bubble";
  messageSentBubble.classList.add("m" + messageCount);
  messageSentTime.className = "time";
  messageSentTimestamp.className = "timestamp";
  messageSentAvatar.className = "avatar";
  messageSentStatus.className = "status";

  messageSentBubble.innerHTML = message;
  messageSentAvatar.innerHTML = sender;
  messageSentTime.innerHTML = new Date().toLocaleTimeString([], {
    hour12: false,
  });

  messageSentTime.appendChild(messageSentStatus);
  messageSentTimestamp.appendChild(messageSentTime);
  messageSentTimestamp.appendChild(messageSentAvatar);

  messageSent.appendChild(messageSentBubble);
  messageSent.appendChild(messageSentTimestamp);

  const shouldScroll =
    content.scrollTop + content.clientHeight === content.scrollHeight;

  content.appendChild(messageSent);

  if (!shouldScroll) {
    content.scrollTop = content.scrollHeight;
  }
};

const updateChatBubble = (newMessage) => {
  latest = document.getElementsByClassName("m" + messageCount)[0];
  latest.innerHTML = newMessage;
};

const handleBotResponse = async (event) => {
  event.preventDefault();

  // ================ USER MESSAGE ================
  addChatBubble(message.value, "ME", "message-sent");

  // ================ BOT MESSAGE ================
  addChatBubble('<div class="loader"></div>', "RLB", "message-received");

  let res = await fetch("http://localhost:5000/send", {
    method: "POST",
    body: JSON.stringify({ message: message.value }),
    headers: {
      "Content-Type": "application/json",
    },
    redirect: "follow",
  });
  message.value = "";
  res = await res.json();
  res.answer = res.answer.replaceAll("\n", "<br>");

  updateChatBubble(res.answer);
};

message.addEventListener("keydown", async (event) => {
  if (event.code === "Enter") {
    handleBotResponse(event);
  }
});

document.querySelector(".send").addEventListener("click", async (event) => {
  handleBotResponse(event);
});

document.querySelector(".help").addEventListener("click", (event) => {
  event.preventDefault();

  let messageHelp = document.createElement("div");
  let messageHelpText = document.createElement("div");

  messageHelp.className = "message-help";
  messageHelpText.className = "help";

  messageHelpText.innerHTML =
    "<p>Poți avea o discuție lejeră cu mine! Încearcă să îmi spui ceva!</p><p>Sunt specializat în orice lege! Întreaba-mă despre ce ți-ar plăcea să aflii!</p><p>Îți pot spune despre: Constituție, Codul Civil și cel de Procedură Civilă, Codul Fiscal și cel de Procedură Fiscală, Codul Penal și cel de Procedură Penală, Codul Muncii, Codul Administrativ.</p>";
  messageHelp.appendChild(messageHelpText);

  content.appendChild(messageHelp);
});
