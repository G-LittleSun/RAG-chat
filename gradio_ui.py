"""
Gradio 界面模块
提供基于 Gradio 的 Web 界面，用于替代传统的 HTML 前端
"""
import gradio as gr
from typing import List, Tuple, Optional
import os
from pathlib import Path

from core.models import ChatModel
from core.session_manager import SessionManager
from core.simple_rag_service import SimpleRAGService
from core.config import config


class GradioInterface:
    """
    Gradio 界面管理类
    整合普通聊天和 RAG 文档问答功能
    """
    
    def __init__(self, chat_model: ChatModel, session_manager: SessionManager, rag_service: SimpleRAGService):
        """
        初始化 Gradio 界面
        
        Args:
            chat_model: 聊天模型实例
            session_manager: 会话管理器实例
            rag_service: RAG 服务实例
        """
        self.chat_model = chat_model
        self.session_manager = session_manager
        self.rag_service = rag_service
        self.current_session_id = None  # 用于普通聊天
        self.current_rag_session_id = None  # 用于 RAG 聊天
        
    def create_interface(self) -> gr.Blocks:
        """
        创建 Gradio 界面
        
        Returns:
            gr.Blocks: Gradio 界面对象
        """
        # 自定义 CSS 样式
        custom_css = """
        /* 容器样式 */
        .chat-container {
            max-width: 900px; 
            margin: 0 auto;
        }
        
        /* 文档卡片样式 */
        .document-card {
            border: 1px solid #e0e0e0; 
            border-radius: 8px; 
            padding: 15px; 
            margin: 10px 0;
        }
        
        /* 状态提示样式 */
        .status-success {
            color: #4caf50; 
            font-weight: bold;
        }
        .status-error {
            color: #f44336; 
            font-weight: bold;
        }
        
        /* ==================== 修复双滚动条问题（终极版本） ==================== */
        
        /* 🎯 核心修复：强制禁用 bubble-wrap 的滚动（所有状态） */
        .bubble-wrap,
        .bubble-wrap.svelte-gjtrl6,
        div.bubble-wrap {
            overflow: visible !important;
            overflow-y: visible !important;
            overflow-x: visible !important;
            max-height: none !important;
            height: auto !important;
        }
        
        /* 🎯 确保 Chatbot 固定高度并可滚动 */
        .chatbot,
        .chatbot.svelte-7ddecg,
        .md.chatbot {
            height: 500px !important;
            max-height: 500px !important;
            min-height: 500px !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }
        
        /* 强制应用到所有可能的父容器 */
        .gradio-container *:not(.chatbot):not(.chatbot *) {
            overflow-y: visible !important;
        }
        
        /* 特别针对 svelte 生成的类 */
        [class*="bubble-wrap"],
        [class*="svelte-gjtrl6"] {
            overflow: visible !important;
            overflow-y: visible !important;
            max-height: none !important;
        }
        """
        
        with gr.Blocks(
            title="RAG-Chat 智能对话系统",
            theme=gr.themes.Soft(primary_hue="blue"),
            css=custom_css
        ) as interface:
            
            gr.Markdown(
                """
                # 🤖 RAG-Chat 智能对话系统
                
                ### 功能介绍
                - **普通聊天**：与 AI 进行自然对话
                - **RAG 文档问答**：上传文档，基于文档内容进行智能问答
                - **会话管理**：自动管理对话历史，支持上下文连续对话
                
                ---
                """
            )
            
            with gr.Tabs() as tabs:
                # ============ 标签页 1: 普通聊天 ============
                with gr.Tab("💬 普通聊天"):
                    chatbot = gr.Chatbot(
                        label="对话窗口",
                        height=500,
                        show_copy_button=True,
                        avatar_images=(None, "🤖")
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="输入消息",
                            placeholder="请输入您的问题...",
                            lines=2,
                            scale=4
                        )
                        send_btn = gr.Button("发送 📤", variant="primary", scale=1)
                    
                    with gr.Row():
                        clear_btn = gr.Button("清除对话 🗑️")
                        new_session_btn = gr.Button("新建会话 ✨")
                    
                    # 隐藏的会话 ID 状态（用于内部逻辑，不显示给用户）
                    session_id_display = gr.State(value="未创建")
                    
                    # 定义普通聊天的交互逻辑
                    def chat_respond(message: str, history: List[Tuple[str, str]], session_id: str):
                        """处理普通聊天消息"""
                        if not message.strip():
                            return history, history, session_id
                        
                        # 如果没有会话，创建新会话（生成 UUID）
                        if session_id == "未创建":
                            import uuid
                            session_id = str(uuid.uuid4())
                            self.current_session_id = session_id
                        
                        # 获取或创建会话对象
                        session = self.session_manager.get_session(session_id)
                        
                        # 生成响应（流式）
                        full_response = ""
                        for chunk in self.chat_model.generate_stream_response(message):
                            full_response += chunk
                        
                        # 添加到会话历史
                        session.add_message("user", message)
                        session.add_message("assistant", full_response)
                        
                        # 更新聊天历史
                        history.append((message, full_response))
                        
                        return history, history, session_id
                    
                    def clear_chat():
                        """清除对话"""
                        if self.current_session_id:
                            session = self.session_manager.get_session(self.current_session_id)
                            session.clear_history()
                        return [], [], self.current_session_id or "未创建"
                    
                    def new_session():
                        """创建新会话"""
                        import uuid
                        new_id = str(uuid.uuid4())
                        self.current_session_id = new_id
                        return [], [], new_id
                    
                    # 绑定事件
                    msg_input.submit(
                        chat_respond,
                        [msg_input, chatbot, session_id_display],
                        [chatbot, chatbot, session_id_display]
                    ).then(
                        lambda: "",
                        None,
                        msg_input
                    )
                    
                    send_btn.click(
                        chat_respond,
                        [msg_input, chatbot, session_id_display],
                        [chatbot, chatbot, session_id_display]
                    ).then(
                        lambda: "",
                        None,
                        msg_input
                    )
                    
                    clear_btn.click(
                        clear_chat,
                        None,
                        [chatbot, chatbot, session_id_display]
                    )
                    
                    new_session_btn.click(
                        new_session,
                        None,
                        [chatbot, chatbot, session_id_display]
                    )
                
                # ============ 标签页 2: RAG 文档问答 ============
                with gr.Tab("📚 RAG 文档问答"):
                    with gr.Row():
                        with gr.Column(scale=4):
                            rag_chatbot = gr.Chatbot(
                                label="文档问答窗口",
                                height=500,
                                show_copy_button=True,
                                avatar_images=(None, "📖")
                            )
                            
                            with gr.Row():
                                rag_msg_input = gr.Textbox(
                                    label="输入问题",
                                    placeholder="请输入关于文档的问题...",
                                    lines=2,
                                    scale=4
                                )
                                rag_send_btn = gr.Button("发送 📤", variant="primary", scale=1)
                            
                            with gr.Row():
                                rag_clear_btn = gr.Button("清除对话 🗑️")
                                rag_new_session_btn = gr.Button("新建会话 ✨")
                        
                        with gr.Column(scale=1):
                            gr.Markdown("### 📁 文档管理")
                            
                            file_upload = gr.File(
                                label="上传文档",
                                file_types=[".pdf", ".txt", ".doc", ".docx"],
                                type="filepath",
                                show_progress="hidden"  # 隐藏上传进度动画
                            )
                            upload_btn = gr.Button("上传 ⬆️", variant="secondary")
                            upload_status = gr.Textbox(
                                label="上传状态",
                                interactive=False,
                                placeholder="等待上传...",
                                lines=3,
                                max_lines=5
                            )
                            
                            gr.Markdown("---")
                            
                            refresh_docs_btn = gr.Button("刷新文档列表 🔄")
                            doc_list = gr.Textbox(
                                label="已上传文档",
                                lines=10,
                                interactive=False,
                                placeholder="暂无文档"
                            )
                    
                    # 隐藏的 RAG 会话 ID 状态（用于内部逻辑）
                    rag_session_id_display = gr.State(value="未创建")
                    
                    # 定义 RAG 聊天的交互逻辑
                    def rag_respond(message: str, history: List[Tuple[str, str]], session_id: str):
                        """处理 RAG 文档问答"""
                        if not message.strip():
                            return history, history, session_id
                        
                        # 如果没有会话，创建新会话（生成 UUID）
                        if session_id == "未创建":
                            import uuid
                            session_id = str(uuid.uuid4())
                            self.current_rag_session_id = session_id
                        
                        try:
                            # 使用 RAG 服务生成响应（使用 rag_chat 方法）
                            response = self.rag_service.rag_chat(message, use_context=True)
                            
                            # 更新聊天历史
                            history.append((message, response))
                            
                            return history, history, session_id
                        except Exception as e:
                            error_msg = f"❌ 查询失败: {str(e)}"
                            history.append((message, error_msg))
                            return history, history, session_id
                    
                    def upload_document(file_path: Optional[str]):
                        """上传文档"""
                        # 验证文件路径
                        if not file_path:
                            return "⚠️ 请先选择文件", get_document_list(), None
                        
                        # 去除空格
                        file_path = str(file_path).strip()
                        if not file_path:
                            return "⚠️ 请先选择文件", get_document_list(), None
                        
                        # 验证文件是否存在
                        file_obj = Path(file_path)
                        if not file_obj.exists():
                            return "❌ 文件不存在或已被删除，请重新选择", get_document_list(), None
                        
                        # 验证文件大小
                        if file_obj.stat().st_size == 0:
                            return "❌ 文件为空，请选择有效的文件", get_document_list(), None
                        
                        try:
                            file_name = file_obj.name
                            
                            # 使用 process_document 处理文档
                            success, doc_id = self.rag_service.process_document(file_path)
                            
                            if success:
                                return f"✅ 文档上传成功！\n文档 ID: {doc_id}\n文件名: {file_name}", get_document_list(), None
                            else:
                                return f"❌ 文档处理失败\n错误信息: {doc_id}", get_document_list(), None
                        except Exception as e:
                            return f"❌ 上传失败: {str(e)}", get_document_list(), None
                    
                    def get_document_list():
                        """获取文档列表"""
                        try:
                            docs = self.rag_service.list_documents()
                            if not docs:
                                return "暂无文档"
                            
                            doc_info = []
                            for i, doc in enumerate(docs, 1):
                                doc_info.append(
                                    f"{i}. 📄 {doc['name']}\n"
                                    f"   📊 {doc['chunks']} 个文本块\n"
                                    f"   🕐 {doc['timestamp']}\n"
                                    f"   🆔 ID: {doc['id']}"
                                )
                            
                            return "\n\n".join(doc_info)
                        except Exception as e:
                            return f"❌ 获取文档列表失败: {str(e)}"
                    
                    def clear_rag_chat():
                        """清除 RAG 对话"""
                        if self.current_rag_session_id:
                            session = self.session_manager.get_session(self.current_rag_session_id)
                            session.clear_history()
                        return [], [], self.current_rag_session_id or "未创建"
                    
                    def new_rag_session():
                        """创建新 RAG 会话"""
                        import uuid
                        new_id = str(uuid.uuid4())
                        self.current_rag_session_id = new_id
                        return [], [], new_id
                    
                    # 绑定 RAG 事件
                    rag_msg_input.submit(
                        rag_respond,
                        [rag_msg_input, rag_chatbot, rag_session_id_display],
                        [rag_chatbot, rag_chatbot, rag_session_id_display]
                    ).then(
                        lambda: "",
                        None,
                        rag_msg_input
                    )
                    
                    rag_send_btn.click(
                        rag_respond,
                        [rag_msg_input, rag_chatbot, rag_session_id_display],
                        [rag_chatbot, rag_chatbot, rag_session_id_display]
                    ).then(
                        lambda: "",
                        None,
                        rag_msg_input
                    )
                    
                    upload_btn.click(
                        upload_document,
                        [file_upload],
                        [upload_status, doc_list, file_upload]  # 添加 file_upload 到输出，用于清空
                    )
                    
                    refresh_docs_btn.click(
                        get_document_list,
                        None,
                        doc_list
                    )
                    
                    rag_clear_btn.click(
                        clear_rag_chat,
                        None,
                        [rag_chatbot, rag_chatbot, rag_session_id_display]
                    )
                    
                    rag_new_session_btn.click(
                        new_rag_session,
                        None,
                        [rag_chatbot, rag_chatbot, rag_session_id_display]
                    )
                    
                    # 页面加载时刷新文档列表
                    interface.load(
                        get_document_list,
                        None,
                        doc_list
                    )
            
            # ============ 页面加载时执行 JavaScript 修复双滚动条 ============
            interface.load(
                None,
                None,
                None,
                js="""
                function() {
                    console.log('🔧 正在应用双滚动条修复...');
                    
                    // 修复函数
                    function fixDoubleScrollbar() {
                        // 禁用所有 bubble-wrap 的滚动
                        document.querySelectorAll('.bubble-wrap, [class*="bubble-wrap"]').forEach(el => {
                            el.style.setProperty('overflow', 'visible', 'important');
                            el.style.setProperty('overflow-y', 'visible', 'important');
                            el.style.setProperty('max-height', 'none', 'important');
                        });
                        
                        // 确保 chatbot 固定高度
                        document.querySelectorAll('.chatbot').forEach(el => {
                            el.style.setProperty('height', '500px', 'important');
                            el.style.setProperty('max-height', '500px', 'important');
                            el.style.setProperty('overflow-y', 'auto', 'important');
                        });
                    }
                    
                    // 立即执行一次
                    fixDoubleScrollbar();
                    
                    // 监听 DOM 变化，持续修复（针对流式响应）
                    const observer = new MutationObserver((mutations) => {
                        fixDoubleScrollbar();
                    });
                    
                    // 开始监听
                    observer.observe(document.body, {
                        childList: true,
                        subtree: true,
                        attributes: true,
                        attributeFilter: ['style', 'class']
                    });
                    
                    console.log('✅ 双滚动条修复已激活（持续监听中）');
                }
                """
            )
        
        return interface


def create_gradio_app(chat_model: ChatModel, session_manager: SessionManager, rag_service: SimpleRAGService) -> gr.Blocks:
    """
    工厂函数：创建 Gradio 应用
    
    Args:
        chat_model: 聊天模型实例
        session_manager: 会话管理器实例
        rag_service: RAG 服务实例
        
    Returns:
        gr.Blocks: Gradio 应用实例
    """
    gradio_interface = GradioInterface(chat_model, session_manager, rag_service)
    return gradio_interface.create_interface()
