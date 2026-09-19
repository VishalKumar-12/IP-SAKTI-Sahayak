/* ==========================================================================
   chat.js — AI Assistant chat page behavior
   ========================================================================== */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {

        if (
            window.IPSaktiAuth &&
            !window.IPSaktiAuth.requireAuth()
        ) {
            return;
        }

        var messagesEl = document.getElementById('chatMessages');
        var form = document.getElementById('chatForm');
        var input = document.getElementById('chatInput');
        var sendBtn = document.getElementById('sendBtn');
        var answerTemplate = document.getElementById('answerTemplate');
        var quickActions = document.getElementById('quickActions');
        var newChatBtn = document.getElementById('newChatBtn');
        var recentList = document.getElementById('recentList');
        var chatLang = document.getElementById('chatLang');
        var chatJuris = document.getElementById('chatJuris');

        if (!form || !messagesEl) return;

        var currentConversationId = null;

        var WELCOME_HTML =
            '<div class="msg-row assistant">' +
                '<div class="msg-avatar" aria-hidden="true">🌿</div>' +
                '<div class="msg-bubble">' +
                    '<p style="margin:0;">' +
                    'Namaste! Ask me a new question about Ayurveda IPR, ABS, TKDL, classification or international frameworks.' +
                    '</p>' +
                '</div>' +
            '</div>';

        var QUICK_PROMPTS = {
            patent: 'I developed a new Ayurvedic formulation using Ashwagandha. Can I patent it?',
            trademark: 'Can I trademark the name of my Ayurvedic product line?',
            biodiversity: 'What biodiversity clearances apply if I use a wild-harvested plant?',
            abs: 'What Access and Benefit-Sharing rules apply to exporting Neem extract?',
            tkdl: 'Is my Triphala-based formulation already documented as traditional knowledge?',
            regulatory: 'What AYUSH regulatory approvals are needed for a new Ayurvedic product?',
            international: 'Does the Nagoya Protocol apply if I license my formulation abroad?'
        };

        if (input) {
            input.addEventListener('input', function () {
                input.style.height = 'auto';
                input.style.height =
                    Math.min(input.scrollHeight, 140) + 'px';
            });
        }

        if (quickActions) {
            quickActions.addEventListener('click', function (e) {

                var btn = e.target.closest('.quick-action');

                if (!btn) return;

                var topic = btn.getAttribute('data-topic');

                if (QUICK_PROMPTS[topic]) {
                    input.value = QUICK_PROMPTS[topic];
                    input.focus();
                }
            });
        }

        function loadConversations() {

            if (
                !recentList ||
                !window.IPSaktiAPI ||
                typeof window.IPSaktiAPI.getConversations !== 'function'
            ) {
                return;
            }

            window.IPSaktiAPI.getConversations()
                .then(renderConversationList)
                .catch(function (error) {

                    console.error(
                        'Load conversations error:',
                        error
                    );

                    recentList.innerHTML =
                        '<p style="font-size:0.82rem; color:var(--color-text-faint); padding:4px 6px;">' +
                        'Unable to load chat history.' +
                        '</p>';
                });
        }

        function renderConversationList(conversations) {

            if (!recentList) return;

            recentList.innerHTML = '';

            if (!conversations || !conversations.length) {

                recentList.innerHTML =
                    '<p style="font-size:0.82rem; color:var(--color-text-faint); padding:4px 6px;">' +
                    'No conversations yet. Ask a question to get started.' +
                    '</p>';

                return;
            }

            conversations.forEach(function (conversation) {

                var row = document.createElement('div');

                row.className = 'recent-row';

                if (conversation.id === currentConversationId) {
                    row.classList.add('active');
                }

                var btn = document.createElement('button');

                btn.className = 'recent-item';
                btn.type = 'button';
                btn.title = conversation.title;
                btn.textContent =
                    conversation.title ||
                    'Untitled conversation';

                btn.addEventListener('click', function () {
                    openConversation(conversation.id);
                });

                var del = document.createElement('button');

                del.className = 'recent-delete';
                del.type = 'button';
                del.setAttribute(
                    'aria-label',
                    'Delete conversation'
                );

                del.textContent = '✕';

                del.addEventListener('click', function (e) {

                    e.stopPropagation();

                    removeConversation(
                        conversation.id
                    );
                });

                row.appendChild(btn);
                row.appendChild(del);

                recentList.appendChild(row);
            });
        }

        function openConversation(conversationId) {

            if (
                !window.IPSaktiAPI ||
                typeof window.IPSaktiAPI.getConversationMessages !== 'function'
            ) {
                return;
            }

            window.IPSaktiAPI
                .getConversationMessages(conversationId)

                .then(function (conversation) {

                    currentConversationId = conversation.id;

                    messagesEl.innerHTML = '';

                    (conversation.messages || [])
                        .forEach(function (message) {

                            if (message.role === 'user') {

                                appendUserMessage(
                                    message.content || ''
                                );

                            } else if (
                                message.role === 'assistant'
                            ) {

                                var citations =
                                    message.citations || [];

                                if (
                                    typeof citations === 'string'
                                ) {

                                    try {
                                        citations =
                                            JSON.parse(citations);
                                    } catch (error) {
                                        citations = [];
                                    }
                                }

                                if (
                                    !Array.isArray(citations)
                                ) {
                                    citations = [];
                                }

                                appendAssistantAnswer({

                                    answer:
                                        message.content || '',

                                    confidence:
                                        message.confidence ?? 0,

                                    sources:
                                        citations.map(
                                            function (citation) {

                                                return {
                                                    document:
                                                        citation.source ||
                                                        citation.document ||
                                                        'Unknown source',

                                                    page:
                                                        citation.page ??
                                                        null,

                                                    section:
                                                        citation.section ??
                                                        null,

                                                    url:
                                                        citation.url ??
                                                        null
                                                };
                                            }
                                        )
                                });
                            }
                        });

                    loadConversations();
                })

                .catch(function (error) {

                    console.error(
                        'Open conversation error:',
                        error
                    );
                });
        }

        function removeConversation(conversationId) {

            if (
                !window.IPSaktiAPI ||
                typeof window.IPSaktiAPI.deleteConversation !== 'function'
            ) {
                return;
            }

            window.IPSaktiAPI
                .deleteConversation(conversationId)

                .then(function () {

                    if (
                        conversationId ===
                        currentConversationId
                    ) {

                        currentConversationId = null;

                        messagesEl.innerHTML =
                            WELCOME_HTML;
                    }

                    loadConversations();
                })

                .catch(function (error) {

                    console.error(
                        'Delete conversation error:',
                        error
                    );
                });
        }

        loadConversations();

        if (newChatBtn) {

            newChatBtn.addEventListener(
                'click',
                function () {

                    currentConversationId = null;

                    messagesEl.innerHTML =
                        WELCOME_HTML;

                    input.value = '';

                    input.focus();

                    loadConversations();
                }
            );
        }

        form.addEventListener(
            'submit',
            function (e) {

                e.preventDefault();

                var message =
                    input.value.trim();

                if (!message) return;

                submitMessage(message);
            }
        );

        if (input) {

            input.addEventListener(
                'keydown',
                function (e) {

                    if (
                        e.key === 'Enter' &&
                        !e.shiftKey
                    ) {

                        e.preventDefault();

                        form.requestSubmit();
                    }
                }
            );
        }

        function submitMessage(message) {

            appendUserMessage(message);

            input.value = '';

            input.style.height = 'auto';

            sendBtn.disabled = true;

            var typingRow =
                appendTypingIndicator();

            var language =
                chatLang
                    ? chatLang.value
                    : 'en';

            var jurisdiction =
                chatJuris
                    ? chatJuris.value
                    : 'india';

            if (
                !window.IPSaktiAPI ||
                typeof window.IPSaktiAPI.sendChatMessage !== 'function'
            ) {

                typingRow.remove();

                appendErrorMessage();

                sendBtn.disabled = false;

                return;
            }

            window.IPSaktiAPI
                .sendChatMessage(
                    message,
                    language,
                    jurisdiction,
                    currentConversationId
                )

                .then(function (data) {

                    typingRow.remove();

                    if (data.conversation_id) {

                        currentConversationId =
                            data.conversation_id;
                    }

                    if (data.abstained) {

                        appendAbstentionMessage(data);

                    } else {

                        appendAssistantAnswer(data);
                    }

                    loadConversations();
                })

                .catch(function (error) {

                    console.error(
                        'Chat Error:',
                        error
                    );

                    typingRow.remove();

                    var errorMessage =
                        (error && error.message) || '';

                    if (
                        errorMessage
                            .toLowerCase()
                            .indexOf('log in') !== -1 &&
                        window.IPSaktiAuth
                    ) {

                        window.IPSaktiAuth.logout(
                            'login.html'
                        );

                        return;
                    }

                    appendErrorMessage();
                })

                .finally(function () {

                    sendBtn.disabled = false;
                });
        }

        function scrollToBottom() {

            messagesEl.scrollTop =
                messagesEl.scrollHeight;
        }

        function appendUserMessage(text) {

            var row =
                document.createElement('div');

            row.className =
                'msg-row user';

            row.innerHTML =
                '<div class="msg-avatar" aria-hidden="true">🙂</div>' +
                '<div class="msg-bubble"><p></p></div>';

            row.querySelector('p').textContent =
                text;

            messagesEl.appendChild(row);

            scrollToBottom();
        }

        function appendTypingIndicator() {

            var row =
                document.createElement('div');

            row.className =
                'msg-row assistant';

            row.innerHTML =
                '<div class="msg-avatar" aria-hidden="true">🌿</div>' +
                '<div class="msg-bubble typing-indicator">' +
                    '<span></span>' +
                    '<span></span>' +
                    '<span></span>' +
                '</div>';

            messagesEl.appendChild(row);

            scrollToBottom();

            return row;
        }

        function appendAssistantAnswer(data) {
            console.log("CHAT RESPONSE:", data);
            console.log("CONSIDERATIONS:", data.considerations);
            
            var row =
                document.createElement('div');

            row.className =
                'msg-row assistant';

            var avatar =
                document.createElement('div');

            avatar.className =
                'msg-avatar';

            avatar.setAttribute(
                'aria-hidden',
                'true'
            );

            avatar.textContent = '🌿';

            row.appendChild(avatar);

            var fragment =
                answerTemplate.content.cloneNode(true);

            var root =
                fragment.querySelector(
                    '.assistant-response'
                );

            var answerEl =
                root.querySelector(
                    '[data-field="answer"]'
                );

            if (answerEl) {
                answerEl.innerHTML =
                    renderMarkdown(
                        data.answer || ''
                    );
            }

            var whyMattersEl =
                root.querySelector(
                    '[data-field="whyMatters"]'
                );

            if (whyMattersEl) {
                whyMattersEl.innerHTML =
                    renderMarkdown(
                        data.why_this_matters || ''
                    );
            }

            var considerationsEl =
                root.querySelector(
                    '[data-field="considerations"]'
                );

            if (considerationsEl) {

                (data.considerations || [])
                    .forEach(function (item) {

                        var li =
                            document.createElement('li');

                        li.textContent = item;

                        li.style.marginBottom =
                            '6px';

                        considerationsEl.appendChild(li);
                    });
            }

            var sourcesEl =
                root.querySelector(
                    '[data-field="sources"]'
                );

            if (sourcesEl) {
                renderSources(
                    sourcesEl,
                    data.sources || []
                );
            }

            renderConfidence(
                root,
                data.confidence || 0,
                data.confidence_level
            );

            var actions =
                root.querySelectorAll(
                    '.result-actions button'
                );

            actions.forEach(function (btn) {

                btn.addEventListener(
                    'click',
                    function () {

                        handleResultAction(
                            btn,
                            data
                        );
                    }
                );
            });

            row.appendChild(fragment);

            messagesEl.appendChild(row);

            scrollToBottom();
        }

        function renderMarkdown(text) {

            if (!text) return '';

            return text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/^### (.*)$/gm, '<h5>$1</h5>')
                .replace(/^## (.*)$/gm, '<h4>$1</h4>')
                .replace(/^# (.*)$/gm, '<h3>$1</h3>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/^\s*[-•]\s+(.*)$/gm, '<li>$1</li>')
                .replace(/^\s*(\d+)\.\s+(.*)$/gm,
                    '<li><strong>$1.</strong> $2</li>'
                )
                .replace(/\n\n/g, '<br><br>')
                .replace(/\n/g, '<br>');
        }

        function renderSources(container, sources) {

            if (!container) return;

            container.innerHTML = '';

            if (
                !sources ||
                !sources.length
            ) {

                container.innerHTML =
                    '<div class="state-box" style="padding:18px;">' +
                        '<p style="margin:0;font-size:0.88rem;">' +
                            'No supporting sources were found for this answer.' +
                        '</p>' +
                    '</div>';

                return;
            }

            sources.forEach(function (src) {

                var item =
                    document.createElement('div');

                item.className =
                    'source-item';

                item.innerHTML =
                    '<span class="source-icon" aria-hidden="true">📄</span>' +
                    '<div><strong></strong><span></span></div>';

                item.querySelector(
                    'strong'
                ).textContent =
                    src.document ||
                    'Unknown source';

                var meta = [];

                if (src.section) {
                    meta.push(src.section);
                }

                if (src.page) {
                    meta.push(
                        'Page ' + src.page
                    );
                }

                item.querySelector(
                    'span'
                ).textContent =
                    meta.join(' · ');

                if (src.url) {

                    item.style.cursor =
                        'pointer';

                    item.onclick =
                        function () {

                            var url =
                                src.url;

                            if (
                                src.page &&
                                url.indexOf(
                                    '#page='
                                ) === -1
                            ) {

                                url +=
                                    '#page=' +
                                    src.page;
                            }

                            window.open(
                                url,
                                '_blank',
                                'noopener,noreferrer'
                            );
                        };
                }

                container.appendChild(item);
            });
        }

        function renderConfidence(
            root,
            score,
            level
        ) {

            var pct =
                Math.round(
                    (score || 0) * 100
                );

            if (!level) {

                if (score >= 0.75) {
                    level = 'high';
                } else if (score >= 0.50) {
                    level = 'medium';
                } else {
                    level = 'low';
                }
            }

            var confidenceValue =
                root.querySelector(
                    '[data-field="confidenceValue"]'
                );

            if (confidenceValue) {
                confidenceValue.textContent =
                    pct + '%';
            }

            var levelEl =
                root.querySelector(
                    '[data-field="confidenceLevel"]'
                );

            if (levelEl) {

                levelEl.textContent =
                    level.charAt(0).toUpperCase() +
                    level.slice(1);

                levelEl.className =
                    'confidence-level ' +
                    level;
            }

            var bar =
                root.querySelector(
                    '[data-field="confidenceBar"]'
                );

            if (bar) {

                bar.className =
                    'confidence-bar ' +
                    level;

                var span =
                    bar.querySelector('span');

                if (span) {
                    span.style.width =
                        pct + '%';
                }
            }
        }

        function appendAbstentionMessage(data) {

            var row =
                document.createElement('div');

            row.className =
                'msg-row assistant';

            row.innerHTML =
                '<div class="msg-avatar" aria-hidden="true">🌿</div>' +
                '<div class="assistant-response">' +
                    '<div class="state-box state-low">' +
                        '<div class="state-icon">🤔</div>' +
                        '<h4>Insufficient evidence to answer reliably</h4>' +
                        '<p></p>' +
                    '</div>' +
                '</div>';

            row.querySelector('p').textContent =
                data.message ||
                data.answer ||
                'I could not find sufficient information in the available sources.';

            messagesEl.appendChild(row);

            scrollToBottom();
        }

        function appendErrorMessage() {

            var row =
                document.createElement('div');

            row.className =
                'msg-row assistant';

            row.innerHTML =
                '<div class="msg-avatar" aria-hidden="true">🌿</div>' +
                '<div class="assistant-response">' +
                    '<div class="state-box state-error">' +
                        '<div class="state-icon">⚠️</div>' +
                        '<h4>Something went wrong</h4>' +
                        '<p>The assistant could not reach the backend. Please try again in a moment.</p>' +
                    '</div>' +
                '</div>';

            messagesEl.appendChild(row);

            scrollToBottom();
        }

        function handleResultAction(
            btn,
            data
        ) {

            var action =
                btn.getAttribute(
                    'data-action'
                );

            if (action === 'copy') {

                var text =
                    data.answer || '';

                if (navigator.clipboard) {

                    navigator.clipboard
                        .writeText(text)
                        .catch(function () {});
                }

                var original =
                    btn.textContent;

                btn.textContent =
                    'Copied ✓';

                setTimeout(
                    function () {

                        btn.textContent =
                            original;

                    },
                    1500
                );
            }

            else if (
                action === 'view-source'
            ) {

                if (
                    data.sources &&
                    data.sources[0] &&
                    data.sources[0].url
                ) {

                    window.open(
                        data.sources[0].url,
                        '_blank',
                        'noopener,noreferrer'
                    );
                }
            }

            else if (
                action === 'helpful' ||
                action === 'not-helpful'
            ) {

                if (
                    window.IPSaktiAPI &&
                    typeof window.IPSaktiAPI.sendFeedback === 'function'
                ) {

                    window.IPSaktiAPI.sendFeedback({
                        helpful:
                            action === 'helpful',
                        message:
                            data.answer
                    });
                }

                btn.disabled = true;

                btn.textContent =
                    action === 'helpful'
                        ? '👍 Thanks!'
                        : '👎 Noted';
            }
        }
    });
})();