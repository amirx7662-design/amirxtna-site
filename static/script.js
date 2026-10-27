async function fetchUsage() {
  const res = await fetch("/api/usage");
  const data = await res.json();
  const used = data.used || {};
  document.getElementById("chatUsed").textContent = used.chat || 0;
  document.getElementById("imageUsed").textContent = used.image || 0;
  document.getElementById("videoUsed").textContent = used.video || 0;
}

async function chatRequest() {
  const prompt = document.getElementById("chatPrompt").value.trim();
  const box = document.getElementById("chatResult");

  if (!prompt) {
    box.textContent = "اكتب سؤالًا أو فكرة أولًا";
    return;
  }

  box.textContent = "جاري الإرسال...";
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  });

  const data = await res.json();
  if (!res.ok) {
    box.textContent = data.error || "حدث خطأ";
    return;
  }

  box.textContent = data.answer;
  fetchUsage();
}

async function imageRequest() {
  const prompt = document.getElementById("imagePrompt").value.trim();
  const box = document.getElementById("imageResult");

  if (!prompt) {
    box.textContent = "اكتب وصف الصورة أولًا";
    return;
  }

  box.textContent = "جاري توليد الصورة...";
  const res = await fetch("/api/image", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  });

  const data = await res.json();
  if (!res.ok) {
    box.textContent = data.error || "حدث خطأ";
    return;
  }

  if (data.result && data.result.url) {
    box.innerHTML = `
      <div>
        <strong>تم إنشاء الصورة بنجاح</strong><br>
        <img src="${data.result.url}" style="max-width:100%; border-radius:12px; margin-top:12px;" />
      </div>
    `;
  } else {
    box.textContent = "تمت العملية بنجاح";
  }

  fetchUsage();
}

async function videoRequest() {
  const prompt = document.getElementById("videoPrompt").value.trim();
  const box = document.getElementById("videoResult");

  if (!prompt) {
    box.textContent = "اكتب وصف الفيديو أولًا";
    return;
  }

  box.textContent = "جاري توليد الفيديو...";
  const res = await fetch("/api/video", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  });

  const data = await res.json();
  if (!res.ok) {
    box.textContent = data.error || "حدث خطأ";
    return;
  }

  const result = data.result || {};
  if (result.url) {
    box.innerHTML = `
      <div>
        <strong>${result.message || "تم إنشاء الفيديو"}</strong><br>
        <video controls style="max-width:100%; border-radius:12px; margin-top:12px;">
          <source src="${result.url}" type="video/mp4" />
        </video>
      </div>
    `;
  } else {
    box.textContent = result.message || "تمت العملية بنجاح";
  }

  fetchUsage();
}

document.getElementById("chatBtn").addEventListener("click", chatRequest);
document.getElementById("imageBtn").addEventListener("click", imageRequest);
document.getElementById("videoBtn").addEventListener("click", videoRequest);

fetchUsage();
