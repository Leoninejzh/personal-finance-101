"""
UI strings for Streamlit (English default + Spanish + Chinese).

Use ``t("key")`` from Streamlit callbacks after ``st.session_state`` exists.
Use ``text("key", lang, **kwargs)`` from non-Streamlit code (e.g. funnel math).
"""

from __future__ import annotations

from typing import Any, Mapping

STRINGS: dict[str, dict[str, str]] = {
    "lang_selector_label": {
        "en": "Language",
        "es": "Idioma",
        "zh": "语言",
    },
    # --- Post-onboarding dashboard header ---
    "dash_subtitle": {
        "en": "Use the list on the left to move through each topic.",
        "es": "Usa la lista a la izquierda para recorrer cada tema.",
        "zh": "用左侧列表依次查看各主题。",
    },
    "dash_disk_cache_off": {
        "en": "Your numbers stay in this browser until you close the tab. Use **Export** to download a copy.",
        "es": "Tus cifras permanecen en este navegador hasta cerrar la pestaña. Usa **Exportar** para descargar una copia.",
        "zh": "数字保存在本浏览器，关闭标签即清空。需要备份请用 **Export** 下载。",
    },
    "cloud_mode_banner": {
        "en": "**Cloud mode:** disk save is off. Your answers exist only in this browser session and will not persist after a full refresh or if you close the tab. Use **Export** on the dashboard to download a copy.",
        "es": "**Modo nube:** el guardado en disco está desactivado. Tus datos solo viven en esta sesión del navegador y no persisten tras recargar o cerrar la pestaña. Usa **Exportar** en el panel para descargar una copia.",
        "zh": "**云端模式：** 未启用磁盘保存。内容仅存在于当前浏览器会话，刷新或关闭标签后不会保留。请在仪表板使用 **Export** 下载备份。",
    },
    "cloud_mode_sidebar_badge": {
        "en": "Cloud mode · session only",
        "es": "Modo nube · solo sesión",
        "zh": "云端模式 · 仅本会话",
    },
    "dash_baseline_header": {
        "en": "Your baseline (from the questionnaire)",
        "es": "Tu línea base (del cuestionario)",
        "zh": "你的基线（来自问卷）",
    },
    "dash_style_saved": {
        "en": "**Style:** {vibe} · **Saved:** `{ts}`",
        "es": "**Estilo:** {vibe} · **Guardado:** `{ts}`",
        "zh": "**风格：** {vibe} · **已保存：** `{ts}`",
    },
    # --- Pie breakdown (8 rows) ---
    "pie_breakdown_title": {
        "en": "**Monthly breakdown (8 rows)**",
        "es": "**Desglose mensual (8 filas)**",
        "zh": "**月度分项（8 行）**",
    },
    "pie_breakdown_line": {
        "en": "{n}. {label} — **{usd:,.0f}** USD/mo (**{pct:.1f}%** of take-home)",
        "es": "{n}. {label} — **{usd:,.0f}** USD/mes (**{pct:.1f}%** del ingreso neto)",
        "zh": "{n}. {label} — **{usd:,.0f}** 美元/月（占实发 **{pct:.1f}%**）",
    },
    "pie_ledger_note_disk_on": {
        "en": "Figures match your worksheet and the chart (saved data: `{path}`).",
        "es": "Las cifras coinciden con tu hoja y el gráfico (archivo: `{path}`).",
        "zh": "数字与当前工作表及饼图一致（数据文件：`{path}`）。",
    },
    "pie_ledger_note_disk_off": {
        "en": "Figures match the chart and what you entered in each step.",
        "es": "Las cifras coinciden con el gráfico y lo que introdujiste en cada paso.",
        "zh": "数字与饼图及你在各步填写的内容一致。",
    },
    "pie_row_0": {
        "en": "Housing",
        "es": "Vivienda",
        "zh": "住房",
    },
    "pie_row_1": {
        "en": "Car / transit",
        "es": "Coche / transporte",
        "zh": "车 / 交通",
    },
    "pie_row_2": {
        "en": "Child-related",
        "es": "Hijos",
        "zh": "育儿",
    },
    "pie_row_3": {
        "en": "Groceries at home",
        "es": "Comida en casa",
        "zh": "在家食品杂货",
    },
    "pie_row_4": {
        "en": "Fun & discretionary",
        "es": "Ocio y discrecional",
        "zh": "娱乐与可自由支配",
    },
    "pie_row_5": {
        "en": "Emergency savings (this month)",
        "es": "Ahorro de emergencia (este mes)",
        "zh": "应急储蓄（本月）",
    },
    "pie_row_6": {
        "en": "Long-term investing (hypothetical %)",
        "es": "Inversión a largo plazo (% hipotético)",
        "zh": "长期投资（假设比例）",
    },
    "pie_row_7": {
        "en": "What’s left after the plan",
        "es": "Lo que queda tras el plan",
        "zh": "按计划分配后的结余",
    },
    # --- Invest success ---
    "invest_congrats": {
        "en": "You still have about **${s:,.0f}/mo** left after everyday spending — before emergency savings and investing. *Educational only.*",
        "es": "Aún te quedan unos **${s:,.0f}/mes** tras el gasto corriente — antes de emergencia e inversión. *Solo educativo.*",
        "zh": "日常开支后仍约有 **${s:,.0f}/月** — 尚未扣应急与长期投资。*仅供学习参考。*",
    },
    # --- Chat / LLM ---
    "chat_title": {
        "en": "##### Chat",
        "es": "##### Chat",
        "zh": "##### 对话",
    },
    "chat_caption_disk_on": {
        "en": "Add your own API key below. Each person uses their own key; nothing is shared between visitors.",
        "es": "Añade tu propia API key abajo. Cada persona usa la suya; no hay datos compartidos entre visitantes.",
        "zh": "在下方填写你自己的 API Key。每人用自己的 Key，访客之间不共享数据。",
    },
    "chat_caption_disk_off": {
        "en": "Add your own API key. Your chat clears when you close this tab.",
        "es": "Añade tu propia API key. El chat se borra al cerrar esta pestaña.",
        "zh": "填写你自己的 API Key。关闭本标签后对话即清空。",
    },
    "chat_api_key_label": {
        "en": "API key (OpenAI or compatible)",
        "es": "API key (OpenAI o compatible)",
        "zh": "API Key（OpenAI 或兼容接口）",
    },
    "chat_api_key_help": {
        "en": "Stored only in this browser for this visit.",
        "es": "Solo se guarda en este navegador en esta visita.",
        "zh": "仅在本浏览器本次访问中保存。",
    },
    "chat_model_label": {
        "en": "Model name",
        "es": "Nombre del modelo",
        "zh": "模型名称",
    },
    "chat_missing_openai_key": {
        "en": "Please enter your **OpenAI API key** in the field below to use the advisor.",
        "es": "Introduce tu **API key de OpenAI** en el campo de abajo para usar el asesor.",
        "zh": "请在下方填写 **OpenAI API Key** 以使用顾问对话。",
    },
    "chat_clear_button": {
        "en": "Clear chat",
        "es": "Borrar chat",
        "zh": "清空对话",
    },
    "chat_info_box": {
        "en": "Ask in plain language about your numbers. Replies are **educational only**, not personal advice.",
        "es": "Pregunta en lenguaje natural sobre tus cifras. Las respuestas son **solo educativas**, no asesoramiento personal.",
        "zh": "用日常语言提问。回复**仅供学习**，不是个人投资建议。",
    },
    "chat_area_caption": {
        "en": "Scroll to see earlier messages.",
        "es": "Desplázate para ver mensajes anteriores.",
        "zh": "向上滚动可查看更早消息。",
    },
    "chat_input_placeholder": {
        "en": "Describe your situation or question…",
        "es": "Describe tu situación o pregunta…",
        "zh": "用自然语言描述你的情况或问题…",
    },
    "chat_spinner": {
        "en": "Calling the model…",
        "es": "Llamando al modelo…",
        "zh": "正在请求大模型…",
    },
    "chat_error_reply": {
        "en": "Something went wrong: `{err}`. Check your key, model name, and connection.",
        "es": "Algo falló: `{err}`. Revisa la clave, el modelo y la conexión.",
        "zh": "出错了：`{err}`。请检查 Key、模型与网络。",
    },
    "chat_reply_need_openai_key": {
        "en": "Please enter your **OpenAI API key** in the left panel. Without it the advisor cannot be called. Your worksheet data is only sent to the model in the background with your question — it is **not** shown in this chat.",
        "es": "Introduce tu **API key de OpenAI** en el panel izquierdo. Sin ella no se puede llamar al asesor. Tus datos solo se envían al modelo en segundo plano junto con tu pregunta — **no** aparecen aquí en el chat.",
        "zh": "请在左侧填写 **OpenAI API Key**，否则无法调用顾问。你的问卷与现金流 JSON 只在后台随你的问题一并发给模型，**不会**显示在本对话框中。",
    },
    "api_empty_choices": {
        "en": "The assistant returned an empty message. Try again.",
        "es": "El asistente devolvió un mensaje vacío. Inténtalo de nuevo.",
        "zh": "助手没有返回内容，请重试。",
    },
    # --- Funnel warnings ---
    "funnel_negative_surplus": {
        "en": "Saving before investing is negative: total living expenses exceed after-tax income.",
        "es": "El ahorro antes de invertir es negativo: los gastos de vida superan el ingreso neto.",
        "zh": "投资前结余为负：生活开支已超过税后收入。",
    },
    "funnel_invest_capped": {
        "en": "Investing capped: requested ${raw:,.2f}/mo exceeds surplus ${s_before:,.2f}/mo; applied ${inv_applied:,.2f}/mo to the remainder.",
        "es": "Inversión limitada: solicitado ${raw:,.2f}/mes supera el superávit ${s_before:,.2f}/mes; aplicado ${inv_applied:,.2f}/mes.",
        "zh": "投资金额已封顶：请求 ${raw:,.2f}/月 超过基础结余 ${s_before:,.2f}/月，按 ${inv_applied:,.2f}/月 计入结余。",
    },
    # --- Onboarding ---
    "onboard_main_title": {
        "en": "Wise spending",
        "es": "Gasto prudente",
        "zh": "明智支出",
    },
    "onboard_main_caption": {
        "en": "A quick baseline — three short steps.",
        "es": "Una línea base rápida — tres pasos breves.",
        "zh": "快速建立基线 — 三个简短步骤。",
    },
    "onboard_step1_title": {
        "en": "### Household income\nWhat is your **monthly take-home** for the household — after taxes and deductions?",
        "es": "### Ingreso del hogar\n¿Cuál es tu **ingreso neto mensual** del hogar — después de impuestos y deducciones?",
        "zh": "### 家庭收入\n家庭的**每月税后实发**大概是多少？",
    },
    "onboard_step1_btn": {
        "en": "Continue",
        "es": "Continuar",
        "zh": "继续",
    },
    "onboard_step2_title": {
        "en": "### Household\nWho is in your household? This shapes our baseline living-cost estimate.",
        "es": "### Hogar\n¿Quién forma parte de tu hogar? Esto orienta la estimación de costes de vida.",
        "zh": "### 家庭成员\n家里有哪些人？用于估算基础生活成本。",
    },
    "onboard_step2_btn": {
        "en": "Continue",
        "es": "Continuar",
        "zh": "继续",
    },
    "onboard_step3_title": {
        "en": "### Spending vibe\nHow would you describe your **day-to-day spending style**?",
        "es": "### Estilo de gasto\n¿Cómo describirías tu **forma de gastar el día a día**?",
        "zh": "### 消费习惯\n你如何描述自己的**日常消费风格**？",
    },
    "onboard_step3_btn": {
        "en": "Finish & save",
        "es": "Finalizar y guardar",
        "zh": "完成并保存",
    },
    "intro_start_questionnaire": {
        "en": "Begin questionnaire →",
        "es": "Empezar cuestionario →",
        "zh": "开始问卷 →",
    },
    "intro_cta_line": {
        "en": "Three steps · No account · Stays in this browser",
        "es": "Tres pasos · Sin cuenta · Solo en este navegador",
        "zh": "三步 · 无需账号 · 数据仅在本浏览器",
    },
    # --- Waterfall short labels (tracker, pie table, legend; same order as ledger) ---
    "wfl_short_0": {
        "en": "Housing",
        "es": "Vivienda",
        "zh": "住房",
    },
    "wfl_short_1": {
        "en": "Car / transit",
        "es": "Coche / transporte",
        "zh": "车 / 交通",
    },
    "wfl_short_2": {
        "en": "Child",
        "es": "Hijos",
        "zh": "育儿",
    },
    "wfl_short_3": {
        "en": "Groceries",
        "es": "Comida en casa",
        "zh": "食品杂货",
    },
    "wfl_short_4": {
        "en": "Fun",
        "es": "Ocio",
        "zh": "娱乐",
    },
    "wfl_short_5": {
        "en": "Emergency save",
        "es": "Ahorro emergencia",
        "zh": "应急储蓄",
    },
    "wfl_short_6": {
        "en": "Invest (%)",
        "es": "Inversión (%)",
        "zh": "投资 (%)",
    },
    "wfl_short_7": {
        "en": "Final savings",
        "es": "Ahorro final",
        "zh": "最终结余",
    },
    # --- Wizard module cards & sidebar ---
    "wiz_title_housing": {
        "en": "Housing · Rent / own",
        "es": "Vivienda · Alquiler / ser propietario",
        "zh": "住房 · 租房 / 自有",
    },
    "wiz_desc_housing": {
        "en": "Your rent or own-home costs for a typical month.",
        "es": "Tus costes de alquiler o vivienda en propiedad en un mes típico.",
        "zh": "填写典型月份的租房或自有住房开支。",
    },
    "wiz_nav_housing": {"en": "Housing", "es": "Vivienda", "zh": "住房"},
    "wiz_title_car": {"en": "Car", "es": "Coche", "zh": "用车"},
    "wiz_desc_car": {
        "en": "All-in monthly cost of having a car — or transit if you don’t drive.",
        "es": "Coste mensual total del coche — o transporte si no conduces.",
        "zh": "有车时的月度总成本 — 或不开车时的交通支出。",
    },
    "wiz_nav_car": {"en": "Car", "es": "Coche", "zh": "用车"},
    "wiz_title_child": {"en": "Child", "es": "Hijos", "zh": "育儿"},
    "wiz_desc_child": {
        "en": "Child-related costs you pay each month.",
        "es": "Gastos mensuales relacionados con los hijos.",
        "zh": "与子女相关的月度开支。",
    },
    "wiz_nav_child": {"en": "Child", "es": "Hijos", "zh": "育儿"},
    "wiz_title_grocery": {
        "en": "Grocery shopping",
        "es": "Compra de comida",
        "zh": "食品杂货",
    },
    "wiz_desc_grocery": {
        "en": "Food you buy to eat at home.",
        "es": "Comida que compras para casa.",
        "zh": "在家做饭所需的食品采购。",
    },
    "wiz_nav_grocery": {"en": "Groceries", "es": "Comida", "zh": "杂货"},
    "wiz_title_entertainment": {
        "en": "Entertainment",
        "es": "Ocio",
        "zh": "娱乐",
    },
    "wiz_desc_entertainment": {
        "en": "Dining out, streaming, trips, hobbies — the fun part of the budget.",
        "es": "Salidas, streaming, viajes, hobbies — la parte de ocio del presupuesto.",
        "zh": "外食、影音、旅行、爱好等娱乐性支出。",
    },
    "wiz_nav_entertainment": {"en": "Fun", "es": "Ocio", "zh": "娱乐"},
    "wiz_title_invest": {"en": "Invest", "es": "Inversión", "zh": "投资"},
    "wiz_desc_invest": {
        "en": "Emergency fund, optional long-term %, and what’s left — all for learning, not advice.",
        "es": "Fondo de emergencia, % opcional a largo plazo y lo que queda — solo aprendizaje, no asesoramiento.",
        "zh": "应急金、可选长期投资比例与结余 — 仅供学习，非投资建议。",
    },
    "wiz_nav_invest": {"en": "Invest", "es": "Invertir", "zh": "投资"},
    "wiz_title_chat": {
        "en": "Chat · AI financial advisor",
        "es": "Chat · asesor financiero IA",
        "zh": "对话 · AI 财务顾问",
    },
    "wiz_desc_chat": {
        "en": "See your split in the chart, then chat in your own words (optional API key).",
        "es": "Mira el reparto en el gráfico y luego conversa con tus palabras (API key opcional).",
        "zh": "先看分配图，再用自己的话提问（可选填 API Key）。",
    },
    "wiz_nav_chat": {"en": "Chat", "es": "Chat", "zh": "对话"},
    "wiz_build_analyze": {
        "en": "Build & analyze",
        "es": "Construir y analizar",
        "zh": "搭建与分析",
    },
    "wiz_step_counter": {
        "en": "Step {cur} of {total}",
        "es": "Paso {cur} de {total}",
        "zh": "第 {cur} / {total} 步",
    },
    "wiz_back": {"en": "← Back", "es": "← Atrás", "zh": "← 返回"},
    "wiz_next": {"en": "Next →", "es": "Siguiente →", "zh": "下一步 →"},
    "wiz_next_last": {"en": "Last step ✓", "es": "Último paso ✓", "zh": "最后一步 ✓"},
    "wiz_last_caption": {
        "en": "Last step — use **Back** or the list to change an earlier one.",
        "es": "Último paso — usa **Atrás** o la lista para cambiar uno anterior.",
        "zh": "最后一步 — 用**返回**或列表可改前面的步骤。",
    },
    # --- Household / vibe (display only; stored values stay English) ---
    "opt_fam_single": {"en": "Single", "es": "Una persona", "zh": "单身"},
    "opt_fam_couple": {"en": "Couple", "es": "Pareja", "zh": "夫妻/伴侣"},
    "opt_fam_p1": {"en": "Parents (1 kid)", "es": "Padres (1 hijo)", "zh": "父母（1 孩）"},
    "opt_fam_p2": {"en": "Parents (2+ kids)", "es": "Padres (2+ hijos)", "zh": "父母（2+ 孩）"},
    "opt_vibe_min": {"en": "Minimalist", "es": "Minimalista", "zh": "极简"},
    "opt_vibe_bal": {"en": "Balanced", "es": "Equilibrado", "zh": "均衡"},
    "opt_vibe_spend": {"en": "Spender", "es": "Gastador", "zh": "偏消费"},
    "onboard_slider_income": {
        "en": "Monthly household take-home ($)",
        "es": "Ingreso neto mensual del hogar ($)",
        "zh": "家庭每月税后实发（$）",
    },
    "onboard_slider_income_help": {
        "en": "Adjusted in **$1,000** steps. Use the closest match.",
        "es": "Ajuste en pasos de **$1,000**. Elige el más cercano.",
        "zh": "按 **$1,000** 步进调整，选最接近的即可。",
    },
    "lbl_household": {"en": "Household", "es": "Hogar", "zh": "家庭构成"},
    "lbl_spending_style": {
        "en": "Spending style",
        "es": "Estilo de gasto",
        "zh": "消费习惯",
    },
    # --- Dashboard metrics & export ---
    "dash_metric_takehome_mo": {
        "en": "Take-home / mo",
        "es": "Ingreso neto / mes",
        "zh": "税后实发/月",
    },
    "dash_metric_housing_ceiling": {
        "en": "Housing spend ceiling (30% take-home)",
        "es": "Tope vivienda (30% del ingreso neto)",
        "zh": "住房支出上限（实发 30%）",
    },
    "dash_metric_housing_ceiling_help": {
        "en": "Many people aim for **all-in housing** around **30%** of take-home pay — a rough guide, not a rule.",
        "es": "Mucha gente apunta a ~**30%** del ingreso neto en **vivienda total** — guía aproximada, no regla fija.",
        "zh": "许多人把**住房总成本**控制在实发约 **30%** — 仅供参考，不是硬性标准。",
    },
    "dash_metric_est_living": {
        "en": "Est. living cost",
        "es": "Coste de vida est.",
        "zh": "估算生活成本",
    },
    "dash_metric_household_lbl": {
        "en": "Household",
        "es": "Hogar",
        "zh": "家庭",
    },
    "dash_start_over": {
        "en": "Start over",
        "es": "Empezar de nuevo",
        "zh": "重新开始",
    },
    "dash_expander_raw_json": {
        "en": "Saved summary (technical view)",
        "es": "Resumen guardado (vista técnica)",
        "zh": "已保存摘要（技术视图）",
    },
    "dash_expander_export": {
        "en": "Download your worksheet",
        "es": "Descargar tu hoja de trabajo",
        "zh": "下载工作表",
    },
    "dash_export_caption_disk_on": {
        "en": "A copy of your inputs can also be saved on this computer for the next visit.",
        "es": "También puede guardarse una copia en este equipo para la próxima visita.",
        "zh": "在本机使用时，也可保存一份以便下次打开继续。",
    },
    "dash_export_caption_disk_off": {
        "en": "Download here if you want a file. Closing the tab clears what you typed.",
        "es": "Descarga aquí si quieres un archivo. Cerrar la pestaña borra lo escrito.",
        "zh": "需要文件请在此下载。关闭标签会清空已填内容。",
    },
    "dash_rag_size_caption": {
        "en": "Last updated: `{ts}`",
        "es": "Última actualización: `{ts}`",
        "zh": "上次更新：`{ts}`",
    },
    "dash_dl_json": {"en": "Download JSON", "es": "Descargar JSON", "zh": "下载 JSON"},
    "dash_dl_docx": {
        "en": "Download Word (.docx)",
        "es": "Descargar Word (.docx)",
        "zh": "下载 Word (.docx)",
    },
    "dash_dl_pdf": {"en": "Download PDF", "es": "Descargar PDF", "zh": "下载 PDF"},
    "dash_dl_docx_err": {
        "en": ".docx: `{ex}` — `pip install python-docx`",
        "es": ".docx: `{ex}` — `pip install python-docx`",
        "zh": ".docx: `{ex}` — `pip install python-docx`",
    },
    "dash_dl_pdf_err": {
        "en": "PDF: `{ex}` — `pip install reportlab`",
        "es": "PDF: `{ex}` — `pip install reportlab`",
        "zh": "PDF: `{ex}` — `pip install reportlab`",
    },
    # --- Take-home tracker ---
    "trk_title": {"en": "Take-home tracker", "es": "Seguimiento del ingreso neto", "zh": "实发资金流跟踪"},
    "trk_step_header": {
        "en": "**Step — {title}**",
        "es": "**Paso — {title}**",
        "zh": "**步骤 — {title}**",
    },
    "trk_m1_before": {
        "en": "Take-home left / mo (before {title})",
        "es": "Ingreso neto restante / mes (antes de {title})",
        "zh": "剩余实发/月（{title} 之前）",
    },
    "trk_m1_after": {
        "en": "Take-home left / mo (after {prev})",
        "es": "Ingreso neto restante / mes (después de {prev})",
        "zh": "剩余实发/月（{prev} 之后）",
    },
    "trk_m1_help_first": {
        "en": "Your full **monthly take-home** — nothing deducted yet; first slice in the waterfall.",
        "es": "Tu **ingreso neto mensual** completo — aún sin restar; primera fila de la cascada.",
        "zh": "你的**每月税后实发** — 尚未扣减；瀑布第一步。",
    },
    "trk_m1_help_carry": {
        "en": "Same as **what you had left** after **{prev}**.",
        "es": "Igual que **lo que te quedó** tras **{prev}**.",
        "zh": "与 **{prev}** 之后的**剩余**相同。",
    },
    "trk_m2_spend": {
        "en": "Spending this step ({title})",
        "es": "Gasto en este paso ({title})",
        "zh": "本步支出（{title}）",
    },
    "trk_spend_help_default": {
        "en": "This row’s dollars (same slice as the pie / snapshot breakdown).",
        "es": "Dólares de esta fila (misma porción que el gráfico / desglose).",
        "zh": "该行的金额（与饼图/快照分项一致）。",
    },
    "trk_spend_help_grocery": {
        "en": "Same **$** as **Monthly groceries — food at home** on this page (widget return value).",
        "es": "Los mismos **$** que **Comida mensual en casa** en esta página (valor del control).",
        "zh": "与本页 **每月食品杂货 — 在家** 的 **$** 相同（控件返回值）。",
    },
    "trk_spend_help_ent": {
        "en": "Same **$** as **Total estimated monthly entertainment & discretionary fun** above (sum of the six lines).",
        "es": "Los mismos **$** que **Total ocio y discrecional mensual** arriba (suma de las seis líneas).",
        "zh": "与上方 **娱乐与可自由支配月度合计** 的 **$** 相同（六行之和）。",
    },
    "trk_spend_help_housing": {
        "en": "Matches the **Rent vs Own** binding at the top of this module (saved when you leave Housing / **Next**). **Rent:** your monthly total or ZIP benchmark. **Own:** actual all-in when > **$0**, else modeled / medians.",
        "es": "Coincide con **Alquiler vs Propiedad** vinculante arriba (guardado al salir de Vivienda / **Siguiente**). **Alquiler:** tu total o referencia ZIP. **Propiedad:** todo incluido real si > **$0**, si no modelo / medianas.",
        "zh": "与本模块顶部**租/自有**绑定一致（离开住房 / **下一步** 时保存）。**租：** 你的月总额或邮编基准。**自有：** 大于 **$0** 时用实际全包，否则用模型/中位数。",
    },
    "trk_m3_left": {
        "en": "Left after this step ({title})",
        "es": "Tras este paso ({title})",
        "zh": "本步之后剩余（{title}）",
    },
    "trk_m3_help": {
        "en": "**Left after** = money before this step − spending for **{title}**.",
        "es": "**Tras este paso** = dinero antes de este paso − gasto de **{title}**.",
        "zh": "**本步之后** = 本步前的钱 − **{title}** 的支出。",
    },
    # --- Pie UI ---
    "pie_checkbox_ledger": {
        "en": "Load the chart from a saved ledger file on disk",
        "es": "Cargar el gráfico desde un archivo guardado en disco",
        "zh": "从本机已保存的账本文件加载饼图",
    },
    "pie_checkbox_ledger_help": {
        "en": "Off = use what you entered in the app (usual). On = use the file only if it is valid.",
        "es": "Desactivado = usar lo que introdujiste (lo habitual). Activado = usar solo el archivo si es válido.",
        "zh": "关 = 使用当前应用里的数字（常用）。开 = 仅在文件有效时使用该文件。",
    },
    "pie_warn_ledger_invalid": {
        "en": "Saved ledger file missing or invalid — showing your current numbers instead.",
        "es": "Falta el archivo guardado o no es válido — se muestran tus cifras actuales.",
        "zh": "保存的账本文件无效或不存在 — 已改为你当前填写的数字。",
    },
    "pie_info_ledger_ok": {
        "en": "**Pie source:** on-disk ledger **`{path}`** (updated **{ts}**).",
        "es": "**Origen del gráfico:** libro en disco **`{path}`** (actualizado **{ts}**).",
        "zh": "**饼图来源：** 磁盘账本 **`{path}`**（更新 **{ts}**）。",
    },
    "pie_title_split": {
        "en": "Take-home split (matches monthly take-home)",
        "es": "Reparto del ingreso neto (coincide con el mensual)",
        "zh": "实发分配（与每月实发一致）",
    },
    "pie_set_takehome": {
        "en": "Set **monthly take-home** in the questionnaire to chart your allocation.",
        "es": "Indica el **ingreso neto mensual** en el cuestionario para graficar la asignación.",
        "zh": "请在问卷中设置**每月税后实发**以绘制分配图。",
    },
    "pie_caption_sum_line": {
        "en": "**Rows add up to:** ${ssum:,.0f}/mo · **Take-home:** ${inc:,.0f}/mo",
        "es": "**Suma de filas:** ${ssum:,.0f}/mes · **Ingreso neto:** ${inc:,.0f}/mes",
        "zh": "**各行合计：** ${ssum:,.0f}/月 · **实发：** ${inc:,.0f}/月",
    },
    "pie_warn_over_budget": {
        "en": "Planned lines add up to **more than take-home** by about **${gap:,.0f}/mo** (“Final savings” would need to go negative). Adjust inputs or see the table — pie is hidden until the plan fits inside take-home.",
        "es": "Las líneas suman **más que el ingreso neto** unos **${gap:,.0f}/mes** (“Ahorro final” sería negativo). Ajusta entradas o mira la tabla — el gráfico circular se oculta hasta que quepa en el ingreso.",
        "zh": "各行合计**超过实发**约 **${gap:,.0f}/月**（“最终结余”会为负）。请调整输入或查看表格 — 计划纳入实发前隐藏饼图。",
    },
    "pie_warn_matplotlib": {
        "en": "Install **matplotlib** to see the chart: `pip install matplotlib`",
        "es": "Instala **matplotlib** para ver el gráfico: `pip install matplotlib`",
        "zh": "安装 **matplotlib** 后可显示饼图：`pip install matplotlib`",
    },
    "pie_warn_chart_render": {
        "en": "Could not render the pie chart; figures are still available in the table below.",
        "es": "No se pudo dibujar el gráfico circular; las cifras siguen en la tabla de abajo.",
        "zh": "饼图未能绘制，下方表格中仍有完整数字。",
    },
    "pie_col_category": {"en": "Category", "es": "Categoría", "zh": "类别"},
    "pie_col_pct_th": {
        "en": "% of take-home",
        "es": "% del ingreso neto",
        "zh": "占实发%",
    },
    "pie_col_usd_mo": {"en": "$/mo", "es": "$/mes", "zh": "$/月"},
    "pie_legend_title": {
        "en": "Category · % take-home · $/mo",
        "es": "Categoría · % ingreso neto · $/mes",
        "zh": "类别 · 占实发% · $/月",
    },
    "pie_chart_title": {
        "en": "Take-home ${inc:,.0f}/mo",
        "es": "Ingreso neto ${inc:,.0f}/mes",
        "zh": "税后实发 ${inc:,.0f}/月",
    },
    # --- Allocation breakdown labels (display; dict keys stay English in code) ---
    "alloc_long_0": {
        "en": "Housing (effective — rent, owned, model, or ZIP benchmark)",
        "es": "Vivienda (efectiva — alquiler, propiedad, modelo o referencia ZIP)",
        "zh": "住房（有效 — 租、自有、模型或邮编基准）",
    },
    "alloc_long_1": {
        "en": "Car or transit (effective — lines or guideline)",
        "es": "Coche o transporte (efectivo — líneas o guía)",
        "zh": "车或交通（有效 — 分项或指引）",
    },
    "alloc_long_2": {
        "en": "Child-related",
        "es": "Relacionado con hijos",
        "zh": "育儿相关",
    },
    "alloc_long_3": {
        "en": "Groceries (food at home)",
        "es": "Comida en casa",
        "zh": "食品杂货（在家）",
    },
    "alloc_long_4": {
        "en": "Entertainment & discretionary",
        "es": "Ocio y gasto discrecional",
        "zh": "娱乐与可自由支配",
    },
    "alloc_long_5": {
        "en": "Emergency savings (this month)",
        "es": "Ahorro de emergencia (este mes)",
        "zh": "应急储蓄（本月）",
    },
    "alloc_long_6": {
        "en": "Long-term investing (hypothetical %)",
        "es": "Inversión a largo plazo (% hipotético)",
        "zh": "长期投资（假设 %）",
    },
    "alloc_long_7": {
        "en": "Final savings / unallocated",
        "es": "Ahorro final / no asignado",
        "zh": "最终结余 / 未分配",
    },
    "inv_section_snapshot": {
        "en": "Cashflow snapshot from your wizard inputs",
        "es": "Instantánea de flujo de caja desde tus entradas",
        "zh": "根据向导输入的现金流快照",
    },
    "inv_snapshot_caption": {
        "en": "**Spent so far** = housing through fun. **Left over** = take-home minus that — you then plan emergency savings and investing from what’s left.",
        "es": "**Gastado hasta ahora** = vivienda hasta ocio. **Lo que queda** = ingreso neto menos eso — luego planeas emergencia e inversión.",
        "zh": "**已花掉的部分** = 住房到娱乐。**剩余** = 实发减去这部分 — 再从中安排应急与投资。",
    },
    "inv_expander_funnel": {
        "en": "How the numbers flow step by step",
        "es": "Cómo encajan los números paso a paso",
        "zh": "数字如何一步步扣减",
    },
    "inv_funnel_caption": {
        "en": "**Before investing** = cash left after fun. **After investing** = that minus the invest amount you chose (capped at what you have).",
        "es": "**Antes de invertir** = efectivo tras ocio. **Tras invertir** = eso menos lo que elegiste invertir (limitado a lo disponible).",
        "zh": "**投资前** = 娱乐后的现金。**投资后** = 减去你选择投资的金额（不超过可用余额）。",
    },
    "inv_metric_sbi": {
        "en": "Saving before investing",
        "es": "Ahorro antes de invertir",
        "zh": "投资前储蓄",
    },
    "inv_metric_inv_applied": {
        "en": "Investing (applied)",
        "es": "Inversión (aplicada)",
        "zh": "投资（已计入）",
    },
    "inv_metric_sai": {
        "en": "Saving after investing",
        "es": "Ahorro tras invertir",
        "zh": "投资后储蓄",
    },
    "inv_funnel_slider_caption": {
        "en": "Invest amount from the slider: **${inv:,.0f}/mo**",
        "es": "Inversión según el control: **${inv:,.0f}/mes**",
        "zh": "滑块对应投资：**${inv:,.0f}/月**",
    },
    "inv_caption_rent_mortgage": {
        "en": "⚠️ You have **both** rent and mortgage filled — the worksheet & pie use the **larger** as monthly housing. Clear one if only one applies.",
        "es": "⚠️ Tienes **alquiler e hipoteca** rellenos — la hoja y el gráfico usan el **mayor** como vivienda mensual. Borra uno si solo aplica uno.",
        "zh": "⚠️ **租金与按揭均填写** — 工作表与饼图取**较大值**作为月住房。若只适用一项请清空另一项。",
    },
    "inv_expander_math": {
        "en": "Line items",
        "es": "Partidas",
        "zh": "分项明细",
    },
    "inv_line_item": {
        "en": "- **{label}:** ${amt:,.0f}/mo",
        "es": "- **{label}:** ${amt:,.0f}/mes",
        "zh": "- **{label}：** ${amt:,.0f}/月",
    },
    "inv_sum_lines": {
        "en": "- **Sum of all lines above:** ${s:,.0f}/mo",
        "es": "- **Suma de líneas:** ${s:,.0f}/mes",
        "zh": "- **以上各行合计：** ${s:,.0f}/月",
    },
    "inv_takehome_match": {
        "en": "- **Take-home (should match):** ${inc:,.0f}/mo",
        "es": "- **Ingreso neto (debe coincidir):** ${inc:,.0f}/mes",
        "zh": "- **实发（应对齐）：** ${inc:,.0f}/月",
    },
    "inv_info_mostly_zero": {
        "en": "Most lines are still **$0** — **Final** here ≈ take-home until you add real numbers in Housing → Fun.",
        "es": "Muchas líneas siguen en **$0** — el **Final** ≈ ingreso neto hasta que pongas cifras reales en Vivienda → Ocio.",
        "zh": "多数行仍为 **$0** — **最终**在此 ≈ 实发，直到在住房→娱乐填入真实数字。",
    },
    "inv_metric_takehome_q": {
        "en": "Take-home (questionnaire)",
        "es": "Ingreso neto (cuestionario)",
        "zh": "实发（问卷）",
    },
    "inv_metric_allocated": {
        "en": "Allocated (all lines except final cushion)",
        "es": "Asignado (todas las filas salvo colchón final)",
        "zh": "已分配（除最终缓冲外各行）",
    },
    "inv_metric_allocated_help": {
        "en": "**Take-home − Final** here — total monthly dollars through **Fun** (Housing → … → Fun). Same as the sum of the first five rows in **What went into this math** when those rows match the Fun carry.",
        "es": "**Ingreso neto − Final** — total mensual hasta **Ocio** (Vivienda → … → Ocio). Igual que la suma de las cinco primeras filas en **Qué entra** cuando coinciden con el arrastre de Ocio.",
        "zh": "**实发 − 最终** — 至**娱乐**的月支出合计（住房→…→娱乐）。与**本计算**前五行之和一致（当与娱乐结转一致时）。",
    },
    "inv_metric_final": {
        "en": "Final savings / unallocated (remainder)",
        "es": "Ahorro final / no asignado (resto)",
        "zh": "最终储蓄/未分配（余量）",
    },
    "inv_metric_final_help": {
        "en": "**Take-home − Allocated** — same as **Left after this step (Fun)** and **Saving before investing** (**S**). Emergency + invest sit **below** this headline; see the pie / strict funnel for how they use **S**.",
        "es": "**Ingreso neto − Asignado** — igual que **Tras Ocio** y **Ahorro antes de invertir** (**S**). Emergencia + inversión van **debajo** de este titular; mira el gráfico / embudo.",
        "zh": "**实发 − 已分配** — 同 **娱乐步之后剩余** 与 **投资前储蓄（S）**。应急与投资在此标题之下；详见饼图/严格漏斗如何用 **S**。",
    },
    "inv_warn_deficit_living": {
        "en": "**Living costs already exceed take-home** on these numbers (Housing through Fun add to more than monthly take-home) — either the inputs need a second look, or the month needs a plan (timing, cuts, or income not modeled here).\n\n**Plugging the hole with a credit card** is a *very* pricey habit: many revolving balances sit around **~20–24% APR** (often higher for subprime or cash advances), and interest **stacks on interest** — small gaps can snowball fast.\n\nNo lecture, just physics: **revisit the big lines**, and if this reflects real life more than a typo, a budget coach or nonprofit credit counseling beats “I’ll fix it next month” on plastic.",
        "es": "**Los gastos de vida ya superan el ingreso neto** con estas cifras (Vivienda a Ocio suman más que el mes) — revisa entradas o planifica el mes.\n\n**Tapar el hueco con tarjeta** suele ser *muy* caro: muchos saldos rotativos rondan **~20–24% TAE**; los intereses se acumulan.\n\nSin sermón: **revisa las grandes partidas**; si es realidad, asesoría presupuestaria o orientación crediticia suele ayudar más que “lo arreglo el mes que viene”.",
        "zh": "按当前数字，**生活支出已超过实发**（住房至娱乐合计大于月实发）— 请复核输入或为当月做计划。\n\n用**信用卡填坑**往往代价*极高*：循环利息常在 **约 20–24% APR**，利滚利会让小缺口变大。\n\n直说：**先看大头**；若这是现实而非笔误，预算辅导或非营利债务咨询通常比“下个月再还卡”更靠谱。",
    },
    "inv_warn_deficit_invest": {
        "en": "**Your calculator just muttered “interesting… in a spreadsheet way.”** Housing through Fun fit inside take-home, but **emergency + hypothetical invest** (pie rows) **exceed** what’s left (**S**). Tweak those lines or the slider — the **pie’s last slice** (full waterfall) is what goes negative here.\n\n**Plugging the hole with a credit card** is a *very* pricey habit: many revolving balances sit around **~20–24% APR** (often higher for subprime or cash advances), and interest **stacks on interest** — small gaps can snowball fast.\n\nNo lecture, just physics: **revisit the big lines**, and if this reflects real life more than a typo, a budget coach or nonprofit credit counseling beats “I’ll fix it next month” on plastic.",
        "es": "**La hoja de cálculo suspira.** Vivienda–Ocio caben en el ingreso, pero **emergencia + inversión hipotética** **superan** lo que queda (**S**). Ajusta esas líneas o el slider — la **última porción** del gráfico (cascada completa) es la que queda negativa.\n\n**Tapar con tarjeta** es caro (intereses altos, efecto bola de nieve).\n\nRevisa cifras; si es realidad, busca apoyo presupuestario profesional.",
        "zh": "**表格在叹气：** 住房到娱乐尚在实发内，但**应急+假设投资**（饼图行）**超过**剩余 **S**。请调整这些行或滑块 — **饼图最后一片**（完整瀑布）在此处变负。\n\n**用信用卡填坑**代价高、利滚利。\n\n请复核大额科目；若属实，预算/债务咨询比拖延还款更稳妥。",
    },
    "inv_emergency_title": {
        "en": "Emergency fund — before you chase returns",
        "es": "Fondo de emergencia — antes de perseguir rentabilidades",
        "zh": "应急资金 — 在追逐收益之前",
    },
    "inv_emergency_caption": {
        "en": "In the U.S., common guidance is **3–6 months of living expenses** in cash for surprises. Below we size the **target** as **months × your monthly take-home** (a simple rule some people use); if your real spending is lower, you can mentally trim the target.",
        "es": "En EE. UU. suele recomendarse **3–6 meses de gastos** en efectivo. Aquí el **objetivo** = **meses × ingreso neto mensual** (regla simple); si gastas menos, puedes ajustar a la baja mentalmente.",
        "zh": "在美国，常见建议是现金准备 **3–6 个月生活费**。下面将**目标**设为 **月数 × 每月税后实发**（简易规则）；若实际支出更低可自行心理调低。",
    },
    "inv_ef_months": {
        "en": "Emergency fund target (months of take-home)",
        "es": "Objetivo fondo emergencia (meses de ingreso neto)",
        "zh": "应急目标（相当于几个月实发）",
    },
    "inv_ef_months_help": {
        "en": "3 = lean cushion, 6 = sleep-better cushion for many households.",
        "es": "3 = colchón ajustado, 6 = más tranquilidad para muchos hogares.",
        "zh": "3 = 较紧缓冲，6 = 许多家庭更安心。",
    },
    "inv_ef_current": {
        "en": "Current emergency cash (high-yield savings, etc.) — total $",
        "es": "Efectivo de emergencia actual (ahorro remunerado, etc.) — total $",
        "zh": "当前应急现金（活期/高收益储蓄等）— 合计 $",
    },
    "inv_ef_current_help": {
        "en": "Round guess is fine — this is for reflection, not underwriting.",
        "es": "Una estimación redondeada vale — es para reflexión, no suscripción.",
        "zh": "粗略估计即可 — 用于反思，非核保。",
    },
    "inv_ef_target_metric": {
        "en": "Target emergency fund (~{mo} mo take-home)",
        "es": "Objetivo fondo emergencia (~{mo} meses de ingreso neto)",
        "zh": "应急目标（约 {mo} 个月实发）",
    },
    "inv_ef_gap": {
        "en": "Still to go (if target is right for you)",
        "es": "Falta por llegar (si el objetivo te encaja)",
        "zh": "距目标还差（若目标适合你）",
    },
    "inv_ef_monthly_save": {
        "en": "This month — how much will you move into emergency savings? ($)",
        "es": "Este mes — ¿cuánto pasarás a ahorro de emergencia? ($)",
        "zh": "本月 — 计划转入应急储蓄多少？（$）",
    },
    "inv_ef_ballpark": {
        "en": "Ballpark: at **${mo_save:,.0f}/mo**, you’d cover the **${gap:,.0f}** gap in about **{approx}** months (ignoring interest and life surprises — illustration only).",
        "es": "Aprox.: a **${mo_save:,.0f}/mes**, cubrirías **${gap:,.0f}** en unos **{approx}** meses (solo ilustración).",
        "zh": "粗算：按 **${mo_save:,.0f}/月**，约 **{approx}** 个月可补上 **${gap:,.0f}** 缺口（忽略利息与意外 — 仅示意）。",
    },
    "inv_401k_title": {
        "en": "Workplace plan — 401(k) / similar",
        "es": "Plan laboral — 401(k) / similar",
        "zh": "职场计划 — 401(k) / 类似计划",
    },
    "inv_401k_info": {
        "en": "**401(k)-style plans** often let you contribute **pre-tax** (traditional) — those deferrals usually **lower taxable income today** (you’ll generally owe ordinary income tax on qualified withdrawals later, unless rules change) — or **Roth** (pay tax now, potentially tax-free growth). We’re **not** doing tax advice; a pro can compare brackets and goals.\n\nWhat *is* widely treated as a no-brainer: if your employer offers a **match**, consider contributing **at least enough to capture the full match** — it’s effectively part of your compensation. Many people **raise pre-tax deferrals** until the match is maxed before they chase extra taxable investing. Only after that (and a sane cash cushion) does “more brokerage” usually enter the chat.\n\nConfirm contribution limits, vesting, and fund choices with your plan documents or a **licensed** advisor.",
        "es": "Los planes **tipo 401(k)** suelen permitir aportaciones **preimpuesto** (tradicional) o **Roth**. **No** damos asesoría fiscal.\n\nSi hay **match** del empleador, suele tener sentido aportar **al menos** lo necesario para el **match completo**.\n\nConfirma límites, vesting y fondos con tu plan o un asesor **licenciado**.",
        "zh": "**401(k) 类计划** 常有 **税前**（传统）或 **Roth** 供款路径。**非**税务建议。\n\n若有雇主 **matching**，通常值得至少供到 **拿满匹配**。\n\n限额、归属与基金请以计划文件或**持牌**顾问为准。",
    },
    "inv_401k_radio_lbl": {
        "en": "Reflection: are you already contributing enough for the **full employer match** (if you have one)?",
        "es": "Reflexión: ¿aportas ya lo suficiente para el **match completo** del empleador (si aplica)?",
        "zh": "反思：你是否已供款足够拿到**雇主全额匹配**（若有）？",
    },
    "inv_401k_opt_ns": {
        "en": "Not sure — need to check",
        "es": "No estoy seguro — hay que revisar",
        "zh": "不确定 — 需核实",
    },
    "inv_401k_opt_under": {
        "en": "No / probably under the match",
        "es": "No / probablemente por debajo del match",
        "zh": "否 / 可能低于匹配线",
    },
    "inv_401k_opt_full": {
        "en": "Yes — I’m at or above full match",
        "es": "Sí — estoy en o por encima del match completo",
        "zh": "是 — 已达或超过全额匹配",
    },
    "inv_401k_opt_na": {
        "en": "No employer plan / N/A",
        "es": "Sin plan del empleador / N/A",
        "zh": "无雇主计划 / 不适用",
    },
    "inv_401k_caption_hr": {
        "en": "If you picked **under the match**, consider asking HR or your plan site: *“What % do I need to defer to get the full match?”*",
        "es": "Si marcaste **por debajo del match**, pregunta a RRHH o al portal del plan: *¿qué % debo diferir para el match completo?*",
        "zh": "若选**低于匹配**，可问人事或计划网站：*“要递延多少 % 才能拿满匹配？”*",
    },
    "inv_not_advice": {
        "en": "**Not investment advice.** Discuss products, tax, and risk with a licensed professional.",
        "es": "**No es asesoramiento de inversión.** Habla de productos, impuestos y riesgo con un profesional licenciado.",
        "zh": "**非投资建议。** 产品、税务与风险请咨询持牌专业人士。",
    },
    "inv_slider_pct": {
        "en": "Hypothetical % of **cash after emergency** — max($0, S − this month’s emergency save); long-term investing (discussion only)",
        "es": "% hipotético del **efectivo tras emergencia** — max($0, S − ahorro emergencia del mes); inversión largo plazo (solo discusión)",
        "zh": "假设占**扣应急后现金**的 % — max($0, S−本月应急储蓄)；长期投资（仅讨论）",
    },
    "inv_slider_help": {
        "en": "Invest row = % × max($0, S − emergency). **S** = **Left after Fun** from the Fun step when carried here; else take-home − Housing through Fun. Final pie row is what’s left after emergency and this hypothetical slice. 401(k) match is not subtracted as dollars here.",
        "es": "Fila inversión = % × max($0, S − emergencia). **S** = **Tras Ocio** si se arrastra; si no, ingreso − Vivienda…Ocio. La última porción es lo que queda. El match 401(k) no se resta aquí en dólares.",
        "zh": "投资行 = % × max($0, S−应急)。**S** = 娱乐步带入的 **娱乐后剩余**；否则 实发−住房…娱乐。饼图末行是扣应急与本假设后的余量。401(k) 匹配在此不按美元扣除。",
    },
    "inv_waterfall_check": {
        "en": "**Waterfall check:** **S** ≈ **${sbi:,.0f}/mo**; **after emergency** ≈ **${post_em:,.0f}/mo**; **long-term invest** = **{pct}% × max($0, that)** ≈ **${hyp:,.0f}/mo**; **final savings** ≈ **${final:,.0f}/mo** (pie last row).",
        "es": "**Chequeo cascada:** **S** ≈ **${sbi:,.0f}/mes**; **tras emergencia** ≈ **${post_em:,.0f}/mes**; **inversión** = **{pct}% × max($0, eso)** ≈ **${hyp:,.0f}/mes**; **ahorro final** ≈ **${final:,.0f}/mes**.",
        "zh": "**瀑布核对：** **S** ≈ **${sbi:,.0f}/月**；**扣应急后** ≈ **${post_em:,.0f}/月**；**长期投资** = **{pct}% × max($0, 该项)** ≈ **${hyp:,.0f}/月**；**最终储蓄** ≈ **${final:,.0f}/月**（饼图末行）。",
    },
    # --- Benchmark compare (housing ZIP / car ceiling) ---
    "cmp_bench_high": {
        "en": "Your number is about **{pct:.0f}% above** the benchmark (**${baseline:,}/mo**). Worth double-checking what’s included (parking, HOA, etc.).",
        "es": "Tu cifra está un **{pct:.0f}% por encima** de la referencia (**${baseline:,}/mes**). Revisa qué incluye (parking, HOA, etc.).",
        "zh": "你的数字约比基准**高 {pct:.0f}%**（**${baseline:,}/月**）。请核对是否含停车费、HOA 等。",
    },
    "cmp_bench_low": {
        "en": "Your number is about **{pct:.0f}% below** the benchmark (**${baseline:,}/mo**). Great if it reflects your real all-in cost.",
        "es": "Tu cifra está un **{pct:.0f}% por debajo** de la referencia (**${baseline:,}/mes**). Genial si refleja tu coste real.",
        "zh": "你的数字约比基准**低 {pct:.0f}%**（**${baseline:,}/月**）。若符合实际全包成本则很好。",
    },
    "cmp_bench_near": {
        "en": "**Within ~5%** of the benchmark (**${baseline:,}/mo**) — you’re in a typical band for this ZIP + household shape.",
        "es": "**Cerca del ~5%** de la referencia (**${baseline:,}/mes**) — banda típica para este ZIP y hogar.",
        "zh": "与基准（**${baseline:,}/月**）相差约 **5% 内** — 对该邮编与家庭结构较典型。",
    },
    "cmp_car_high": {
        "en": "Your car costs are about **{pct:.0f}% above** this ceiling (**${ceiling:,}/mo**). Worth reviewing payment/lease (if any), depreciation estimate (if owned outright), insurance, fuel, and maintenance.",
        "es": "Tus costes de coche están un **{pct:.0f}% por encima** de este tope (**${ceiling:,}/mes**). Revisa pago/leasing, depreciación, seguro, combustible y mantenimiento.",
        "zh": "用车成本约**高于**该上限 **{pct:.0f}%**（**${ceiling:,}/月**）。请复核月供/租赁、折旧估算、保险、油费与保养。",
    },
    "cmp_car_low": {
        "en": "Your car costs are about **{pct:.0f}% below** this ceiling (**${ceiling:,}/mo**).",
        "es": "Tus costes de coche están un **{pct:.0f}% por debajo** de este tope (**${ceiling:,}/mes**).",
        "zh": "用车成本约**低于**该上限 **{pct:.0f}%**（**${ceiling:,}/月**）。",
    },
    "cmp_car_near": {
        "en": "**Within ~5%** of the car spend ceiling (**${ceiling:,}/mo**) — lines up with this rough guideline.",
        "es": "**Dentro del ~5%** del tope de coche (**${ceiling:,}/mes**) — encaja con esta guía.",
        "zh": "与用车支出上限（**${ceiling:,}/月**）相差约 **5% 内** — 符合该经验指引。",
    },
    "own_model_high": {
        "en": "Your actual cost is about **{pct:.0f}% higher** than the modeled baseline (**${model:,}/mo**).",
        "es": "Tu coste real es un **{pct:.0f}% mayor** que el modelo (**${model:,}/mes**).",
        "zh": "你的实际成本比模型基线**高约 {pct:.0f}%**（**${model:,}/月**）。",
    },
    "own_model_low": {
        "en": "Your actual cost is about **{pct:.0f}% lower** than the modeled baseline (**${model:,}/mo**).",
        "es": "Tu coste real es un **{pct:.0f}% menor** que el modelo (**${model:,}/mes**).",
        "zh": "你的实际成本比模型基线**低约 {pct:.0f}%**（**${model:,}/月**）。",
    },
    "own_model_near": {
        "en": "**Within ~5%** of the modeled baseline (**${model:,}/mo**) — your inputs line up with the simplified model.",
        "es": "**Dentro del ~5%** del modelo (**${model:,}/mes**) — tus entradas encajan con el modelo simplificado.",
        "zh": "与模型基线（**${model:,}/月**）相差约 **5% 内** — 输入与简化模型一致。",
    },
    "own_model_ideas_high": {
        "en": "**Ideas to explore**\n- **Refinance / rate check** — if your rate is above current market, a loan officer can quote break-even.\n- **Escrow & taxes** — confirm your bill split (tax reassessment, PMI removal milestones).\n- **Insurance** — shop homeowners annually; raise deductibles only if your emergency fund supports it.\n- **Utilities** — audit usage (HVAC, insulation); time-of-use plans where available.\n- **HOA / fees** — confirm what’s bundled vs duplicated in your “all-in” number.",
        "es": "**Ideas**\n- **Refinanciación / tipo** — compara con el mercado.\n- **Impuestos y escrow** — revisa reparto y PMI.\n- **Seguro** — comparar cada año.\n- **Servicios** — consumo y tarifas.\n- **HOA** — qué incluye tu “todo incluido”.",
        "zh": "**可探索方向**\n- **再融资/利率** — 与市场比较。\n- **托管与税费** — 账单拆分、PMI 取消节点。\n- **房屋保险** — 年比；自付额与应急金匹配。\n- **水电暖** — 用量与分时电价。\n- **HOA/费用** — “全包”数字是否重复计入。",
    },
    "own_model_ideas_low": {
        "en": "**Nice — a few checks**\n- Make sure the model includes everything you pay (HOA, PMI, flood insurance if any).\n- If the gap is real, consider routing the surplus to **debt payoff**, **repairs reserve**, or **retirement** after emergency savings.",
        "es": "**Bien — revisa**\n- Que el modelo incluya todo (HOA, PMI, seguros extra).\n- Si el hueco es real, valora **deuda**, **fondo reparaciones** o **jubilación** tras emergencia.",
        "zh": "**不错 — 再确认**\n- 模型是否含 HOA、PMI、洪水险等。\n- 若差距属实，可在应急后考虑**还债**、**维修储备**或**退休储蓄**。",
    },
    # --- Privacy & intro hero ---
    "privacy_banner_html": {
        "en": '<div class="questionnaire-privacy-shell"><h3>Privacy</h3><p><strong>No login.</strong> Your numbers stay in <strong>this browser</strong> for this visit. We don’t ask for your name or ID. We don’t use your inputs for ads or resale.</p></div>',
        "es": '<div class="questionnaire-privacy-shell"><h3>Privacidad</h3><p><strong>Sin cuenta.</strong> Tus cifras quedan en <strong>este navegador</strong> en esta visita. No pedimos nombre ni documento. No usamos tus datos para anuncios ni venta.</p></div>',
        "zh": '<div class="questionnaire-privacy-shell"><h3>隐私</h3><p><strong>无需登录。</strong>数字仅保存在<strong>本浏览器本次访问</strong>。我们不收集姓名或证件信息，也不将输入用于广告或出售。</p></div>',
    },
    "intro_hero_html": {
        "en": '<div class="fv-hero-shell"><div class="fv-hero-brand"><div class="fv-hero-logo"><span class="fv-hero-icon" aria-hidden="true">◆</span></div><p class="fv-hero-sub">Household cash-flow clarity</p><h1 class="fv-hero-title">Wise spending</h1></div><div class="fv-hero-body"><p class="fv-hero-line">If you earn over <strong>$300,000 USD</strong> a year, please speak with a <strong>licensed investment professional</strong> — this tool is not meant to replace one.</p></div></div>',
        "es": '<div class="fv-hero-shell"><div class="fv-hero-brand"><div class="fv-hero-logo"><span class="fv-hero-icon" aria-hidden="true">◆</span></div><p class="fv-hero-sub">Claridad del flujo del hogar</p><h1 class="fv-hero-title">Wise spending</h1></div><div class="fv-hero-body"><p class="fv-hero-line">Si ganas más de <strong>300.000 USD</strong> al año, habla con un <strong>profesional de inversiones licenciado</strong> — esta herramienta no lo sustituye.</p></div></div>',
        "zh": '<div class="fv-hero-shell"><div class="fv-hero-brand"><div class="fv-hero-logo"><span class="fv-hero-icon" aria-hidden="true">◆</span></div><p class="fv-hero-sub">家庭现金流 · 清晰起步</p><h1 class="fv-hero-title">Wise spending</h1></div><div class="fv-hero-body"><p class="fv-hero-line">若年收入超过 <strong>30 万美元</strong>，请咨询<strong>持牌投资顾问</strong> — 本工具不能替代专业意见。</p></div></div>',
    },
    # --- Housing profile hints (questionnaire family → rental band) ---
    "bed_single": {"en": "Studio – 2 bedrooms", "es": "Estudio – 2 dormitorios", "zh": "开间 – 2 卧室"},
    "bed_couple": {"en": "1 – 2 bedrooms", "es": "1 – 2 dormitorios", "zh": "1 – 2 卧室"},
    "bed_p1": {"en": "2 – 3 bedrooms", "es": "2 – 3 dormitorios", "zh": "2 – 3 卧室"},
    "bed_p2": {"en": "3+ bedrooms / single-family style", "es": "3+ dormitorios / estilo unifamiliar", "zh": "3+ 卧室 / 独栋风格"},
    "bed_default": {"en": "Typical market mix", "es": "Mix típico del mercado", "zh": "典型市场组合"},
    "prof_single_short": {
        "en": "No children · 1–2 bedrooms",
        "es": "Sin hijos · 1–2 dormitorios",
        "zh": "无孩 · 1–2 卧",
    },
    "prof_single_detail": {
        "en": "Typical studio–2BR renter unit.",
        "es": "Típico estudio–2BR en alquiler.",
        "zh": "典型开间–两卧租赁单元。",
    },
    "prof_couple_short": {
        "en": "No children · 1–2 bedrooms",
        "es": "Sin hijos · 1–2 dormitorios",
        "zh": "无孩 · 1–2 卧",
    },
    "prof_couple_detail": {
        "en": "Typical 1BR–2BR for two adults.",
        "es": "Típico 1BR–2BR para dos adultos.",
        "zh": "典型两人 1–2 卧。",
    },
    "prof_p1_short": {
        "en": "With children · 2–3 bedrooms",
        "es": "Con hijos · 2–3 dormitorios",
        "zh": "有孩 · 2–3 卧",
    },
    "prof_p1_detail": {
        "en": "Family-sized rental band.",
        "es": "Banda de alquiler familiar.",
        "zh": "家庭型租赁区间。",
    },
    "prof_p2_short": {
        "en": "Larger household · 3+ bedrooms",
        "es": "Hogar grande · 3+ dormitorios",
        "zh": "较大家庭 · 3+ 卧",
    },
    "prof_p2_detail": {
        "en": "More space / multi-kid typical mix.",
        "es": "Más espacio / varios hijos.",
        "zh": "更大空间/多孩常见组合。",
    },
    "prof_default_short": {"en": "Typical renter", "es": "Inquilino típico", "zh": "典型租户"},
    "prof_default_detail": {
        "en": "Typical for the area.",
        "es": "Típico para la zona.",
        "zh": "该地区常见情况。",
    },
    "house_from_q": {
        "en": "**From your questionnaire:** _{family}_ → **{short}**  \n{detail}",
        "es": "**Según el cuestionario:** _{family}_ → **{short}**  \n{detail}",
        "zh": "**来自问卷：** _{family}_ → **{short}**  \n{detail}",
    },
    "house_zip_label": {
        "en": "ZIP code (5 digits)",
        "es": "Código ZIP (5 dígitos)",
        "zh": "邮编（5 位）",
    },
    "house_zip_ph": {"en": "e.g. 10001", "es": "ej. 10001", "zh": "如 10001"},
    "house_flow_intro": {
        "en": "**Three steps:** (1) ZIP → local Census benchmarks · (2) **Rent or own** the home you budget for · (3) **Rent:** type your all-in or start from the ZIP median · **Own:** use a **quick ZIP median** or the **mortgage & bills calculator**, then optionally type your **real all-in** so charts match life.",
        "es": "**Tres pasos:** (1) ZIP → referencias del censo · (2) **Alquiler u propiedad** · (3) **Alquiler:** tu total o la mediana ZIP · **Propiedad:** **mediana ZIP rápida** o **calculadora de hipoteca y gastos**, y opcionalmente tu **total real**.",
        "zh": "**三步：** (1) 邮编 → 本地普查基准 · (2) 你按**租**还是**自有**做预算 · (3) **租：**填写月全包或从邮编中位数起步 · **自有：**选 **邮编中位数快估** 或 **按揭与账单计算器**，并可填写**真实月全包**以对齐生活。",
    },
    "house_living_situation_lbl": {
        "en": "For this worksheet, are you **renting** or **owning** the home?",
        "es": "En esta hoja, ¿**alquilas** o **eres propietario** de la vivienda?",
        "zh": "本页预算里，你是**租房**还是**自有住房**？",
    },
    "house_living_situation_help": {
        "en": "This single choice drives the rent vs own path, benchmarks, and what feeds the pie — no second toggle.",
        "es": "Una sola elección: alquiler o propiedad; alimenta referencias y el gráfico.",
        "zh": "仅此一项决定租房/自有路径与饼图来源，无需第二个开关。",
    },
    "house_btn_fill_zip_rent": {
        "en": "Fill “your monthly total” with the ZIP benchmark above",
        "es": "Rellenar el total mensual con la referencia ZIP",
        "zh": "用上方邮编基准填入“月合计”",
    },
    "house_own_baseline_header": {
        "en": "Owner baseline: quick estimate or calculator?",
        "es": "Propietario: ¿referencia rápida o calculadora?",
        "zh": "自有住房：快估还是计算器？",
    },
    "house_own_baseline_subcaption": {
        "en": "Pick how we **estimate** your monthly owner cost when you have not typed a full all-in yet. You can always enter **your real all-in** below (quick path) or after the model (calculator path).",
        "es": "Cómo **estimamos** el coste mensual si aún no escribes un total completo. Siempre puedes poner tu **total real** abajo.",
        "zh": "在未填写完整“月全包”时，用哪种方式**估算**自有月成本；也可随时在下方填写**真实月全包**（快估路径）或在模型后填写（计算器路径）。",
    },
    "house_own_baseline_mode_lbl": {
        "en": "Baseline source",
        "es": "Fuente de la referencia",
        "zh": "基准来源",
    },
    "house_own_mode_acs": {
        "en": "ZIP / Census median owner cost (quick)",
        "es": "Mediana de coste de propietario ZIP / censo (rápido)",
        "zh": "邮编业主成本中位数 / 普查（快估）",
    },
    "house_own_mode_calc": {
        "en": "Mortgage & bills calculator (detailed)",
        "es": "Calculadora hipoteca y gastos (detallada)",
        "zh": "按揭与账单计算器（细项）",
    },
    "house_own_mode_acs_caption": {
        "en": "Uses **ACS median monthly owner cost** for your ZIP when it matches your expectations — or type **your real all-in** to override.",
        "es": "Usa la **mediana mensual de propietario** del ZIP si encaja — o escribe tu **total real**.",
        "zh": "在认可邮编**业主月成本中位数**时使用；若与实际不符，请直接填写**真实月全包**覆盖。",
    },
    "house_own_actual_optional_acs": {
        "en": "Your real monthly all-in — mortgage, taxes, insurance, HOA, utilities ($)",
        "es": "Tu total mensual real — hipoteca, impuestos, seguro, HOA, servicios ($)",
        "zh": "真实月全包 — 按揭、税、保险、HOA、水电等（$）",
    },
    "house_own_actual_optional_acs_help": {
        "en": "When **above $0**, this wins over the Census median for totals and the pie.",
        "es": "Si es **> $0**, manda sobre la mediana del censo.",
        "zh": "大于 **0** 时优先于普查中位数计入合计与饼图。",
    },
    "house_back_estimate": {
        "en": "← Back to quick ZIP estimate",
        "es": "← Volver a la referencia ZIP rápida",
        "zh": "← 返回邮编快估",
    },
    "house_ws_side_lbl": {
        "en": "If both inputs are blank, estimate from",
        "es": "Si ambos importes siguen en blanco, estimar según",
        "zh": "若租金与自有均未填写，估算取自",
    },
    "house_ws_side_rent": {
        "en": "Rent  \nZIP gross-rent median · rent",
        "es": "Alquiler  \nMediana alquiler bruto ZIP · alquiler",
        "zh": "租房  \n邮编毛租金中位数 · 租房侧",
    },
    "house_ws_side_own": {
        "en": "Own  \nMortgage or ZIP owner median · own",
        "es": "Propiedad  \nHipoteca o mediana propietario ZIP · propiedad",
        "zh": "自有  \n按揭或邮编业主中位数 · 自有侧",
    },
    "house_ws_side_help": {
        "en": "After you type your real monthly rent **or** owned all-in, that number always wins — this only picks which benchmark/model fills the gap.",
        "es": "Tras poner tu alquiler real **o** todo incluido de propiedad, ese número manda — esto solo elige qué referencia/modelo rellena el hueco.",
        "zh": "填写真实月租**或**自有全包后，始终以该数为准 — 此项仅选择用哪套基准/模型填缺口。",
    },
    "house_binding_lbl": {
        "en": "Which side drives totals",
        "es": "Qué lado alimenta los totales",
        "zh": "哪一侧计入合计",
    },
    "house_tab_rent_lbl": {"en": "Rent", "es": "Alquiler", "zh": "租房"},
    "house_tab_own_lbl": {"en": "Own", "es": "Propiedad", "zh": "自有"},
    "house_renting_title": {"en": "Renting", "es": "Alquiler", "zh": "租房"},
    "house_renting_caption": {
        "en": "Benchmark uses Census **median gross rent** for the ZIP (ZCTA): contract rent plus **utilities** (electric, gas, water, sewer, fuels) that renters typically pay — match that with **your all-in** monthly.",
        "es": "La referencia usa la **mediana de alquiler bruto** del ZIP (ZCTA): contrato más **servicios** típicos — alinéala con tu **todo incluido** mensual.",
        "zh": "基准采用人口普查该邮编（ZCTA）**毛租金中位数**：合同租金加上租客通常支付的**水电等** — 请与你的**月全包**对齐。",
    },
    "house_bench_rent": {
        "en": "Benchmark (rent + utilities)",
        "es": "Referencia (alquiler + servicios)",
        "zh": "基准（租+杂费）",
    },
    "house_bench_rent_help": {
        "en": "ACS {yr} B25064 median ${med:,} × {mult:.2f} for your household shape.",
        "es": "Mediana ACS {yr} B25064 ${med:,} × {mult:.2f} para tu hogar.",
        "zh": "ACS {yr} B25064 中位数 ${med:,} × {mult:.2f}（按家庭结构）",
    },
    "house_warn_no_rent": {
        "en": "No median rent data for this ZCTA — try a nearby ZIP or check the code.",
        "es": "Sin mediana de alquiler para este ZCTA — prueba un ZIP cercano.",
        "zh": "该 ZCTA 无租金中位数 — 可试附近邮编。",
    },
    "house_info_zip": {
        "en": "Enter a **5-digit ZIP** to load a local benchmark.",
        "es": "Introduce un **ZIP de 5 dígitos** para cargar una referencia local.",
        "zh": "请输入 **5 位邮编** 以加载本地基准。",
    },
    "house_your_rent": {
        "en": "Your monthly total — **rent + all utilities** ($)",
        "es": "Tu total mensual — **alquiler + todos los servicios** ($)",
        "zh": "你的月合计 — **租金+全部杂费**（$）",
    },
    "house_your_rent_help": {
        "en": "Include electric, gas, water, trash, internet if bundled — match Census “gross rent” scope.",
        "es": "Incluye luz, gas, agua, basura, internet si va junto — alinea con el alcance “gross rent”.",
        "zh": "含电、气、水、垃圾、捆绑网络等 — 与普查“毛租金”口径一致。",
    },
    "house_metric_rent_tab": {
        "en": "Housing in worksheet & pie — **Rent** tab / mo",
        "es": "Vivienda en hoja y gráfico — pestaña **Alquiler** / mes",
        "zh": "工作表与饼图住房 — **租**页 / 月",
    },
    "house_metric_rent_tab_help": {
        "en": "**Your** rent + utilities when the box is above **$0**; otherwise the **ZIP gross-rent benchmark** fills in. Totals use this path when you chose **Rent** at the top.",
        "es": "Tu alquiler + servicios si la caja > **$0**; si no, la **referencia ZIP**. Los totales usan esto si elegiste **Alquiler** arriba.",
        "zh": "填写 >**$0** 时用你的数字；否则用**邮编毛租金基准**。若在上方选了**租房**，合计与饼图走此路径。",
    },
    "house_owning_title": {"en": "Owning", "es": "Ser propietario", "zh": "自有住房"},
    "house_own_beds_caption": {
        "en": "**Suggested home size for your household:** {beds}. Census uses your **ZIP (ZCTA)** as the geography — we show **ZIP-area medians** (closest public proxy to “your city block” without a paid geocoder).",
        "es": "**Tamaño sugerido:** {beds}. El censo usa tu **ZIP (ZCTA)** — mostramos **medianas del área ZIP**.",
        "zh": "**建议户型：** {beds}。普查以你的 **ZIP（ZCTA）** 为地理单元 — 展示**该邮编区域中位数**（无需付费地理编码的近似）。",
    },
    "house_own_step1": {
        "en": "Step 1 · Market median check",
        "es": "Paso 1 · Comprobar medianas",
        "zh": "步骤 1 · 市场中位数",
    },
    "house_own_zip_info": {
        "en": "Enter a **5-digit ZIP** at the top to load owner medians.",
        "es": "Introduce un **ZIP de 5 dígitos** arriba para medianas de propietarios.",
        "zh": "请在顶部输入 **5 位邮编** 以加载业主中位数。",
    },
    "house_census_lbl": {
        "en": "**Census area label:** _{name}_",
        "es": "**Etiqueta área censo:** _{name}_",
        "zh": "**普查区标签：** _{name}_",
    },
    "house_band_mult": {
        "en": "**Household band:** {short} · **Size multiplier:** ×{mult:.2f} (applied to local medians for more bedrooms / space).",
        "es": "**Banda hogar:** {short} · **Multiplicador tamaño:** ×{mult:.2f} (aplicado a medianas locales).",
        "zh": "**家庭带：** {short} · **面积系数：** ×{mult:.2f}（用于调整本地中位数）。",
    },
    "house_own_cost_metric": {
        "en": "ZIP-area median — monthly owner housing cost (adjusted)",
        "es": "Mediana área ZIP — coste mensual vivienda propietario (ajustado)",
        "zh": "邮编区域中位数 — 业主月住房成本（调整后）",
    },
    "house_own_cost_help": {
        "en": "ACS {yr} B25105 median ${med:,} × {mult:.2f}. Includes owner-reported monthly housing cost components.",
        "es": "Mediana ACS {yr} B25105 ${med:,} × {mult:.2f}. Incluye componentes declarados por propietarios.",
        "zh": "ACS {yr} B25105 中位数 ${med:,} × {mult:.2f}。含业主自报的月住房成本组成。",
    },
    "house_warn_no_b25105": {
        "en": "No B25105 owner monthly cost for this ZCTA.",
        "es": "Sin B25105 coste mensual propietario para este ZCTA.",
        "zh": "该 ZCTA 无 B25105 业主月成本。",
    },
    "house_home_val_metric": {
        "en": "ZIP-area median — owner-occupied home value (adjusted)",
        "es": "Mediana área ZIP — valor vivienda ocupada por el propietario (ajustado)",
        "zh": "邮编区域中位数 — 自住房价值（调整后）",
    },
    "house_home_val_help": {
        "en": "ACS {yr} B25077 median ${med:,} × {mult:.2f}. Used as default purchase price in the mortgage step.",
        "es": "Mediana ACS {yr} B25077 ${med:,} × {mult:.2f}. Precio compra por defecto en hipoteca.",
        "zh": "ACS {yr} B25077 中位数 ${med:,} × {mult:.2f}。按揭步骤默认房价。",
    },
    "house_info_no_b25077": {
        "en": "No B25077 median home value for this ZCTA — you’ll type a price in the next step.",
        "es": "Sin mediana B25077 para este ZCTA — podrás poner un precio en el siguiente paso.",
        "zh": "该 ZCTA 无 B25077 房价中位数 — 下一步可手动填写。",
    },
    "house_median_confirm_lbl": {
        "en": "Does this ZIP-area picture look roughly right for what you expect?",
        "es": "¿Esta imagen del área ZIP encaja más o menos con lo que esperas?",
        "zh": "该邮编区域概况是否大致符合你的预期？",
    },
    "own_median_yes_disp": {
        "en": "Yes — matches my market expectations",
        "es": "Sí — encaja con mis expectativas",
        "zh": "是 — 符合我对市场的预期",
    },
    "own_median_unsure_disp": {
        "en": "Unsure — still continue to the mortgage model",
        "es": "No estoy seguro — continuar al modelo hipotecario",
        "zh": "不确定 — 仍继续到按揭模型",
    },
    "house_unsure_title": {
        "en": "**You’re unsure about the ZIP-area medians — that’s fine.**",
        "es": "**No estás seguro de las medianas del ZIP — no pasa nada.**",
        "zh": "**若对邮编中位数不确定 — 没关系。**",
    },
    "house_unsure_body": {
        "en": "The next screen is a **calculator**, not a grade on your market:\n\n- **Median owner cost (B25105)** mixes many situations (older loans, smaller homes, some paid-off). It may sit **above or below** what you pay.\n- **Median home value (B25077)** is only a **default price** — replace it with a listing, appraisal, or a number your lender uses.\n- **Interest rate** starts from the latest **national** 30-year average (FRED). Your actual offer will depend on credit, points, and timing.\n\nYou can still enter your **real all-in monthly** at the bottom of Step 2; we’ll compare it to the modeled baseline and suggest next checks.",
        "es": "La siguiente pantalla es una **calculadora**, no una nota sobre tu mercado:\n\n- **B25105** mezcla muchas situaciones.\n- **B25077** es solo **precio por defecto** — sustitúyelo por anuncio, tasación o cifra del prestamista.\n- El **tipo** parte de la media **nacional** 30 años (FRED); tu oferta real depende de crédito, puntos y momento.\n\nPuedes poner tu **todo incluido real** al final del Paso 2; lo compararemos con el modelo.",
        "zh": "下一屏是**计算器**，不是给市场打分：\n\n- **业主成本中位数 (B25105)** 混合多种情况，可能高于或低于你实际支付。\n- **房价中位数 (B25077)** 只是**默认价** — 请换成挂牌、评估或银行数字。\n- **利率**起始于 **FRED** 全国 30 年均值；实际报价取决于信用、点数与时间。\n\n你仍可在第 2 步底部填写**真实月全包**；我们会与模型基线对比并提示下一步。",
    },
    "house_btn_verify": {
        "en": "Verify & continue to mortgage model →",
        "es": "Verificar y continuar al modelo hipotecario →",
        "zh": "确认并继续到按揭模型 →",
    },
    "house_own_step2": {
        "en": "Step 2 · Mortgage & monthly baseline",
        "es": "Paso 2 · Hipoteca y línea base mensual",
        "zh": "步骤 2 · 按揭与月基线",
    },
    "house_from_unsure_info": {
        "en": "**From “Unsure” in Step 1:** treat **home price** and **rate** as placeholders — edit them to match a listing, Loan Estimate, or what your loan officer quoted. The modeled monthly baseline updates as you change inputs.",
        "es": "**Desde “No seguro” en Paso 1:** precio y tipo son **marcadores de posición** — edítalos según anuncio, Loan Estimate u oferta del banco. La línea base se actualiza al cambiar entradas.",
        "zh": "**来自第 1 步“不确定”：** 请将**房价**与**利率**视为占位 — 按挂牌、贷款估算表或银行报价修改。模型月基线会随输入更新。",
    },
    "house_fred_ok": {
        "en": "**Reference rate (FRED `MORTGAGE30US`, weekly):** **{rate}%** — editable below. Not a loan offer.",
        "es": "**Tipo referencia (FRED `MORTGAGE30US`, semanal):** **{rate}%** — editable abajo. No es oferta de préstamo.",
        "zh": "**参考利率（FRED `MORTGAGE30US`，周）：** **{rate}%** — 下方可改。非贷款要约。",
    },
    "house_fred_fail": {
        "en": "**Could not load FRED** (timeout or network). Using **{rate}%** as a placeholder — type your lender’s APR below. Not a loan offer.",
        "es": "**No se pudo cargar FRED** (red). Usamos **{rate}%** como marcador — pon el APR de tu prestamista. No es oferta.",
        "zh": "**无法加载 FRED**（超时或网络）。暂用 **{rate}%** — 请在下方填写银行 APR。非贷款要约。",
    },
    "house_back_median": {
        "en": "← Back to median review",
        "es": "← Volver a medianas",
        "zh": "← 返回中位数审阅",
    },
    "house_inp_home_price": {
        "en": "Home value / purchase price for the model ($)",
        "es": "Valor / precio de compra para el modelo ($)",
        "zh": "模型用房价 / 购买价（$）",
    },
    "house_slider_down": {"en": "Down payment (%)", "es": "Entrada (%)", "zh": "首付 (%)"},
    "house_inp_rate": {"en": "Annual interest rate (%)", "es": "Tipo de interés anual (%)", "zh": "年利率 (%)"},
    "house_sel_term": {"en": "Loan term (years)", "es": "Plazo del préstamo (años)", "zh": "贷款期限（年）"},
    "house_prop_tax_lbl": {
        "en": "Property type — **estimated** monthly property tax",
        "es": "Tipo de vivienda — impuesto mensual **estimado**",
        "zh": "房屋类型 — **估算**月房产税",
    },
    "house_prop_apt": {
        "en": "Condo / apartment / similar (**${mo:,.0f}/mo**)",
        "es": "Piso / apartamento / similar (**${mo:,.0f}/mes**)",
        "zh": "公寓/类似（**${mo:,.0f}/月**）",
    },
    "house_prop_house": {
        "en": "House — single-family or larger (**${mo:,.0f}/mo**)",
        "es": "Casa unifamiliar o mayor (**${mo:,.0f}/mes**)",
        "zh": "独栋或更大（**${mo:,.0f}/月**）",
    },
    "house_modeled_breakdown": {
        "en": "**Modeled monthly breakdown** — utilities & insurance are **rules of thumb** vs P&I; property tax is a **fixed monthly estimate**: **${apt}** (apartment-style) or **${house}** (house), per your selection above.",
        "es": "**Desglose mensual modelado** — servicios y seguro son **reglas prácticas** vs P&I; impuesto es **fijo mensual estimado**: **${apt}** (piso) o **${house}** (casa), según arriba.",
        "zh": "**模型月分项** — 水电与保险相对本息为**经验比例**；房产税为**固定月估算**：**${apt}**（公寓式）或 **${house}**（独栋），依上选。",
    },
    "house_m_pi": {"en": "Principal + interest", "es": "Capital + interés", "zh": "本息"},
    "house_m_util": {
        "en": "Utilities (~10% of P&I)",
        "es": "Servicios (~10% de P&I)",
        "zh": "水电等（约本息 10%）",
    },
    "house_m_ins": {
        "en": "Insurance (~5% of P&I)",
        "es": "Seguro (~5% de P&I)",
        "zh": "保险（约本息 5%）",
    },
    "house_m_tax": {
        "en": "Property tax (estimated)",
        "es": "Impuesto (estimado)",
        "zh": "房产税（估算）",
    },
    "house_m_tax_help": {
        "en": "Rough placeholder — not your county assessor bill. Switch property type above to change.",
        "es": "Placeholder — no es tu recibo del catastro. Cambia el tipo arriba.",
        "zh": "粗略占位 — 非县估税单。请用上方房屋类型切换。",
    },
    "house_m_total_model": {
        "en": "**Total modeled baseline**",
        "es": "**Total modelo**",
        "zh": "**模型合计基线**",
    },
    "house_model_disclaimer": {
        "en": "Does **not** include HOA, PMI, flood/earthquake riders, or lump repairs. Property tax uses the **simple apartment vs house** rule above, not live tax rolls.",
        "es": "No incluye HOA, PMI, seguros catastróficos ni reparaciones puntuales. Impuesto con regla simple arriba, no recibo real.",
        "zh": "不含 HOA、PMI、洪水/地震附加险或大额维修。房产税用上文**简化的公寓/独栋**规则，非实时税单。",
    },
    "house_actual_allin": {
        "en": "Your **actual** monthly all-in (mortgage + escrow + utilities + insurance + property tax) ($)",
        "es": "Tu **real** mensual todo incluido (hipoteca + escrow + servicios + seguro + impuesto) ($)",
        "zh": "你的**实际**月全包（按揭+托管+杂费+保险+房产税）（$）",
    },
    "house_unsure_worksheet_cap": {
        "en": "**Worksheet & pie (Unsure path):** uses the **modeled baseline** above until this **actual all-in** is above **$0**; then this box is the housing line.",
        "es": "**Hoja y gráfico (ruta “No seguro”):** usan el **modelo** hasta que el **todo incluido real** > **$0**; entonces esta caja es la línea de vivienda.",
        "zh": "**工作表与饼图（不确定路径）：** 在本**实际全包** > **$0** 前用上文**模型基线**；之后以本框为住房行。",
    },
    "house_metric_own_tab": {
        "en": "Housing in worksheet & pie — **Own** tab / mo",
        "es": "Vivienda en hoja y gráfico — pestaña **Propiedad** / mes",
        "zh": "工作表与饼图住房 — **自有**页 / 月",
    },
    "house_metric_own_tab_help": {
        "en": "**Your** owned all-in when filled; **Yes** on medians → **ZIP owner-cost median** when all-in is still **$0**; **Unsure** → **modeled** baseline until you enter actual all-in. The **tracker & pie** use this path only when **Own** is the binding choice above.",
        "es": "Tu todo incluido si lo rellenas; **Sí** en medianas → **mediana coste propietario ZIP** si sigue en **$0**; **No seguro** → **modelo** hasta poner el real. **Tracker y gráfico** solo si **Propiedad** es vinculante arriba.",
        "zh": "填写后用你的自有全包；中位数选**是**且全包仍 **$0** → **邮编业主成本中位数**；**不确定** → **模型**直到填实际全包。**跟踪与饼图**仅当上方**自有**为绑定项时走此路径。",
    },
    "house_saved_next_blurb": {
        "en": "This choice is **saved when you leave this step** (e.g. **Next**) and drives the **tracker**, **pie**, and **exports**.",
        "es": "Esta elección se **guarda al salir** (p. ej. **Siguiente**) y alimenta **tracker**, **gráfico** y **exportaciones**.",
        "zh": "离开本步（如**下一步**）时**保存**，并驱动**跟踪**、**饼图**与**导出**。",
    },
    # --- Car panel ---
    "car_metric_ceiling": {
        "en": "Car spend ceiling (15% take-home)",
        "es": "Tope coche (15% del ingreso neto)",
        "zh": "用车支出上限（实发 15%）",
    },
    "car_metric_ceiling_help": {
        "en": "Rule of thumb: keep **all-in vehicle cost** (payment/lease if any, **estimated depreciation** if you own outright, insurance, fuel, maintenance) often near or below ~**15%** of monthly **after-tax** income — sanity check, not a hard limit.",
        "es": "Regla práctica: mantén el **coste total del vehículo** (cuota/leasing, **depreciación estimada** si es tuyo, seguro, combustible, mantenimiento) cerca o bajo ~**15%** del ingreso **neto** mensual — guía, no límite duro.",
        "zh": "经验法则：**车辆全成本**（若有贷款/租、**估算折旧**、保险、油费、保养）宜接近或低于税后月收入约 **15%** — 仅供参考。",
    },
    "car_ceiling_caption": {
        "en": "Ceiling is framed per **one** vehicle’s worth of budget. **Own outright:** include a **monthly depreciation estimate** (economic loss, not a bill) so totals stay comparable to lease/finance.",
        "es": "El tope es por **un** vehículo. **Propio al contado:** incluye **depreciación mensual estimada** (pérdida económica) para comparar con leasing/financiación.",
        "zh": "上限按**一辆车**计。**全款车：** 请计入**月折旧估算**（经济损耗，非账单）以便与租/贷可比。",
    },
    "car_edu_block": {
        "en": "**Cars are expensive consumables, not investments.** A new vehicle typically **loses a large share of value in the first few years** (often on the order of roughly **half** in ~3 years and **well over half** by ~5 years in many consumer guides — exact loss varies by make, demand, and mileage).\n\nThat **invisible depreciation** stacks on top of **insurance**, **fuel**, **tires/brakes/repairs**, and any **payment or lease** — so the true monthly “burn” is usually **much larger** than a dealer’s payment quote alone.\n\n**Two cars** often mean **two policies**, **twice the maintenance**, and **twice the depreciation story** — for **lower take-home** households, running two newer vehicles can quietly **consume a large slice of cash flow** that could otherwise go to debt, emergencies, or savings.",
        "es": "**Los coches son consumo caro, no inversión.** Un coche nuevo suele **perder mucho valor al inicio** (orden ~**mitad** en ~3 años y **más** en ~5 en muchas guías).\n\nEsa **depreciación invisible** se suma a **seguro**, **combustible**, **neumáticos/frenos/reparaciones** y **cuota o leasing** — el “quemado” mensual real suele ser **mayor** que solo la cuota.\n\n**Dos coches** suelen ser **dos pólizas**, **doble mantenimiento** y **doble depreciación** — con **ingreso moderado**, dos coches nuevos pueden **comerse mucho flujo** que podría ir a deuda, emergencias o ahorro.",
        "zh": "**汽车是昂贵消耗品，不是投资。** 新车前几年通常**大幅贬值**（许多指南约 **3 年半价、5 年更低**，因品牌与里程而异）。\n\n**隐性折旧**叠在**保险、油费、轮胎/刹车/维修**及**月供或租金**之上 — 真实月度“烧掉”的钱往往**远大于**经销商只报月供。\n\n**两辆车**常意味着**两份保单**、**双倍保养**与**双倍折旧故事** — 对**实发不高**的家庭，两辆较新车可能**悄悄吃掉大量现金流**本可用于还债、应急或储蓄。",
    },
    "car_hh_radio": {
        "en": "How many vehicles does your household rely on day to day?",
        "es": "¿Cuántos vehículos usa tu hogar a diario?",
        "zh": "家庭日常依赖几辆车？",
    },
    "car_hh_1": {"en": "1", "es": "1", "zh": "1"},
    "car_hh_2plus": {"en": "2 or more", "es": "2 o más", "zh": "2 辆及以上"},
    "car_warn_two": {
        "en": "If **each** vehicle were in line with the guideline, **two** would stress the budget closer to **~${ceil2:,}/mo** in combined ceiling terms (2 × ~${ceil1:,}) — before counting the **depreciation** you don’t write a check for. At **${inc:,.0f}/mo** take-home, two cars often **hurt the most** in cash flow; many households re-check whether the second car is **necessary** (older paid-off vehicle, stagger commutes, transit, or a deliberate one-car trial).",
        "es": "Si **cada** coche cumpliera la guía, **dos** acercan el presupuesto a **~${ceil2:,}/mes** combinados (2 × ~${ceil1:,}) — sin contar **depreciación** sin talón. Con **${inc:,.0f}/mes** neto, dos coches suelen **lastrar** el flujo; muchos revisan si el segundo es **necesario**.",
        "zh": "若**每辆车**都达指引，**两辆**合计上限约 **~${ceil2:,}/月**（2 × ~${ceil1:,}）— 尚未计**无账单的折旧**。实发 **${inc:,.0f}/月** 时两辆车往往**最伤现金流**；许多家庭会重审第二辆是否**必需**。",
    },
    "car_pay_heading": {"en": "**How you pay for the car**", "es": "**Cómo pagas el coche**", "zh": "**如何为车付款**"},
    "car_status_radio": {"en": "Car status", "es": "Estado del coche", "zh": "车辆状态"},
    "car_st_none": {"en": "No car", "es": "Sin coche", "zh": "无车"},
    "car_st_lease": {"en": "Lease", "es": "Leasing", "zh": "租赁"},
    "car_st_finance": {"en": "Finance", "es": "Financiación", "zh": "贷款"},
    "car_st_own": {"en": "Own outright", "es": "Propio al contado", "zh": "全款自有"},
    "car_md_lease": {
        "en": "**Lease** usually **packages** a predictable monthly number, mileage limits, and turn-in rules — easy to budget month-to-month, but **total cost** can hide excess mileage, wear charges, disposition fees, and **continuous payments** if you roll from lease to lease.",
        "es": "**Leasing** suele **empaquetar** cuota fija, límite de km y reglas de devolución — fácil de presupuestar, pero el **coste total** puede esconder km de más, cargos y **pagos continuos** si renuevas siempre.",
        "zh": "**租赁**通常**打包**可预期月付、里程与还车规则 — 按月好做预算，但**总成本**可能含超里程、车损费、还车费及**连续租约**的持续付款。",
    },
    "car_md_finance": {
        "en": "**Finance** spreads purchase price plus **interest (APR)** into payments — also highly **“productized”** (term length, lender fees, gap add-ons). Compare **total paid vs cash price** and shop APR; early-years depreciation can mean you **owe more than resale value** (“underwater”) for a while.",
        "es": "**Financiación** reparte precio + **interés (TAE)** en cuotas — muy **“productizada”** (plazo, comisiones, extras). Compara **total pagado vs al contado** y compara TAE; la depreciación temprana puede dejarte **debajo del valor de reventa** un tiempo.",
        "zh": "**贷款**把车价加**利息（APR）**摊到月供 — 也很**“产品化”**（期限、费用、附加险）。比较**总付款与现金价**并比价 APR；早期折旧可能让你一度**欠款高于残值**（“水下”）。",
    },
    "car_md_own": {
        "en": "**Own outright** drops the loan/lease payment, but **depreciation**, **insurance**, **fuel**, and **repairs** still flow — and an older paid-off car is often the **lowest-cash-flow** option if reliability stays acceptable.",
        "es": "**Propio al contado** elimina cuota, pero siguen **depreciación**, **seguro**, **combustible** y **reparaciones** — un coche viejo pagado suele ser la opción de **menor flujo de caja** si aguanta bien.",
        "zh": "**全款自有**无贷款/租约月供，但**折旧、保险、油费、维修**仍在 — 若可靠性尚可，旧车常是**现金流压力最小**的选择。",
    },
    "car_md_transit": {
        "en": "**No car — public & shared mobility.** Many people get around with **buses, subways, commuter rail, light rail**, and **monthly or annual passes** instead of owning a vehicle. Some add **bike-share**, **ferry**, or **occasional taxi / rideshare** when that’s part of a typical month.\n\nCosts **vary a lot** by city, commute distance, and discounts (student/senior/employer). **There’s no single “correct” budget** — use your real pass price, ticket history, and typical extra rides to pick a **monthly total** below (you can change it anytime).",
        "es": "**Sin coche — transporte público y compartido.** Mucha gente usa **bus, metro, cercanías** y **abonos** en lugar de coche. Algunos suman **bici pública**, **ferry** o **taxi/VTC** ocasional.\n\nLos costes **varían mucho** por ciudad y trayecto. **No hay un presupuesto “correcto”** — usa tus precios reales abajo (cámbialo cuando quieras).",
        "zh": "**无车 — 公交与共享出行。** 许多人靠**公交、地铁、市郊铁路、轻轨**及**月票/年票**出行，也有人加**共享单车、轮渡**或**偶尔打车**。\n\n成本因城市、通勤与优惠**差异很大**。**没有唯一“正确”预算** — 请用真实票价与习惯在下方填**月合计**（可随时改）。",
    },
    "car_dep_expander": {
        "en": "Illustrative depreciation (new car — not tax or resale advice)",
        "es": "Depreciación ilustrativa (coche nuevo — no es asesoría fiscal ni de reventa)",
        "zh": "示意折旧（新车 — 非税务或残值建议）",
    },
    "car_dep_caption": {
        "en": "We use **illustrative** resale values of about **{r3:.0%}** of purchase price after 3 years and **{r5:.0%}** after 5 years — mid-range figures from many consumer summaries; your market will differ.",
        "es": "Usamos valores **ilustrativos** de reventa ~**{r3:.0%}** a 3 años y ~**{r5:.0%}** a 5 años — cifras medias de muchas guías; tu mercado variará.",
        "zh": "采用**示意**残值：约 **{r3:.0%}**（3 年）与 **{r5:.0%}**（5 年）— 来自常见消费指南区间；你所在市场会不同。",
    },
    "car_dep_example_price": {
        "en": "Example: what did the vehicle cost new (or current value when new)? ($)",
        "es": "Ejemplo: ¿precio nuevo del vehículo (o valor cuando era nuevo)? ($)",
        "zh": "示例：新车价（或当年新购价值）？（$）",
    },
    "car_dep_lines": {
        "en": "- **After ~3 years:** illustrative value ~**${v3:,}** → economic loss ~**${d3:,}** (~**${a3:,.0f}/mo** averaged depreciation alone)\n- **After ~5 years:** illustrative value ~**${v5:,}** → loss ~**${d5:,}** (~**${a5:,.0f}/mo** averaged)",
        "es": "- **~3 años:** valor ~**${v3:,}** → pérdida ~**${d3:,}** (~**${a3:,.0f}/mes** solo depreciación)\n- **~5 años:** valor ~**${v5:,}** → pérdida ~**${d5:,}** (~**${a5:,.0f}/mes**)",
        "zh": "- **约 3 年：** 示意残值 ~**${v3:,}** → 经济损耗 ~**${d3:,}**（仅折旧均摊 ~**${a3:,.0f}/月**）\n- **约 5 年：** 残值 ~**${v5:,}** → 损耗 ~**${d5:,}**（~**${a5:,.0f}/月**）",
    },
    "car_dep_add_ons": {
        "en": "Add insurance, gas, maintenance, and any payment on top of these averages.",
        "es": "Suma seguro, gasolina, mantenimiento y cualquier cuota encima de estos promedios.",
        "zh": "请在此平均值之上另加保险、油费、保养及任何月供。",
    },
    "car_mob_budget_title": {
        "en": "Your monthly mobility budget",
        "es": "Tu presupuesto mensual de movilidad",
        "zh": "你的月度出行预算",
    },
    "car_mob_budget_cap": {
        "en": "Optional shortcuts — edit the box to match **your** situation",
        "es": "Atajos opcionales — edita la caja para **tu** caso",
        "zh": "可选快捷 — 请改数字以符合**你的**情况",
    },
    "car_chip_transit_75": {"en": "$75 / mo", "es": "$75 / mes", "zh": "$75/月"},
    "car_chip_transit_150": {"en": "$150 / mo", "es": "$150 / mes", "zh": "$150/月"},
    "car_chip_transit_300": {"en": "$300 / mo", "es": "$300 / mes", "zh": "$300/月"},
    "car_transit_inp": {
        "en": "Public transit & shared mobility per month ($)",
        "es": "Transporte público y compartido al mes ($)",
        "zh": "公交与共享出行/月（$）",
    },
    "car_transit_help": {
        "en": "Passes, commuter rail, bus/subway, ferry, bike-share, plus any regular rides you count as mobility — **your** number.",
        "es": "Abonos, cercanías, bus/metro, ferry, bici pública y viajes habituales que cuentes como movilidad — **tu** cifra.",
        "zh": "月票、市郊铁路、公交/地铁、轮渡、共享单车及你计入出行的常规费用 — **你的**数字。",
    },
    "car_transit_info": {
        "en": "**${m:,}/mo** toward mobility — **you** chose this amount. We don’t apply the **15% car ceiling** here; transit costs don’t match that rule of thumb.",
        "es": "**${m:,}/mes** en movilidad — elegido por **ti**. No aplicamos el **tope 15% coche** aquí; el transporte no encaja en esa regla.",
        "zh": "**${m:,}/月**用于出行 — 由**你**填写。此处**不适用 15% 用车上限**；公交成本不适用该经验法则。",
    },
    "car_monthly_costs_title": {
        "en": "Monthly vehicle costs",
        "es": "Costes mensuales del vehículo",
        "zh": "车辆月度成本",
    },
    "car_monthly_costs_cap": {
        "en": "Enter **each line** below — we sum them for the total. **Own outright:** depreciation is an **economic** estimate (value loss), not cash; **Lease/Finance:** use your real payment.",
        "es": "Rellena **cada línea** — sumamos el total. **Propio:** depreciación es **económica** (pérdida de valor), no efectivo; **Leasing/Financiación:** tu cuota real.",
        "zh": "请逐行填写 — 我们求和。**全款：** 折旧为**经济**估算（贬值），非现金；**租/贷：** 填真实月供。",
    },
    "car_inp_lease": {"en": "Lease payment ($/mo)", "es": "Cuota leasing ($/mes)", "zh": "租赁月供（$/月）"},
    "car_inp_finance": {"en": "Auto loan payment ($/mo)", "es": "Cuota préstamo coche ($/mes)", "zh": "车贷月供（$/月）"},
    "car_inp_dep": {
        "en": "Depreciation — economic estimate ($/mo)",
        "es": "Depreciación — estimación económica ($/mes)",
        "zh": "折旧 — 经济估算（$/月）",
    },
    "car_inp_dep_help": {
        "en": "Not a bill you pay each month — rough **value loss** per month. Use the depreciation expander for ballparks, then adjust.",
        "es": "No es un recibo mensual — **pérdida de valor** aproximada. Usa el expander de depreciación y ajusta.",
        "zh": "非每月账单 — 粗略**贬值**。可用上方折旧说明估区间再调整。",
    },
    "car_inp_ins": {"en": "Insurance ($/mo)", "es": "Seguro ($/mes)", "zh": "保险（$/月）"},
    "car_inp_fuel": {
        "en": "Fuel ($/mo)",
        "es": "Combustible ($/mes)",
        "zh": "油费/能源（$/月）",
    },
    "car_inp_fuel_help": {
        "en": "Gas/electric “fuel”; add typical charging if you track it here.",
        "es": "Gasolina/eléctrico; añade carga típica si lo llevas aquí.",
        "zh": "油/电“能源”；若在此统计，可计入常规充电。",
    },
    "car_inp_maint": {
        "en": "Maintenance & repairs ($/mo)",
        "es": "Mantenimiento y reparaciones ($/mes)",
        "zh": "保养与维修（$/月）",
    },
    "car_inp_maint_help": {
        "en": "Oil changes, tires, brakes, registration amortized, averaged unexpected repairs.",
        "es": "Aceite, neumáticos, frenos, registro amortizado, reparaciones imprevistas promediadas.",
        "zh": "换油、轮胎、刹车、摊销的注册费、平均意外维修。",
    },
    "car_total_metric": {
        "en": "Total estimated monthly vehicle cost",
        "es": "Coste mensual estimado del vehículo",
        "zh": "估算月车辆总成本",
    },
    "car_bundle_exp": {
        "en": "Quick-fill example bundles (optional)",
        "es": "Paquetes de ejemplo rápidos (opcional)",
        "zh": "快速示例组合（可选）",
    },
    "car_bundle_cap": {
        "en": "Rough starting points — **edit every line** afterward.",
        "es": "Puntos de partida — **edita todas las líneas** después.",
        "zh": "粗略起点 — 之后请**逐行修改**。",
    },
    "car_bundle_low": {"en": "Lower-cost mix", "es": "Mix económico", "zh": "较低成本组合"},
    "car_bundle_mid": {"en": "Mid mix", "es": "Mix medio", "zh": "中等组合"},
    "car_bundle_high": {"en": "Higher-cost mix", "es": "Mix alto", "zh": "较高成本组合"},
    "car_part_payment": {
        "en": "Payment **${v:,.0f}**",
        "es": "Cuota **${v:,.0f}**",
        "zh": "月供 **${v:,.0f}**",
    },
    "car_part_dep": {
        "en": "Depreciation **${v:,.0f}**",
        "es": "Depreciación **${v:,.0f}**",
        "zh": "折旧 **${v:,.0f}**",
    },
    "car_part_ins": {
        "en": "Insurance **${v:,.0f}**",
        "es": "Seguro **${v:,.0f}**",
        "zh": "保险 **${v:,.0f}**",
    },
    "car_part_fuel": {
        "en": "Fuel **${v:,.0f}**",
        "es": "Combustible **${v:,.0f}**",
        "zh": "油费 **${v:,.0f}**",
    },
    "car_part_maint": {
        "en": "Maintenance **${v:,.0f}**",
        "es": "Mantenimiento **${v:,.0f}**",
        "zh": "保养 **${v:,.0f}**",
    },
    "car_mobility_pie_metric": {
        "en": "Mobility in worksheet & pie / mo",
        "es": "Movilidad en hoja y gráfico / mes",
        "zh": "工作表与饼图出行 / 月",
    },
    "car_mobility_pie_help": {
        "en": "**No car:** same as **Public transit & shared mobility / mo**. **Lease, Finance, or Own outright:** same as **Total estimated monthly vehicle cost** (sum of lines). All lines **$0** → **$0** here and in the pie / JSON.",
        "es": "**Sin coche:** igual que **transporte público / mes**. **Leasing/Financiación/Propio:** igual que **total vehículo**. Todo **$0** → **$0** aquí y en el gráfico/JSON.",
        "zh": "**无车：** 同 **公交与共享出行/月**。**租/贷/全款：** 同 **估算月车辆总成本**。全为 **$0** → 此处与饼图/JSON 均为 **$0**。",
    },
    # --- Child / grocery / entertainment ---
    "child_has_kids": {
        "en": "Your questionnaire profile includes children — add typical monthly amounts by category below.",
        "es": "Tu perfil incluye hijos — añade importes mensuales típicos por categoría abajo.",
        "zh": "问卷显示有孩 — 请在下方按类别填写典型月度金额。",
    },
    "child_no_kids": {
        "en": "Profile without kids — still useful to sketch **future** costs or occasional child-related spending.",
        "es": "Perfil sin hijos — aún útil para **futuros** gastos u ocasionales relacionados con niños.",
        "zh": "问卷无孩 — 仍可草估**未来**或偶发育儿支出。",
    },
    "child_cap": {
        "en": "Categories cover many families’ big buckets (school, care, coverage, fun). Use **$0** where something doesn’t apply. **No ceiling** here — costs swing by age, city, and choices.",
        "es": "Categorías típicas (colegio, cuidado, cobertura, ocio). Pon **$0** si no aplica. **Sin tope** — varía por edad, ciudad y decisiones.",
        "zh": "分类覆盖常见大项（学业、照护、保险、玩乐）。不适用填 **$0**。**不设上限** — 因年龄、城市与选择差异很大。",
    },
    "child_title": {
        "en": "Monthly child-related expenses",
        "es": "Gastos mensuales relacionados con hijos",
        "zh": "育儿相关月支出",
    },
    "child_inp_tuition": {
        "en": "Tuition & school fees ($/mo)",
        "es": "Matrícula y tasas escolares ($/mes)",
        "zh": "学费与学杂费（$/月）",
    },
    "child_inp_tuition_h": {
        "en": "School tuition, program fees, supplies/books, field trips averaged monthly.",
        "es": "Colegio, tasas, material, excursiones promediadas al mes.",
        "zh": "学费、项目费、书本用品、研学等按月摊销。",
    },
    "child_inp_care": {
        "en": "Childcare & after-school care ($/mo)",
        "es": "Guardería y extracurricular ($/mes)",
        "zh": "托育与课后照护（$/月）",
    },
    "child_inp_care_h": {
        "en": "Daycare, aftercare, regular babysitting, nanny share — your typical month.",
        "es": "Guardería, tardes, canguro habitual, nanny share — tu mes típico.",
        "zh": "日托、课后、固定保姆、共享保姆 — 你的典型月份。",
    },
    "child_inp_ins": {
        "en": "Insurance — child’s share ($/mo)",
        "es": "Seguro — parte del niño ($/mes)",
        "zh": "保险 — 孩子分摊（$/月）",
    },
    "child_inp_ins_h": {
        "en": "Portion of premiums or kid-specific medical/dental/vision you attribute here.",
        "es": "Parte de primas o gasto médico/dental/vision infantil que atribuyas aquí.",
        "zh": "你归到这里的保费或儿保/牙科/视力份额。",
    },
    "child_inp_act": {
        "en": "Activities, sports, lessons ($/mo)",
        "es": "Actividades, deportes, clases ($/mes)",
        "zh": "活动、运动、兴趣班（$/月）",
    },
    "child_inp_act_h": {
        "en": "Teams, music, tutoring, camps spread over the year.",
        "es": "Equipos, música, refuerzo, campamentos repartidos en el año.",
        "zh": "球队、音乐、补习、营地等按年摊到月。",
    },
    "child_inp_ent": {
        "en": "Entertainment, toys, outings ($/mo)",
        "es": "Ocio, juguetes, salidas ($/mes)",
        "zh": "娱乐、玩具、外出（$/月）",
    },
    "child_inp_ent_h": {
        "en": "Games, streaming kids use, movies, hobbies, small trips.",
        "es": "Juegos, streaming infantil, cine, hobbies, escapadas.",
        "zh": "游戏、儿童流媒体、电影、爱好、短途。",
    },
    "child_inp_clo": {
        "en": "Clothing, diapers, essentials ($/mo)",
        "es": "Ropa, pañales, básicos ($/mes)",
        "zh": "衣物、尿布、必需品（$/月）",
    },
    "child_inp_clo_h": {
        "en": "Clothes, shoes, diapers, basics — averaged.",
        "es": "Ropa, zapatos, pañales, básicos — promediado.",
        "zh": "衣鞋、尿布、基础用品 — 平均。",
    },
    "child_inp_other": {
        "en": "Other child costs ($/mo)",
        "es": "Otros gastos de hijos ($/mes)",
        "zh": "其他育儿支出（$/月）",
    },
    "child_inp_other_h": {
        "en": "Anything else you want in the monthly picture (gifts, tech, specialized care, etc.).",
        "es": "Cualquier otro gasto mensual (regalos, tecnología, cuidados especializados…).",
        "zh": "其他希望计入月度画面的支出（礼物、设备、特殊照护等）。",
    },
    "child_sum_cap": {
        "en": "School **${tui:,.0f}** + Care **${care:,.0f}** + Insurance **${ins:,.0f}** + Activities **${act:,.0f}** + Fun **${ent:,.0f}** + Essentials **${clo:,.0f}** + Other **${oth:,.0f}** → **${tot:,}/mo**",
        "es": "Colegio **${tui:,.0f}** + Cuidado **${care:,.0f}** + Seguro **${ins:,.0f}** + Actividades **${act:,.0f}** + Ocio **${ent:,.0f}** + Básicos **${clo:,.0f}** + Otro **${oth:,.0f}** → **${tot:,}/mes**",
        "zh": "学业 **${tui:,.0f}** + 照护 **${care:,.0f}** + 保险 **${ins:,.0f}** + 活动 **${act:,.0f}** + 玩乐 **${ent:,.0f}** + 必需品 **${clo:,.0f}** + 其他 **${oth:,.0f}** → **${tot:,}/月**",
    },
    "child_total_metric": {
        "en": "Total estimated monthly child costs",
        "es": "Total estimado mensual hijos",
        "zh": "估算月育儿总支出",
    },
    "groc_info_block": {
        "en": "**How much do US households spend on groceries (food at home)?**  \nFederal analysts publish **monthly food-at-home cost** benchmarks by household makeup (USDA “official food plans” — thrift through liberal tiers). For a profile like **{fam}**, **moderate-cost–style** national figures are often in a **very rough ~${lo:,}–${hi:,}/month** range before your city, stores, diet, and food waste change the outcome.\n\nSeparately, **many families** use a simple **~10–15% of after-tax income** as a **conversation starter** for at-home food — it’s not the same methodology as USDA tables, and it breaks for very high or very low incomes.\n\n**Enter whatever matches your real receipts** below — these are orientation, not a target or cap.",
        "es": "**¿Cuánto gastan las familias de EE. UU. en comida en casa?**  \nHay referencias mensuales por tipo de hogar (planes USDA). Para un perfil como **{fam}**, cifras nacionales “moderadas” suelen rondar **~${lo:,}–${hi:,}/mes** muy a grosso modo antes de ciudad, tienda y hábitos.\n\nMuchas familias usan **~10–15% del ingreso neto** solo como **punto de conversación** — no es la misma metodología USDA.\n\n**Pon lo que digan tus tickets** abajo — orientación, no objetivo ni tope.",
        "zh": "**美国家庭在家食品花多少？**  \n联邦分析机构按家庭结构发布**在家食品**月度参考（USDA 官方食物计划等级）。类似 **{fam}** 的画像，全国“中等”口径粗略常在 **~${lo:,}–${hi:,}/月** 量级，城市、门店、饮食与浪费会改变结果。\n\n另有许多家庭用税后收入 **约 10–15%** 作为**聊天起点** — 与 USDA 方法不同，极高/低收入会失真。\n\n**请按真实小票**在下方填写 — 仅供定位，非目标或上限。",
    },
    "groc_why_spread": {
        "en": "Why the spread is so large",
        "es": "Por qué el rango es tan amplio",
        "zh": "为何区间这么大",
    },
    "groc_why_body": {
        "en": "- **Kids’ ages** (calories, formula, school lunch), **special diets**, and **organic vs conventional** move totals a lot.  \n- **Urban vs rural**, **discount vs specialty** grocers, and how much you **eat out** (not counted here) all matter.  \n- USDA tables assume **all meals at home** prepared from their market baskets — real life rarely matches that exactly.",
        "es": "- **Edades** (calorías, fórmula, comedor escolar), **dietas especiales**, **orgánico vs convencional**.  \n- **Ciudad vs rural**, tipo de tienda y cuánto **comes fuera** (no va aquí).  \n- Las tablas USDA asumen **todo en casa** — la vida real rara vez coincide.",
        "zh": "- **孩子年龄**（热量、配方奶、校餐）、**特殊饮食**、**有机/常规**影响大。  \n- **城乡**、**折扣/精品**超市、**外食**比例（此处不计）都重要。  \n- USDA 假设**全在家**按篮子做饭 — 现实很少完全一致。",
    },
    "groc_shortcut_cap": {
        "en": "Shortcuts from **your** take-home (rounded) — optional; you can ignore and type your own total",
        "es": "Atajos desde **tu** ingreso neto (redondeado) — opcional; ignóralos y escribe tu total",
        "zh": "按**你的**实发取整的快捷 — 可选；也可无视并自填总额",
    },
    "groc_monthly_inp": {
        "en": "Monthly groceries — food at home (est., $)",
        "es": "Comida mensual en casa (est., $)",
        "zh": "每月在家食品杂货（估算，$）",
    },
    "groc_monthly_help": {
        "en": "Exclude most restaurant delivery unless you treat it as groceries — consistency matters for you, not us.",
        "es": "Excluye delivery de restaurante salvo que lo cuentes como compra — la coherencia es tuya.",
        "zh": "除非你把外卖当杂货，否则多数外送不计 — 口径一致即可。",
    },
    "ent_info_block": {
        "en": "**Totals above ~$200/mo are very common** when dining out, subscriptions, a few treats, and an occasional trip or show are averaged in.\n\nBelow are **five broad buckets** plus **Other** — each line rolls several habit types together so you can move fast. If something is already in **Child**, skip double-counting on **Social & family fun**.",
        "es": "**Totales >~200 $/mes son muy habituales** con salidas, suscripciones, caprichos y algún viaje o espectáculo.\n\nCinco bloques amplios + **Otro**. Si ya está en **Hijos**, evita duplicar en **Social y familia**.",
        "zh": "外食、订阅、小享受加上偶尔旅行或演出摊到月，**超过约 200 美元/月很常见**。\n\n下方 **五个大类** 加 **其他** — 每行合并多种习惯以便快速填写。若已在**育儿**中计入，**社交与家庭玩乐**勿重复。",
    },
    "ent_vibe_cap": {
        "en": "**Spending style:** **{vibe}** · **Household:** _{family}_ · Take-home **${inc:,.0f}/mo** — use buckets **your** way.",
        "es": "**Estilo:** **{vibe}** · **Hogar:** _{family}_ · Ingreso neto **${inc:,.0f}/mes** — usa los bloques a **tu** manera.",
        "zh": "**消费习惯：** **{vibe}** · **家庭：** _{family}_ · 实发 **${inc:,.0f}/月** — 分类按**你**的方式用。",
    },
    "ent_title": {
        "en": "Monthly entertainment & discretionary fun",
        "es": "Ocio y gasto discrecional mensual",
        "zh": "月度娱乐与可自由支配消费",
    },
    "ent_inp_out": {
        "en": "Eating & drinking out ($/mo)",
        "es": "Comer y beber fuera ($/mes)",
        "zh": "外出餐饮（$/月）",
    },
    "ent_inp_out_h": {
        "en": "Restaurants, meal delivery (not groceries), coffee shops, bars & nightlife.",
        "es": "Restaurantes, delivery (no compra), cafeterías, bares y vida nocturna.",
        "zh": "餐厅、外卖（非杂货）、咖啡馆、酒吧与夜生活。",
    },
    "ent_inp_media": {
        "en": "Subscriptions & paid media ($/mo)",
        "es": "Suscripciones y medios de pago ($/mes)",
        "zh": "订阅与付费媒体（$/月）",
    },
    "ent_inp_media_h": {
        "en": "Streaming, music/gaming subs, premium apps, audiobooks, news & podcasts.",
        "es": "Streaming, música/videojuegos, apps premium, audiolibros, noticias y podcasts.",
        "zh": "流媒体、音乐/游戏订阅、高级应用、有声书、新闻与播客。",
    },
    "ent_inp_trips": {
        "en": "Events, shows & travel ($/mo)",
        "es": "Eventos, espectáculos y viajes ($/mes)",
        "zh": "活动、演出与旅行（$/月）",
    },
    "ent_inp_trips_h": {
        "en": "Tickets, concerts, sports; trips & hotels — **annual cost ÷ 12** works.",
        "es": "Entradas, conciertos, deportes; viajes y hoteles — **anual ÷ 12**.",
        "zh": "门票、演唱会、体育；旅行与酒店 — **年费÷12** 即可。",
    },
    "ent_inp_play": {
        "en": "Hobbies, sports & fun shopping ($/mo)",
        "es": "Aficiones, deporte y compras de ocio ($/mes)",
        "zh": "爱好、运动与玩乐购物（$/月）",
    },
    "ent_inp_play_h": {
        "en": "Gym/studio, hobbies, games, discretionary clothes & gadgets for fun.",
        "es": "Gimnasio/estudio, hobbies, juegos, ropa y gadgets discrecionales.",
        "zh": "健身房/工作室、爱好、游戏、玩乐向衣饰与小玩意。",
    },
    "ent_inp_social": {
        "en": "Social, gifts & family fun ($/mo)",
        "es": "Social, regalos y ocio familiar ($/mes)",
        "zh": "社交、礼物与家庭玩乐（$/月）",
    },
    "ent_inp_social_h": {
        "en": "Dating, parties, gifts, kids’ outings — optional if already under **Child**.",
        "es": "Citas, fiestas, regalos, salidas con niños — opcional si ya va en **Hijos**.",
        "zh": "约会、聚会、礼物、带娃外出 — 若已在**育儿**可不再计。",
    },
    "ent_inp_other": {
        "en": "Other entertainment ($/mo)",
        "es": "Otro ocio ($/mes)",
        "zh": "其他娱乐（$/月）",
    },
    "ent_inp_other_h": {
        "en": "Anything else: memberships, charity events, oddballs that don’t fit the five lines.",
        "es": "Membresías, eventos benéficos, gastos que no encajan en las cinco líneas.",
        "zh": "会员费、慈善活动、不好归入前五类的支出。",
    },
    "ent_sum_cap": {
        "en": "Out **${out:,.0f}** + Media **${med:,.0f}** + Events/travel **${trp:,.0f}** + Hobbies/shopping **${ply:,.0f}** + Social/family **${soc:,.0f}** + Other **${ot:,.0f}** → **${tot:,}/mo**",
        "es": "Fuera **${out:,.0f}** + Medios **${med:,.0f}** + Eventos/viaje **${trp:,.0f}** + Aficiones/compras **${ply:,.0f}** + Social/familia **${soc:,.0f}** + Otro **${ot:,.0f}** → **${tot:,}/mes**",
        "zh": "外食 **${out:,.0f}** + 媒体 **${med:,.0f}** + 活动/旅行 **${trp:,.0f}** + 爱好/购物 **${ply:,.0f}** + 社交/家庭 **${soc:,.0f}** + 其他 **${ot:,.0f}** → **${tot:,}/月**",
    },
    "ent_total_metric": {
        "en": "Total estimated monthly entertainment & discretionary fun",
        "es": "Total estimado ocio y discrecional",
        "zh": "估算月娱乐与可自由支配合计",
    },
}


def _norm_lang(lang: Any) -> str:
    v = str(lang or "en").strip().lower()
    if v.startswith("zh"):
        return "zh"
    if v.startswith("es"):
        return "es"
    return "en"


def text(key: str, lang: str, **kwargs: Any) -> str:
    """Translate without Streamlit (e.g. ``ss.get('ui_lang')`` from wizard session)."""
    lang = _norm_lang(lang)
    row = STRINGS.get(key) or {}
    template = row.get(lang) or row.get("en") or key
    return template.format(**kwargs) if kwargs else template


def t(key: str, **kwargs: Any) -> str:
    """Translate using ``st.session_state['ui_lang']`` (defaults to English)."""
    try:
        import streamlit as st

        lang = _norm_lang(st.session_state.get("ui_lang", "en"))
    except Exception:
        lang = "en"
    return text(key, lang, **kwargs)
