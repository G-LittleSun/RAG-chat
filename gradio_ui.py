"""
Gradio 界面模块 V2 - 全新设计
左侧固定侧边栏 + 右侧对话区，类似 ChatGPT 风格
"""
import gradio as gr
from typing import List, Tuple, Optional
from pathlib import Path

from core.models import ChatModel
from core.session_manager import SessionManager
from core.simple_rag_service import SimpleRAGService


class GradioInterface:
    """
    Gradio 界面管理类 - V2版本
    采用左右分栏布局，模式切换在左侧
    """
    
    def __init__(self, chat_model: ChatModel, session_manager: SessionManager, rag_service: SimpleRAGService):
        self.chat_model = chat_model
        self.session_manager = session_manager
        self.rag_service = rag_service
        self.current_session_id = None
        self.current_rag_session_id = None
        self.current_mode = "chat"  # "chat" 或 "rag"
        
    def create_interface(self) -> gr.Blocks:
        """创建全新的 Gradio 界面"""
        
        # 简洁的 CSS 样式
        custom_css = """
        /* 全局样式 */
        body, .gradio-container {
            margin: 0 !important;
            padding: 0 !important;
            font-family: -apple-system, system-ui, sans-serif !important;
        }
        
        /* 隐藏 Gradio 页脚 */
        footer, .footer {
            display: none !important;
        }
        
        /* 对话框样式 */
        .chatbot {
            border: none !important;
            background: transparent !important;
        }
        
        /* 输入框样式 */
        .input-box textarea {
            border-radius: 12px !important;
            border: 1px solid #d9d9e3 !important;
            padding: 12px !important;
        }
        
        /* 按钮样式 */
        .primary-button {
            background: #10a37f !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
        }
        
        .primary-button:hover {
            background: #0d8c6d !important;
        }
        
        .secondary-button {
            background: #f7f7f8 !important;
            color: #202123 !important;
            border: 1px solid #d9d9e3 !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
        }
        
        .secondary-button:hover {
            background: #ececf1 !important;
        }
        
        /* 文件卡片样式 */
        .file-card {
            background: #f7f7f8;
            border: 1px solid #d9d9e3;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
        }
        
        .file-name {
            font-weight: 600;
            color: #202123;
            margin-bottom: 4px;
        }
        
        .file-meta {
            font-size: 12px;
            color: #6e6e80;
        }
        
        /* ==================== 文档列表弹窗（全屏独立页面） ==================== */
        #doc-list-modal {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            background: #ffffff !important;
            z-index: 9999 !important;
            padding: 40px 60px !important;
            overflow-y: auto !important;
            margin: 0 !important;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-header h1 {
            margin: 0;
            font-size: 32px;
            color: #202123;
        }
        
        .doc-list-box {
            border: 1px solid #d9d9e3 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            background: #f7f7f8 !important;
            height: calc(100vh - 280px) !important;
            max-height: calc(100vh - 280px) !important;
            min-height: 500px !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }
        
        /* 文档卡片网格布局 */
        .doc-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            padding: 10px;
        }
        
        @media (max-width: 1400px) {
            .doc-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 900px) {
            .doc-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* 文档卡片样式 */
        .doc-card {
            position: relative;
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(217, 217, 227, 0.6);
            border-radius: 12px;
            padding: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            backdrop-filter: blur(10px);
        }
        
        .doc-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
            border-color: #10a37f;
        }
        
        .doc-icon {
            font-size: 40px;
            margin-bottom: 12px;
            text-align: center;
        }
        
        .doc-title {
            font-size: 15px;
            font-weight: 600;
            color: #202123;
            margin-bottom: 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            text-align: center;
        }
        
        .doc-info {
            font-size: 12px;
            color: #6e6e80;
            text-align: center;
            line-height: 1.6;
        }
        
        .doc-status {
            display: inline-block;
            background: rgba(16, 163, 127, 0.1);
            color: #10a37f;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin-top: 8px;
        }
        
        /* 文档列表滚动条美化 */
        .doc-list-box::-webkit-scrollbar {
            width: 12px !important;
        }
        
        .doc-list-box::-webkit-scrollbar-track {
            background: #e5e5e5 !important;
            border-radius: 6px !important;
            margin: 10px 0 !important;
        }
        
        .doc-list-box::-webkit-scrollbar-thumb {
            background: #10a37f !important;
            border-radius: 6px !important;
            border: 2px solid #e5e5e5 !important;
        }
        
        .doc-list-box::-webkit-scrollbar-thumb:hover {
            background: #0d8c6d !important;
        }
        
        /* 确保按钮样式一致 */
        .secondary-button {
            min-width: 120px !important;
            height: 44px !important;
            font-size: 15px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        """
        
        with gr.Blocks(title="智能文档问答系统", css=custom_css, theme=gr.themes.Soft()) as interface:
            
            # 使用 State 管理当前模式
            mode_state = gr.State(value="chat")
            
            # 使用标准的 Row + Column 布局
            with gr.Row():
                # 左侧栏 (固定宽度)
                with gr.Column(scale=2, min_width=300):
                    # Logo 和标题
                    gr.Markdown(
                        """
                        # 🧠 智能问答系统
                        ---
                        """
                    )
                    
                    # 模式切换按钮
                    gr.Markdown("### 🔄 选择模式")
                    
                    with gr.Row():
                        chat_mode_btn = gr.Button(
                            "💬 普通聊天",
                            elem_classes="primary-button",
                            size="lg"
                        )
                        rag_mode_btn = gr.Button(
                            "📚 文档问答",
                            elem_classes="secondary-button",
                            size="lg"
                        )
                    
                    gr.Markdown("---")
                    
                    # 文档管理区（仅在 RAG 模式显示）
                    with gr.Group(visible=False) as doc_management:
                        gr.Markdown("### 📤 上传文档")
                        gr.Markdown("*支持 PDF, Word, TXT 文件*")
                        
                        file_upload = gr.File(
                            label="选择文件",
                            file_types=[".pdf", ".txt", ".doc", ".docx"],
                            type="filepath"
                        )
                        
                        upload_btn = gr.Button(
                            "⬆️ 上传文档",
                            elem_classes="primary-button",
                            size="lg"
                        )
                        
                        upload_status = gr.Textbox(
                            label="上传状态",
                            interactive=False,
                            lines=2
                        )
                        
                        gr.Markdown("---")
                        
                        # 查看文档列表按钮
                        view_docs_btn = gr.Button(
                            "📋 查看已上传文档",
                            elem_classes="secondary-button",
                            size="lg"
                        )
                
                # 右侧对话区 (占据剩余空间)
                with gr.Column(scale=8):
                    # 模式标题
                    mode_title = gr.Markdown("## 💬 普通聊天模式")
                    
                    # 聊天框
                    chatbot = gr.Chatbot(
                        label="",
                        height=600,
                        show_copy_button=True,
                        avatar_images=(
                            "https://api.dicebear.com/7.x/bottts/svg?seed=user",  # 用户头像
                            "https://api.dicebear.com/7.x/bottts/svg?seed=ai"     # AI 头像
                        ),
                        bubble_full_width=False
                    )
                    
                    # 输入区
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="",
                            placeholder="请输入您的问题...",
                            lines=2,
                            scale=9,
                            show_label=False,
                            elem_classes="input-box"
                        )
                        send_btn = gr.Button(
                            "发送 📤",
                            scale=1,
                            elem_classes="primary-button"
                        )
                    
                    # 操作按钮
                    with gr.Row():
                        clear_btn = gr.Button("🗑️ 清除对话", elem_classes="secondary-button")
                        new_session_btn = gr.Button("✨ 新建会话", elem_classes="secondary-button")
            
            # 文档列表弹窗页面（全屏独立页面）
            with gr.Column(visible=False, elem_id="doc-list-modal") as doc_list_modal:
                # 顶部栏
                with gr.Row(elem_classes="modal-header"):
                    gr.Markdown("# 📋 文档管理中心")

                
                gr.Markdown("---")
                
                # 工具栏
                with gr.Row():
                    refresh_btn = gr.Button(
                        "🔄 刷新列表",
                        elem_classes="secondary-button",
                        size="lg"
                    )
                    close_modal_btn = gr.Button(
                        "❌ 关闭",
                        elem_classes="secondary-button",
                        size="lg"
                    )
                
                gr.Markdown("---")
                
                # 文档列表
                doc_list = gr.HTML(
                    value="<div style='text-align: center; padding: 40px; color: #999;'>📭 暂无文档<br><br>请在左侧上传文档开始使用</div>",
                    elem_classes="doc-list-box",
                    elem_id="doc-list-content"
                )
            
            # 隐藏的状态变量
            session_id_display = gr.State(value="未创建")
            rag_session_id_display = gr.State(value="未创建")
            
            # ==================== 函数定义 ====================
            
            def switch_to_chat():
                """切换到普通聊天模式"""
                return {
                    mode_state: "chat",
                    mode_title: gr.update(value="## 💬 普通聊天模式"),
                    doc_management: gr.update(visible=False),
                    doc_list_modal: gr.update(visible=False),
                    chat_mode_btn: gr.update(elem_classes="primary-button"),
                    rag_mode_btn: gr.update(elem_classes="secondary-button")
                }
            
            def switch_to_rag():
                """切换到文档问答模式"""
                return {
                    mode_state: "rag",
                    mode_title: gr.update(value="## 📚 文档问答模式"),
                    doc_management: gr.update(visible=True),
                    doc_list_modal: gr.update(visible=False),
                    chat_mode_btn: gr.update(elem_classes="secondary-button"),
                    rag_mode_btn: gr.update(elem_classes="primary-button")
                }
            
            def open_doc_list_modal():
                """打开文档列表弹窗"""
                doc_content = get_document_list()
                
                return {
                    doc_list_modal: gr.update(visible=True),
                    doc_list: doc_content
                }
            
            def close_doc_list_modal():
                """关闭文档列表弹窗"""
                return {
                    doc_list_modal: gr.update(visible=False)
                }
            
            def refresh_doc_list():
                """刷新文档列表"""
                doc_content = get_document_list()
                
                return {
                    doc_list: doc_content
                }
            
            def chat_respond(message: str, history: List[Tuple[str, str]], mode: str, 
                           chat_session_id: str, rag_session_id: str):
                """统一的响应函数"""
                if not message.strip():
                    return history, history, chat_session_id, rag_session_id
                
                if mode == "chat":
                    # 普通聊天
                    if chat_session_id == "未创建":
                        import uuid
                        chat_session_id = str(uuid.uuid4())
                        self.current_session_id = chat_session_id
                    
                    session = self.session_manager.get_session(chat_session_id)
                    
                    full_response = ""
                    for chunk in self.chat_model.generate_stream_response(message):
                        full_response += chunk
                    
                    session.add_message("user", message)
                    session.add_message("assistant", full_response)
                    
                    history.append((message, full_response))
                    return history, history, chat_session_id, rag_session_id
                    
                else:
                    # RAG 文档问答
                    if rag_session_id == "未创建":
                        import uuid
                        rag_session_id = str(uuid.uuid4())
                        self.current_rag_session_id = rag_session_id
                    
                    try:
                        response = self.rag_service.rag_chat(message, use_context=True)
                        history.append((message, response))
                        return history, history, chat_session_id, rag_session_id
                    except Exception as e:
                        error_msg = f"❌ 查询失败: {str(e)}"
                        history.append((message, error_msg))
                        return history, history, chat_session_id, rag_session_id
            
            def clear_chat(mode: str, chat_session_id: str, rag_session_id: str):
                """清除对话"""
                if mode == "chat" and self.current_session_id:
                    session = self.session_manager.get_session(self.current_session_id)
                    session.clear_history()
                elif mode == "rag" and self.current_rag_session_id:
                    session = self.session_manager.get_session(self.current_rag_session_id)
                    session.clear_history()
                return [], [], chat_session_id, rag_session_id
            
            def new_session(mode: str, chat_session_id: str, rag_session_id: str):
                """创建新会话"""
                import uuid
                new_id = str(uuid.uuid4())
                if mode == "chat":
                    self.current_session_id = new_id
                    return [], [], new_id, rag_session_id
                else:
                    self.current_rag_session_id = new_id
                    return [], [], chat_session_id, new_id
            
            def upload_document(file_path: Optional[str]):
                """上传文档"""
                if not file_path:
                    return "⚠️ 请先选择文件", None
                
                file_path_str = str(file_path).strip() if isinstance(file_path, str) else str(file_path)
                
                if not file_path_str:
                    return "⚠️ 请先选择文件", None
                
                file_obj = Path(file_path_str)
                if not file_obj.exists():
                    return "❌ 文件不存在", None
                
                if file_obj.stat().st_size == 0:
                    return "❌ 文件为空", None
                
                try:
                    file_name = file_obj.name
                    success, doc_id = self.rag_service.process_document(file_path_str)
                    
                    if success:
                        return (
                            f"✅ 上传成功！\n📄 {file_name}\n🆔 {doc_id}",
                            None
                        )
                    else:
                        return f"❌ 上传失败: {doc_id}", None
                except Exception as e:
                    return f"❌ 上传失败: {str(e)}", None
            
            def get_document_list():
                """获取文档列表（HTML卡片格式）"""
                try:
                    docs = self.rag_service.list_documents()
                    if not docs:
                        return "<div style='text-align: center; padding: 40px; color: #999;'>📭 暂无文档<br><br>请在左侧上传文档开始使用</div>"
                    
                    # 开始HTML
                    html = "<div class='doc-grid'>"
                    
                    for doc in docs:
                        doc_id = doc['id']
                        file_name = doc['name']
                        
                        # 根据文件类型选择图标
                        if file_name.endswith('.pdf'):
                            icon = "📕"
                            file_type = "PDF"
                        elif file_name.endswith(('.doc', '.docx')):
                            icon = "📘"
                            file_type = "Word"
                        elif file_name.endswith('.txt'):
                            icon = "📄"
                            file_type = "TXT"
                        else:
                            icon = "📄"
                            file_type = "文档"
                        
                        # 文件名过长时截断
                        display_name = file_name if len(file_name) <= 25 else file_name[:22] + "..."
                        
                        # 计算文件大小（估算）
                        size_kb = doc['chunks'] * 1
                        if size_kb < 1024:
                            size_str = f"{size_kb} KB"
                        else:
                            size_str = f"{size_kb / 1024:.1f} MB"
                        
                        # 生成卡片HTML
                        html += f"""
                        <div class='doc-card' data-doc-id='{doc_id}'>
                            <div class='doc-icon'>{icon}</div>
                            <div class='doc-title' title='{file_name}'>{display_name}</div>
                            <div class='doc-info'>
                                📊 {doc['chunks']} 个文本块<br>
                                💾 约 {size_str}<br>
                                🕐 {doc['timestamp']}
                            </div>
                            <div style='text-align: center;'>
                                <span class='doc-status'>✅ 已索引</span>
                            </div>
                        </div>
                        """
                    
                    html += "</div>"
                    
                    
                    return html
                    
                except Exception as e:
                    return f"<div style='text-align: center; padding: 40px; color: #f44336;'>❌ 获取失败: {str(e)}</div>"
            
            # ==================== 事件绑定 ====================
            
            # 模式切换
            chat_mode_btn.click(
                switch_to_chat,
                None,
                [mode_state, mode_title, doc_management, doc_list_modal, chat_mode_btn, rag_mode_btn]
            )
            
            rag_mode_btn.click(
                switch_to_rag,
                None,
                [mode_state, mode_title, doc_management, doc_list_modal, chat_mode_btn, rag_mode_btn]
            )
            
            # 文档列表弹窗
            view_docs_btn.click(
                open_doc_list_modal,
                None,
                [doc_list_modal, doc_list]
            )
            
            close_modal_btn.click(
                close_doc_list_modal,
                None,
                [doc_list_modal]
            )
            
            refresh_btn.click(
                refresh_doc_list,
                None,
                [doc_list]
            )
            
            # 发送消息
            msg_input.submit(
                chat_respond,
                [msg_input, chatbot, mode_state, session_id_display, rag_session_id_display],
                [chatbot, chatbot, session_id_display, rag_session_id_display]
            ).then(
                lambda: "",
                None,
                msg_input
            )
            
            send_btn.click(
                chat_respond,
                [msg_input, chatbot, mode_state, session_id_display, rag_session_id_display],
                [chatbot, chatbot, session_id_display, rag_session_id_display]
            ).then(
                lambda: "",
                None,
                msg_input
            )
            
            # 清除和新建
            clear_btn.click(
                clear_chat,
                [mode_state, session_id_display, rag_session_id_display],
                [chatbot, chatbot, session_id_display, rag_session_id_display]
            )
            
            new_session_btn.click(
                new_session,
                [mode_state, session_id_display, rag_session_id_display],
                [chatbot, chatbot, session_id_display, rag_session_id_display]
            )
            
            # 文档上传
            upload_btn.click(
                upload_document,
                [file_upload],
                [upload_status, file_upload]
            )
        
        return interface


def create_gradio_app(chat_model: ChatModel, session_manager: SessionManager, 
                      rag_service: SimpleRAGService) -> gr.Blocks:
    """创建 Gradio 应用的工厂函数"""
    gradio_interface = GradioInterface(chat_model, session_manager, rag_service)
    return gradio_interface.create_interface()
