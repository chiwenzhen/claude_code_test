// 评论表单 AJAX 提交
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".comment-form");
    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const slug = form.dataset.slug;
        const nameInput = form.querySelector("#comment-name");
        const contentInput = form.querySelector("#comment-content");
        const messageEl = form.querySelector(".form-message");
        const submitBtn = form.querySelector(".btn-submit");

        const name = nameInput.value.trim();
        const content = contentInput.value.trim();

        // 简单验证
        if (!name || !content) {
            messageEl.textContent = "请填写昵称和评论内容";
            messageEl.className = "form-message error";
            return;
        }

        // 禁用按钮
        submitBtn.disabled = true;
        submitBtn.textContent = "提交中...";
        messageEl.textContent = "";

        try {
            const formData = new FormData();
            formData.append("name", name);
            formData.append("content", content);

            const response = await fetch(`/comment/${slug}`, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                // 添加评论到列表
                const commentList = document.querySelector(".comment-list");
                const noComments = document.querySelector(".no-comments");

                if (noComments) {
                    noComments.remove();
                    const listDiv = document.createElement("div");
                    listDiv.className = "comment-list";
                    document.querySelector(".comments-section h2").after(listDiv);
                }

                const list = document.querySelector(".comment-list");
                const commentDiv = document.createElement("div");
                commentDiv.className = "comment";
                commentDiv.innerHTML = `
                    <div class="comment-header">
                        <strong>${escapeHtml(data.name)}</strong>
                        <time>${data.date}</time>
                    </div>
                    <div class="comment-body">${escapeHtml(data.content)}</div>
                `;
                list.appendChild(commentDiv);

                // 更新评论数
                const h2 = document.querySelector(".comments-section h2");
                const count = list.children.length;
                h2.textContent = `评论 (${count})`;

                // 清空表单
                nameInput.value = "";
                contentInput.value = "";
                messageEl.textContent = "评论提交成功！";
                messageEl.className = "form-message success";
            } else {
                messageEl.textContent = data.error || "提交失败，请稍后重试";
                messageEl.className = "form-message error";
            }
        } catch (err) {
            messageEl.textContent = "网络错误，请稍后重试";
            messageEl.className = "form-message error";
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "提交评论";
        }
    });
});

// HTML 转义
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}
