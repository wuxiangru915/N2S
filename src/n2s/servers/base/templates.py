"""
HTML templates for N2S Agent servers.
"""

from typing import Optional


def get_n2s_component_script(
    dev_mode: bool = False,
    static_path: str = "/static",
    cdn_url: str = "https://img.n2s.ai/n2s-components.js",
) -> str:
    """Get the script tag for loading N2S web components.

    Args:
        dev_mode: If True, load from local static files
        static_path: Path to static assets in dev mode
        cdn_url: CDN URL for production

    Returns:
        HTML script tag for loading components
    """
    if dev_mode:
        return f'<script type="module" src="{static_path}/n2s-components.js"></script>'
    else:
        return f'<script type="module" src="{cdn_url}"></script>'


def get_index_html(
    dev_mode: bool = False,
    static_path: str = "/static",
    cdn_url: str = "https://img.n2s.ai/n2s-components.js",
    api_base_url: str = "",
) -> str:
    """Generate index HTML with configurable component loading.

    Args:
        dev_mode: If True, load components from local static files
        static_path: Path to static assets in dev mode
        cdn_url: CDN URL for production components
        api_base_url: Base URL for API endpoints

    Returns:
        Complete HTML page as string
    """
    component_script = get_n2s_component_script(dev_mode, static_path, cdn_url)

    early_lang_script = """
    <script>
    (function() {
        const getCookie = (name) => {
            const value = '; ' + document.cookie;
            const parts = value.split('; ' + name + '=');
            return parts.length === 2 ? parts.pop().split(';').shift() : null;
        };
        const savedLang = getCookie('n2s_lang') || 'zh';
        document.documentElement.lang = savedLang === 'zh' ? 'zh-CN' : 'en';

        const setChatLang = (chat) => {
            if (chat && chat.getAttribute('lang') !== savedLang) {
                chat.setAttribute('lang', savedLang);
            }
        };

        const chat = document.getElementById('n2sChat');
        if (chat) {
            setChatLang(chat);
        } else {
            const observer = new MutationObserver((mutations, obs) => {
                const chat = document.getElementById('n2sChat');
                if (chat) {
                    setChatLang(chat);
                    obs.disconnect();
                }
            });
            observer.observe(document.documentElement, { childList: true, subtree: true });
        }
    })();
    </script>
    """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>N2S — Natural-to-SQL Agent</title>
    <style>
        * {{
            box-sizing: border-box;
        }}

        html, body {{
            margin: 0;
            padding: 0;
            background: #000000;
            color: #000000;
            font-family: "Times New Roman", Times, serif;
            font-size: 14px;
            line-height: 1.4;
        }}

        .page-frame {{
            border: 8px solid #000000;
            min-height: 100vh;
            background: #ffffff;
        }}

        .top-banner {{
            background: #000000;
            color: #ffffff;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: Helvetica, Arial, sans-serif;
            font-size: 16px;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .top-banner-left {{
            letter-spacing: 0.02em;
        }}

        .top-banner-right {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .lang-select {{
            background: #ffffff;
            color: #000000;
            border: 1px solid #000000;
            font-family: Helvetica, Arial, sans-serif;
            font-size: 12px;
            font-weight: 700;
            padding: 2px 6px;
            cursor: pointer;
        }}

        .section-eyebrow {{
            background: #8e8a25;
            color: #000000;
            font-family: "Arial Black", Arial, sans-serif;
            font-size: 36px;
            font-weight: 900;
            line-height: 1.0;
            text-transform: uppercase;
            padding: 24px 16px;
        }}

        .main-grid {{
            display: flex;
            align-items: stretch;
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px 16px 40px;
            gap: 24px;
        }}

        .left-rail {{
            width: 26%;
            min-width: 240px;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}

        .left-rail .ribbon-card {{
            display: flex;
            flex-direction: column;
        }}

        .left-rail .ribbon-card-body {{
            display: flex;
            flex-direction: column;
        }}

        .right-rail {{
            width: 74%;
            display: flex;
            flex-direction: column;
            gap: 24px;
            min-width: 0;
            min-height: 0;
        }}

        .cta-block {{
            background: #e91d2a;
            color: #ffffff;
            border: 1px solid #000000;
            padding: 16px;
            font-family: "Times New Roman", Times, serif;
            font-size: 14px;
            line-height: 1.4;
            display: flex;
            align-items: center;
        }}

        .cta-block strong {{
            font-family: Helvetica, Arial, sans-serif;
            text-transform: uppercase;
        }}

        .ribbon-card {{
            border: 1px solid #000000;
            background: #ffffff;
        }}

        .ribbon-card-title {{
            background: #ffffff;
            color: #000000;
            border-bottom: 1px solid #000000;
            padding: 6px 12px;
            font-family: Helvetica, Arial, sans-serif;
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .ribbon-card-body {{
            padding: 12px 16px;
        }}

        .ribbon-card-body.sky {{ background: #9ab6c8; }}
        .ribbon-card-body.sage {{ background: #b3bd95; }}
        .ribbon-card-body.peach {{ background: #e6915d; }}
        .ribbon-card-body.steel {{ background: #a5b8c0; }}

        .form-label {{
            display: block;
            margin-bottom: 6px;
            font-family: Helvetica, Arial, sans-serif;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .form-select, .form-input {{
            width: 100%;
            padding: 4px 6px;
            border: 1px solid #000000;
            background: #ffffff;
            color: #000000;
            font-family: "Times New Roman", Times, serif;
            font-size: 14px;
            border-radius: 0;
        }}

        .btn-primary {{
            display: inline-block;
            padding: 6px 16px;
            background: #000000;
            color: #ffffff;
            border: 1px solid #000000;
            font-family: Helvetica, Arial, sans-serif;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            cursor: pointer;
        }}

        .btn-secondary {{
            display: inline-block;
            padding: 6px 16px;
            background: #ffffff;
            color: #000000;
            border: 1px solid #000000;
            font-family: Helvetica, Arial, sans-serif;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            cursor: pointer;
        }}

        .endpoint-list {{
            list-style: none;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .endpoint-list li {{
            padding: 6px 8px;
            background: #ffffff;
            border: 1px solid #000000;
            font-family: "Courier New", Courier, monospace;
            font-size: 12px;
        }}

        .endpoint-list .method {{
            font-family: Helvetica, Arial, sans-serif;
            font-weight: 700;
            color: #e91d2a;
            margin-right: 8px;
        }}

        .footer-band {{
            background: #ffffff;
            color: #000000;
            border-top: 1px solid #000000;
            padding: 16px;
            font-size: 12px;
        }}

        .hidden {{
            display: none !important;
        }}

        .mb-1 {{ margin-bottom: 4px; }}
        .mb-2 {{ margin-bottom: 8px; }}
        .mb-3 {{ margin-bottom: 12px; }}
        .mb-4 {{ margin-bottom: 16px; }}
        .mt-1 {{ margin-top: 4px; }}
        .mt-2 {{ margin-top: 8px; }}

        .db-card .form-label {{
            margin-bottom: 3px;
            margin-top: 6px;
            padding-left: 0;
        }}

        .db-card .form-group {{
            margin-bottom: 6px;
        }}

        .db-card .form-select,
        .db-card .form-input {{
            width: 100%;
        }}

        .db-card details {{
            margin-top: 8px;
        }}

        .db-card details > summary {{
            list-style: none;
            padding: 0;
            margin: 0;
            cursor: pointer;
            font-size: 12px;
        }}

        .db-card details > summary::-webkit-details-marker {{
            display: none;
        }}

        .db-card .db-actions {{
            display: flex;
            gap: 8px;
            margin-top: 8px;
        }}

        .db-card .db-actions .btn-primary,
        .db-card .db-actions .btn-secondary {{
            flex: 1;
            text-align: center;
        }}

        n2s-chat {{
            display: block;
            width: 100%;
            height: 100%;
            max-width: 100%;
        }}

        #chatSections {{
            flex: 1;
            min-height: 0;
            display: flex;
            flex-direction: column;
        }}

        #chatSections .ribbon-card {{
            flex: 1;
            min-height: 0;
            display: flex;
            flex-direction: column;
        }}

        #chatSections .ribbon-card-body {{
            flex: 1;
            min-height: 0;
            padding: 0;
            overflow: hidden;
        }}

        @media (max-width: 768px) {{
            .page-frame {{
                border-width: 4px;
            }}

            .main-grid {{
                flex-direction: column;
            }}

            .left-rail, .right-rail {{
                width: 100%;
            }}
        }}

        @media (max-width: 480px) {{
            .page-frame {{
                border-width: 2px;
            }}

            .top-banner {{
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }}

            .section-eyebrow {{
                font-size: 24px;
                padding: 16px 12px;
            }}
        }}
    </style>
    {early_lang_script}
    {component_script}
</head>
<body>
    <div class="page-frame">
        <div class="top-banner">
            <div class="top-banner-left" data-i18n="topBanner">BUILD YOUR OWN SQL. ONLINE.</div>
            <div class="top-banner-right">
                <select id="langSelect" class="lang-select" aria-label="Language">
                    <option value="zh">中</option>
                    <option value="en">EN</option>
                </select>
            </div>
        </div>

        <div class="section-eyebrow" data-i18n="eyebrow">N2S — NATURAL-TO-SQL AGENT</div>

        <div class="main-grid">
            <div class="left-rail">
                <div class="ribbon-card">
                    <div class="ribbon-card-title" data-i18n="apiTitle">API Endpoints</div>
                    <div class="ribbon-card-body peach">
                        <ul class="endpoint-list">
                            <li><span class="method">POST</span>{api_base_url}/api/n2s/v2/chat_sse</li>
                            <li><span class="method">WS</span>{api_base_url}/api/n2s/v2/chat_websocket</li>
                            <li><span class="method">POST</span>{api_base_url}/api/n2s/v2/chat_poll</li>
                            <li><span class="method">GET</span>{api_base_url}/health</li>
                        </ul>
                    </div>
                </div>

                <div class="ribbon-card db-card">
                    <div class="ribbon-card-title" data-i18n="dbTitle">Database</div>
                    <div class="ribbon-card-body steel">
                        <div class="form-group">
                            <label for="db-select" class="form-label" data-i18n="dbActiveLabel">Active Database</label>
                            <select id="db-select" class="form-select" onchange="switchDatabase()">
                            </select>
                        </div>
                        <div class="db-actions">
                            <button class="btn-secondary" onclick="removeDatabase()" data-i18n="dbRemove">Remove</button>
                        </div>
                        <details>
                            <summary data-i18n="dbAddTitle">Add Database</summary>
                            <div class="form-group">
                                <label class="form-label" data-i18n="dbNameLabel">Name</label>
                                <input id="db-name" class="form-input" type="text" placeholder="my-mysql">
                            </div>
                            <div class="form-group">
                                <label class="form-label" data-i18n="dbTypeLabel">Type</label>
                                <select id="db-type" class="form-select" onchange="updateDefaultPort()">
                                    <option value="mysql">MySQL</option>
                                    <option value="postgresql">PostgreSQL</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label" data-i18n="dbHostLabel">Host</label>
                                <input id="db-host" class="form-input" type="text" value="localhost">
                            </div>
                            <div class="form-group">
                                <label class="form-label" data-i18n="dbPortLabel">Port</label>
                                <input id="db-port" class="form-input" type="text" value="3306">
                            </div>
                            <div class="form-group">
                                <label class="form-label" data-i18n="dbDatabaseLabel">Database</label>
                                <input id="db-database" class="form-input" type="text">
                            </div>
                            <div class="form-group">
                                <label class="form-label" data-i18n="dbUserLabel">Username</label>
                                <input id="db-username" class="form-input" type="text">
                            </div>
                            <div class="form-group">
                                <label class="form-label" data-i18n="dbPassLabel">Password</label>
                                <input id="db-password" class="form-input" type="password">
                            </div>
                            <div class="db-actions">
                                <button class="btn-secondary" onclick="testConnection()" data-i18n="dbTestBtn">Test</button>
                                <button class="btn-primary" onclick="addDatabase()" data-i18n="dbAddBtn">Add</button>
                            </div>
                        </details>
                        <div id="db-status" class="mt-1" style="font-size: 12px;"></div>
                    </div>
                </div>

                <div class="ribbon-card">
                    <div class="ribbon-card-title" data-i18n="importTitle">Data Import</div>
                    <div class="ribbon-card-body sage">
                        <label for="ingest-dir-input" class="form-label" data-i18n="importDirLabel">Directory Path</label>
                        <input id="ingest-dir-input" class="form-input mb-3" type="text" placeholder="/path/to/data">
                        <button id="ingest-button" class="btn-primary" onclick="ingestDirectory()" data-i18n="importBtn">Import</button>
                        <div id="ingest-status" class="mt-2" style="font-size: 12px;"></div>
                        <div id="ingest-tables" class="mt-2" style="font-size: 12px;"></div>
                    </div>
                </div>

            </div>

            <div class="right-rail">
                <!-- Login Form -->
                <div id="loginContainer" class="ribbon-card">
                    <div class="ribbon-card-title" data-i18n="loginTitle">Login to Continue</div>
                    <div class="ribbon-card-body sky">
                        <label for="emailInput" class="form-label" data-i18n="emailLabel">Email Address</label>
                        <select id="emailInput" class="form-select mb-3">
                            <option value="" data-i18n="emailPlaceholder">Select an email...</option>
                            <option value="admin@example.com">admin@example.com</option>
                            <option value="user@example.com">user@example.com</option>
                        </select>

                        <button id="loginButton" class="btn-primary" data-i18n="continue">Continue</button>

                        <p class="mt-2" style="font-size: 12px; margin-bottom: 0;">
                            <strong data-i18n="demoModeStrong">Demo Mode:</strong>
                            <span data-i18n="demoModeText">Frontend-only authentication demo. Your email will be stored as a cookie and sent with API requests.</span>
                        </p>
                    </div>
                </div>

                <!-- Chat Container (hidden by default) -->
                <div id="chatSections" class="hidden">
                    <div class="ribbon-card">
                        <div class="ribbon-card-title" data-i18n="chatTitle">Chat with N2S</div>
                        <div class="ribbon-card-body sage" style="padding: 0; overflow: hidden;">
                            <n2s-chat
                                id="n2sChat"
                                api-base="{api_base_url}"
                                sse-endpoint="{api_base_url}/api/n2s/v2/chat_sse"
                                ws-endpoint="{api_base_url}/api/n2s/v2/chat_websocket"
                                poll-endpoint="{api_base_url}/api/n2s/v2/chat_poll"
                                lang="zh">
                            </n2s-chat>
                        </div>
                    </div>

                </div>
            </div>
        </div>

        <!-- Session (full width, hidden by default) -->
        <div id="loggedInStatus" class="ribbon-card hidden" style="max-width: 1200px; margin: 0 auto 24px; padding: 0 16px;">
            <div class="ribbon-card-title" data-i18n="sessionTitle">Session</div>
            <div class="ribbon-card-body steel">
                <span data-i18n="loggedInAs">Logged in as</span>
                <strong id="loggedInEmail"></strong>
                <br>
                <button id="logoutButton" class="btn-secondary mt-2" data-i18n="logout">Logout</button>
            </div>
        </div>

        <div class="footer-band">
            <p style="text-align: center; margin: 0; font-size: 11px;" data-i18n="bestViewed">
                This site is best viewed with browser versions 3.0 and higher. N2S is built on Vanna 2.0 under the MIT License.
            </p>
        </div>
    </div>

    <script>
        const i18n = {{
            zh: {{
                topBanner: '在线构建你的 SQL',
                eyebrow: 'N2S — 自然语言转 SQL 智能体',
                ctaText: '<strong>在 N2S.AI</strong>，我们将帮助你把自然语言转换为 SQL，针对数据库执行，并可视化结果。只需输入问题，Agent 即可完成工作。',
                getStartedTitle: '开始使用',
                getStarted1: '1. 选择演示邮箱。',
                getStarted2: '2. 点击继续。',
                getStarted3: '3. 提问，例如“有多少员工？”。',
                loginTitle: '登录以继续',
                emailLabel: '邮箱地址',
                emailPlaceholder: '选择邮箱...',
                continue: '继续',
                demoModeStrong: '演示模式：',
                demoModeText: '仅前端认证演示。你的邮箱将以 cookie 形式存储并随 API 请求发送。',
                sessionTitle: '会话',
                loggedInAs: '已登录为',
                logout: '退出',
                chatTitle: '与 N2S 对话',
                apiTitle: 'API 端点',
                importTitle: '数据导入',
                importDirLabel: '目录路径',
                importBtn: '导入',
                dbTitle: '数据库',
                dbActiveLabel: '当前数据库',
                dbRemove: '删除',
                dbAddTitle: '添加数据库',
                dbNameLabel: '名称',
                dbTypeLabel: '类型',
                dbHostLabel: '主机',
                dbPortLabel: '端口',
                dbDatabaseLabel: '数据库名',
                dbUserLabel: '用户名',
                dbPassLabel: '密码',
                dbTestBtn: '测试',
                dbAddBtn: '添加',
                bestViewed: '建议使用 3.0 或更高版本浏览器浏览。N2S 基于 Vanna 2.0 构建，采用 MIT 许可证。'
            }},
            en: {{
                topBanner: 'BUILD YOUR OWN SQL. ONLINE.',
                eyebrow: 'N2S — NATURAL-TO-SQL AGENT',
                ctaText: `<strong>At N2S.AI</strong>, we'll help you turn plain English into SQL, execute it against your database, and visualise the results. Just type a question and let the agent do the work.`,
                getStartedTitle: 'GET STARTED',
                getStarted1: '1. Select a demo email.',
                getStarted2: '2. Click Continue.',
                getStarted3: '3. Ask a question like "How many employees are there?".',
                loginTitle: 'Login to Continue',
                emailLabel: 'Email Address',
                emailPlaceholder: 'Select an email...',
                continue: 'Continue',
                demoModeStrong: 'Demo Mode:',
                demoModeText: 'Frontend-only authentication demo. Your email will be stored as a cookie and sent with API requests.',
                sessionTitle: 'Session',
                loggedInAs: 'Logged in as',
                logout: 'Logout',
                chatTitle: 'Chat with N2S',
                apiTitle: 'API Endpoints',
                importTitle: 'Data Import',
                importDirLabel: 'Directory Path',
                importBtn: 'Import',
                dbTitle: 'Database',
                dbActiveLabel: 'Active Database',
                dbRemove: 'Remove',
                dbAddTitle: 'Add Database',
                dbNameLabel: 'Name',
                dbTypeLabel: 'Type',
                dbHostLabel: 'Host',
                dbPortLabel: 'Port',
                dbDatabaseLabel: 'Database',
                dbUserLabel: 'Username',
                dbPassLabel: 'Password',
                dbTestBtn: 'Test',
                dbAddBtn: 'Add',
                bestViewed: 'This site is best viewed with browser versions 3.0 and higher. N2S is built on Vanna 2.0 under the MIT License.'
            }}
        }};

        function setLanguage(lang) {{
            const dict = i18n[lang] || i18n.zh;
            document.querySelectorAll('[data-i18n]').forEach(el => {{
                const key = el.getAttribute('data-i18n');
                if (dict[key] !== undefined) {{
                    el.textContent = dict[key];
                }}
            }});
            document.querySelectorAll('[data-i18n-html]').forEach(el => {{
                const key = el.getAttribute('data-i18n-html');
                if (dict[key] !== undefined) {{
                    el.innerHTML = dict[key];
                }}
            }});
            document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {{
                const key = el.getAttribute('data-i18n-placeholder');
                if (dict[key] !== undefined) {{
                    el.setAttribute('placeholder', dict[key]);
                }}
            }});
            document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
            const chat = document.getElementById('n2sChat');
            if (chat) chat.setAttribute('lang', lang);
        }}

        // Cookie helpers
        const getCookie = (name) => {{
            const value = `; ${{document.cookie}}`;
            const parts = value.split(`; ${{name}}=`);
            return parts.length === 2 ? parts.pop().split(';').shift() : null;
        }};

        const setCookie = (name, value) => {{
            const expires = new Date(Date.now() + 365 * 864e5).toUTCString();
            document.cookie = `${{name}}=${{value}}; expires=${{expires}}; path=/; SameSite=Lax`;
        }};

        const deleteCookie = (name) => {{
            document.cookie = `${{name}}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        }};

        // Data import
        async function ingestDirectory() {{
            const dirPath = document.getElementById('ingest-dir-input').value;
            const statusDiv = document.getElementById('ingest-status');
            statusDiv.textContent = 'Importing...';
            try {{
                const resp = await fetch('/api/ingest/directory', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{dir_path: dirPath}})
                }});
                const data = await resp.json();
                statusDiv.innerHTML = `Done: ${{data.succeeded}}/${{data.total_files}} files. Tables: ${{data.tables_created.join(', ')}}`;
                loadTables();
            }} catch(e) {{
                statusDiv.textContent = 'Error: ' + e.message;
            }}
        }}

        async function loadTables() {{
            const resp = await fetch('/api/ingest/tables');
            const tables = await resp.json();
            const listDiv = document.getElementById('ingest-tables');
            listDiv.innerHTML = tables.map(t => `<div>${{t.name}} (${{t.rows}} rows)</div>`).join('');
        }}

        // Database management
        async function loadDatabases() {{
            try {{
                const resp = await fetch('/api/databases');
                const dbs = await resp.json();
                const select = document.getElementById('db-select');
                select.innerHTML = dbs.map(db =>
                    `<option value="${{db.name}}" ${{db.is_active ? 'selected' : ''}}>${{db.name}} (${{db.db_type}})</option>`
                ).join('');
            }} catch(e) {{
                console.error('Failed to load databases:', e);
            }}
        }}

        async function switchDatabase() {{
            const name = document.getElementById('db-select').value;
            const statusDiv = document.getElementById('db-status');
            statusDiv.textContent = 'Switching...';
            try {{
                const resp = await fetch('/api/databases/active', {{
                    method: 'PUT',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{name: name}})
                }});
                const data = await resp.json();
                if (data.success) {{
                    statusDiv.textContent = '\u2713 ' + name;
                    loadTables();
                }} else {{
                    statusDiv.textContent = '\u2717 ' + (data.error || 'Failed');
                }}
            }} catch(e) {{
                statusDiv.textContent = 'Error: ' + e.message;
            }}
        }}

        async function addDatabase() {{
            const statusDiv = document.getElementById('db-status');
            const body = {{
                name: document.getElementById('db-name').value,
                db_type: document.getElementById('db-type').value,
                host: document.getElementById('db-host').value,
                port: parseInt(document.getElementById('db-port').value) || 0,
                database: document.getElementById('db-database').value,
                username: document.getElementById('db-username').value,
                password: document.getElementById('db-password').value,
            }};
            if (!body.name || !body.host || !body.database) {{
                statusDiv.textContent = '\u2717 Name, Host, Database required';
                return;
            }}
            try {{
                const resp = await fetch('/api/databases', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(body)
                }});
                const data = await resp.json();
                if (data.success) {{
                    statusDiv.textContent = '\u2713 Added: ' + body.name;
                    loadDatabases();
                }} else {{
                    statusDiv.textContent = '\u2717 ' + (data.error || 'Failed');
                }}
            }} catch(e) {{
                statusDiv.textContent = 'Error: ' + e.message;
            }}
        }}

        async function removeDatabase() {{
            const name = document.getElementById('db-select').value;
            if (!confirm('Remove database "' + name + '"?')) return;
            const statusDiv = document.getElementById('db-status');
            try {{
                const resp = await fetch(`/api/databases/${{name}}`, {{method: 'DELETE'}});
                const data = await resp.json();
                if (data.success) {{
                    statusDiv.textContent = '\u2713 Removed: ' + name;
                    loadDatabases();
                    loadTables();
                }} else {{
                    statusDiv.textContent = '\u2717 ' + (data.error || 'Failed');
                }}
            }} catch(e) {{
                statusDiv.textContent = 'Error: ' + e.message;
            }}
        }}

        async function testConnection() {{
            const statusDiv = document.getElementById('db-status');
            statusDiv.textContent = 'Testing...';
            const body = {{
                db_type: document.getElementById('db-type').value,
                host: document.getElementById('db-host').value,
                port: parseInt(document.getElementById('db-port').value) || 0,
                database: document.getElementById('db-database').value,
                username: document.getElementById('db-username').value,
                password: document.getElementById('db-password').value,
            }};
            try {{
                const resp = await fetch('/api/databases/test', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(body)
                }});
                const data = await resp.json();
                if (data.success) {{
                    statusDiv.textContent = '\u2713 Connection OK';
                }} else {{
                    statusDiv.textContent = '\u2717 ' + (data.message || 'Connection failed');
                }}
            }} catch(e) {{
                statusDiv.textContent = 'Error: ' + e.message;
            }}
        }}

        function updateDefaultPort() {{
            const type = document.getElementById('db-type').value;
            const portInput = document.getElementById('db-port');
            if (type === 'mysql') portInput.value = '3306';
            else if (type === 'postgresql') portInput.value = '5432';
        }}

        // Login/Logout
        document.addEventListener('DOMContentLoaded', () => {{
            loadTables();
            loadDatabases();

            const savedLang = getCookie('n2s_lang') || 'zh';
            langSelect.value = savedLang;
            setLanguage(savedLang);

            langSelect.addEventListener('change', (e) => {{
                const lang = e.target.value;
                setCookie('n2s_lang', lang);
                setLanguage(lang);
            }});

            const email = getCookie('n2s_email');

            if (email) {{
                loginContainer.classList.add('hidden');
                loggedInStatus.classList.remove('hidden');
                chatSections.classList.remove('hidden');
                loggedInEmail.textContent = email;
            }}

            loginButton.addEventListener('click', () => {{
                const email = emailInput.value.trim();
                if (!email) {{
                    alert(savedLang === 'zh' ? '请选择邮箱地址' : 'Please select an email address');
                    return;
                }}
                setCookie('n2s_email', email);
                loginContainer.classList.add('hidden');
                loggedInStatus.classList.remove('hidden');
                chatSections.classList.remove('hidden');
                loggedInEmail.textContent = email;
            }});

            logoutButton.addEventListener('click', () => {{
                deleteCookie('n2s_email');
                loginContainer.classList.remove('hidden');
                loggedInStatus.classList.add('hidden');
                chatSections.classList.add('hidden');
                emailInput.value = '';
            }});

            emailInput.addEventListener('keypress', (e) => {{
                if (e.key === 'Enter') loginButton.click();
            }});
        }});
    </script>

    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const n2sChat = document.querySelector('n2s-chat');

            if (n2sChat) {{
                n2sChat.addEventListener('artifact-opened', (event) => {{
                    const {{ artifactId, type, title, trigger }} = event.detail;
                    console.log('Artifact Event:', {{ artifactId, type, title, trigger }});

                    setTimeout(() => {{
                        const newWindow = window.open('', '_blank', 'width=900,height=700');
                        if (newWindow) {{
                            newWindow.document.write(event.detail.getStandaloneHTML());
                            newWindow.document.close();
                            newWindow.document.title = title || 'N2S Artifact';
                        }}
                    }}, 100);

                    event.detail.preventDefault();
                }});
            }}
        }});

        if (!customElements.get('n2s-chat')) {{
            setTimeout(() => {{
                if (!customElements.get('n2s-chat')) {{
                    document.querySelector('n2s-chat').innerHTML = `
                        <div class="p-10 text-center text-gray-600">
                            <h3 class="text-xl font-semibold mb-2">N2S Chat Component</h3>
                            <p class="mb-2">Web component failed to load. Please check your connection.</p>
                            <p class="text-sm text-gray-400">
                                {("Loading from: local static assets" if dev_mode else f"Loading from: {cdn_url}")}
                            </p>
                        </div>
                    `;
                }}
            }}, 2000);
        }}
    </script>
</body>
</html>"""


# Backward compatibility - default production HTML
INDEX_HTML = get_index_html()
