document.addEventListener("DOMContentLoaded", () => {
    console.log("EduLearn Loaded Successfully");
});

async function sendMessage() {

    const input = document.getElementById("userInput");
    const message = input.value.trim();

    if (message === "") return;

    const chatBox = document.getElementById("chat-messages");

    chatBox.innerHTML += `
        <div><b>You:</b> ${message}</div>
    `;

    input.value = "";

    try {

        const response = await fetch(
            "https://edulearn-mo38.onrender.com/chat",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: message
                })
            }
        );

        const data = await response.json();

        chatBox.innerHTML += `
            <div><b>AI:</b> ${data.reply}</div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {

        console.error(error);

        chatBox.innerHTML += `
            <div style="color:red;">
                Cannot connect to backend.
            </div>
        `;
    }
}