const MOCK_MODE = false;

// const API_BASE_URL = "http://127.0.0.1:5000/api";
const API_BASE_URL = "/api";

/* ==========================================================================
   Authentication Headers
   ========================================================================== */

function authHeaders() {
    const headers = {
        "Content-Type": "application/json"
    };

    if (
        window.IPSaktiAuth &&
        typeof window.IPSaktiAuth.getToken === "function"
    ) {
        const token = window.IPSaktiAuth.getToken();

        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }
    }

    return headers;
}


/* ==========================================================================
   Safe API Request
   ========================================================================== */

async function apiRequest(url, options = {}) {

    let response;

    try {
        response = await fetch(url, options);
    } catch (error) {

        console.error("Network error:", error);

        throw new Error(
            "Unable to connect to the server. " +
            "Please check your connection or make sure the backend is running."
        );
    }

    let data;

    try {

        const contentType =
            response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {

            const text = await response.text();

            console.error(
                "Invalid server response:",
                text.substring(0, 500)
            );

            throw new Error(
                "The server returned an invalid response."
            );
        }

        data = await response.json();

    } catch (error) {

        console.error(
            "Response parsing error:",
            error
        );

        throw new Error(
            "The server returned an invalid response. Please try again."
        );
    }

    if (!response.ok) {

        throw new Error(
            data?.error ||
            data?.message ||
            `Server error (${response.status}).`
        );
    }

    return data;
}


/* ==========================================================================
   Chat
   ========================================================================== */

async function sendMessage(
    message,
    language,
    jurisdiction,
    conversationId
) {

    const data = await apiRequest(
        `${API_BASE_URL}/chat`,
        {
            method: "POST",

            headers: authHeaders(),

            body: JSON.stringify({
                message: message,
                language: language || "en",
                jurisdiction: jurisdiction || "india",

                // Important:
                // Existing conversation continues here.
                conversation_id:
                    conversationId || null
            })
        }
    );

    return {

        success:
            data.success,

        answer:
            data.answer || "",

        confidence:
            data.confidence ?? 0,

        conversation_id:
            data.conversation_id || null,

        sources:
            (data.citations || []).map(
                function (citation) {

                    return {

                        document:
                            citation.source ||
                            "Unknown source",

                        page:
                            citation.page ??
                            null,

                        section:
                            citation.section ||
                            null,

                        url:
                            citation.url ||
                            null
                    };
                }
            )
    };
}


/* ==========================================================================
   Chat History
   ========================================================================== */


/*
 * Get all conversations of
 * currently logged-in user.
 */
async function getConversations() {

    const data = await apiRequest(
        `${API_BASE_URL}/chat/conversations`,
        {
            method: "GET",
            headers: authHeaders()
        }
    );

    return data.conversations || [];
}


/*
 * Get complete conversation.
 *
 * This returns:
 *
 * User question
 * Assistant answer
 * User question
 * Assistant answer
 *
 * along with citations and confidence.
 */
async function getConversationMessages(
    conversationId
) {

    if (!conversationId) {

        throw new Error(
            "Conversation ID is required."
        );
    }

    const data = await apiRequest(
        `${API_BASE_URL}/chat/conversations/${conversationId}`,
        {
            method: "GET",
            headers: authHeaders()
        }
    );

    if (!data.conversation) {

        throw new Error(
            "Conversation data is missing from the server response."
        );
    }

    return data.conversation;
}


/*
 * Delete complete conversation
 * including its messages.
 */
async function deleteConversation(
    conversationId
) {

    if (!conversationId) {

        throw new Error(
            "Conversation ID is required."
        );
    }

    await apiRequest(
        `${API_BASE_URL}/chat/conversations/${conversationId}`,
        {
            method: "DELETE",
            headers: authHeaders()
        }
    );

    return true;
}


/* ==========================================================================
   ABS Analysis
   ========================================================================== */

async function analyzeABS(data) {

    const result = await apiRequest(
        `${API_BASE_URL}/abs`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                query:
                    `${data.resource}. ` +
                    `Resource type: ${data.resourceType}. ` +
                    `Purpose: ${data.purpose}. ` +
                    `Jurisdiction: ${data.jurisdiction}`
            })
        }
    );

    return {

        success:
            result.success,

        resource:
            data.resource,

        access:
            result.answer || "",

        benefit_sharing:
            "",

        traditional_knowledge:
            "",

        framework:
            result.disclaimer || "",

        sources:
            (result.citations || []).map(
                function (citation) {

                    var source =
                        citation.source || "";

                    var url;

                    if (
                        source ===
                        "https://nbaindia.org/" ||

                        source ===
                        "http://nbaindia.org/"
                    ) {

                        url =
                            "https://www.nbaindia.nic.in/";

                    }

                    else if (
                        source.startsWith("http://") ||

                        source.startsWith("https://")
                    ) {

                        url =
                            source;

                    }

                    else {

                        url =
                            `${API_BASE_URL}/source?file=` +
                            `${encodeURIComponent(source)}` +
                            `&page=` +
                            `${encodeURIComponent(
                                citation.page ?? ""
                            )}`;
                    }

                    return {

                        document:
                            source ||
                            "Unknown source",

                        page:
                            citation.page ??
                            null,

                        section:
                            citation.section ||
                            null,

                        url:
                            url
                    };
                }
            ),

        confidence:
            result.confidence ?? 0,

        confidence_level:
            (result.confidence ?? 0) >= 0.75

                ? "high"

                : (result.confidence ?? 0) >= 0.50

                    ? "medium"

                    : "low"
    };
}


/* ==========================================================================
   Traditional Knowledge / TKDL
   ========================================================================== */

async function checkTraditionalKnowledge(
    query
) {

    const result = await apiRequest(
        `${API_BASE_URL}/tkdl`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                query: query
            })
        }
    );

    return {

        success:
            result.success,

        query:
            result.query ||
            query,

        answer:
            result.answer ||
            "",

        sources:
            result.sources ||
            [],

        confidence:
            result.confidence ??
            0,

        disclaimer:
            result.disclaimer ||
            ""
    };
}


/* ==========================================================================
   Sources
   ========================================================================== */

async function getSources() {

    return [

        {
            name:
                "Patents Act, 1970",

            jurisdiction:
                "India",

            category:
                "Patent",

            type:
                "Act",

            version:
                "1970",

            url:
                "https://ipindia.gov.in/resource/patents-resources-act"
        },

        {
            name:
                "Patents Rules, 2003",

            jurisdiction:
                "India",

            category:
                "Patent",

            type:
                "Rules",

            version:
                "2003",

            url:
                "https://ipindia.gov.in/resource/patents-resources-rules"
        },

        {
            name:
                "Trade Marks Act",

            jurisdiction:
                "India",

            category:
                "Trademark",

            type:
                "Act",

            version:
                "1999",

            url:
                "https://ipindia.gov.in/trade-marks-resources-act"
        },

        {
            name:
                "Geographical Indications Act",

            jurisdiction:
                "India",

            category:
                "GI",

            type:
                "Act",

            version:
                "1999",

            url:
                "https://ipindia.gov.in/geographical-indications-resources-act"
        },

        {
            name:
                "Copyright Act, 1957",

            jurisdiction:
                "India",

            category:
                "Copyright",

            type:
                "Act",

            version:
                "1957",

            url:
                "https://www.copyright.gov.in/Copyright_Act_1957/"
        },

        {
            name:
                "Ministry of AYUSH",

            jurisdiction:
                "India",

            category:
                "AYUSH",

            type:
                "Guideline",

            version:
                "Current",

            url:
                "https://ayush.gov.in/"
        },

        {
            name:
                "TKDL",

            jurisdiction:
                "India",

            category:
                "Traditional Knowledge",

            type:
                "Guideline",

            version:
                "Current",

            url:
                "https://www.tkdl.res.in/"
        },

        {
            name:
                "WIPO Traditional Knowledge",

            jurisdiction:
                "International",

            category:
                "International",

            type:
                "Treaty",

            version:
                "Current",

            url:
                "https://www.wipo.int/en/web/traditional-knowledge/"
        }
    ];
}


/* ==========================================================================
   Public API
   ========================================================================== */

window.IPSaktiAPI = {

    /* Chat */
    sendChatMessage:
        sendMessage,

    /* Chat History */
    getConversations:
        getConversations,

    getConversationMessages:
        getConversationMessages,

    deleteConversation:
        deleteConversation,

    /* Other APIs */
    analyzeABS:
        analyzeABS,

    checkTraditionalKnowledge:
        checkTraditionalKnowledge,

    getSources:
        getSources
};