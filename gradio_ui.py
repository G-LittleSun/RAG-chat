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
        .chat-container {max-width: 900px; margin: 0 auto;}
        .document-card {border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin: 10px 0;}
        .status-success {color: #4caf50; font-weight: bold;}
        .status-error {color: #f44336; font-weight: bold;}
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
                    with gr.Row():
                        with gr.Column(scale=4):
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
                        
                        with gr.Column(scale=1):
                            gr.Markdown("### ⚙️ 设置")
                            session_id_display = gr.Textbox(
                                label="当前会话 ID",
                                value="未创建",
                                interactive=False,
                                lines=2,
                                max_lines=3
                            )
                            history_count = gr.Number(
                                label="历史消息数量",
                                value=0,
                                interactive=False
                            )
                            
                    # 定义普通聊天的交互逻辑
                    def chat_respond(message: str, history: List[Tuple[str, str]], session_id: str):
                        """处理普通聊天消息"""
                        if not message.strip():
                            return history, history, 0, session_id
                        
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
                        
                        # 获取更新后的历史数量
                        updated_history = session.get_history()
                        
                        return history, history, len(updated_history), session_id
                    
                    def clear_chat():
                        """清除对话"""
                        if self.current_session_id:
                            session = self.session_manager.get_session(self.current_session_id)
                            session.clear_history()
                        return [], [], 0, self.current_session_id or "未创建"
                    
                    def new_session():
                        """创建新会话"""
                        import uuid
                        new_id = str(uuid.uuid4())
                        self.current_session_id = new_id
                        return [], [], 0, new_id
                    
                    # 绑定事件
                    msg_input.submit(
                        chat_respond,
                        [msg_input, chatbot, session_id_display],
                        [chatbot, chatbot, history_count, session_id_display]
                    ).then(
                        lambda: "",
                        None,
                        msg_input
                    )
                    
                    send_btn.click(
                        chat_respond,
                        [msg_input, chatbot, session_id_display],
                        [chatbot, chatbot, history_count, session_id_display]
                    ).then(
                        lambda: "",
                        None,
                        msg_input
                    )
                    
                    clear_btn.click(
                        clear_chat,
                        None,
                        [chatbot, chatbot, history_count, session_id_display]
                    )
                    
                    new_session_btn.click(
                        new_session,
                        None,
                        [chatbot, chatbot, history_count, session_id_display]
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
                                type="filepath"
                            )
                            upload_btn = gr.Button("上传 ⬆️", variant="secondary")
                            upload_status = gr.Textbox(
                                label="上传状态",
                                interactive=False,
                                placeholder="等待上传..."
                            )
                            
                            gr.Markdown("---")
                            
                            rag_session_id_display = gr.Textbox(
                                label="当前会话 ID",
                                value="未创建",
                                interactive=False,
                                lines=2,
                                max_lines=3
                            )
                            
                            refresh_docs_btn = gr.Button("刷新文档列表 🔄")
                            doc_list = gr.Textbox(
                                label="已上传文档",
                                lines=8,
                                interactive=False,
                                placeholder="暂无文档"
                            )
                    
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
                            # 使用 RAG 服务生成响应
                            response = self.rag_service.query(message, session_id)
                            
                            # 更新聊天历史
                            history.append((message, response))
                            
                            return history, history, session_id
                        except Exception as e:
                            error_msg = f"❌ 查询失败: {str(e)}"
                            history.append((message, error_msg))
                            return history, history, session_id
                    
                    def upload_document(file_path: Optional[str]):
                        """上传文档"""
                        if not file_path:
                            return "❌ 请选择文件", get_document_list()
                        
                        try:
                            file_name = Path(file_path).name
                            
                            # 读取文件内容
                            with open(file_path, 'rb') as f:
                                file_content = f.read()
                            
                            # 上传到 RAG 服务
                            result = self.rag_service.add_document(
                                file_name=file_name,
                                file_content=file_content
                            )
                            
                            return f"✅ {result['message']}", get_document_list()
                        except Exception as e:
                            return f"❌ 上传失败: {str(e)}", get_document_list()
                    
                    def get_document_list():
                        """获取文档列表"""
                        try:
                            docs = self.rag_service.list_documents()
                            if not docs:
                                return "暂无文档"
                            
                            doc_info = []
                            for i, doc in enumerate(docs, 1):
                                doc_info.append(
                                    f"{i}. 📄 {doc['filename']}\n"
                                    f"   📊 {doc['chunks']} 个文本块\n"
                                    f"   🕐 {doc['created_at']}"
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
                        [upload_status, doc_list]
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
                
                # ============ 标签页 3: 系统信息 ============
                with gr.Tab("ℹ️ 系统信息"):
                    gr.Markdown(
                        f"""
                        ### 📋 配置信息
                        
                        - **模型名称**: `{config.ollama_model}`
                        - **模型地址**: `{config.ollama_base_url}`
                        - **向量数据库**: `{config.vector_store_type}`
                        - **历史消息数量**: `{config.select_history_length}`
                        - **文本块大小**: `{config.chunk_size}`
                        - **文本块重叠**: `{config.chunk_overlap}`
                        
                        ### 📦 功能特性
                        
                        1. **智能对话**: 基于 Ollama 大语言模型，支持流式响应
                        2. **RAG 文档问答**: 上传文档，进行基于文档内容的智能问答
                        3. **会话管理**: 自动管理对话历史，支持多会话并行
                        4. **向量存储**: 支持 FAISS、ChromaDB 和内存存储
                        
                        ### 🔗 相关链接
                        
                        - [GitHub 仓库](https://github.com/G-LittleSun/RAG-chat)
                        - [API 文档](/docs)
                        - [原 HTML 界面](/chat)
                        
                        ---
                        
                        *Powered by Gradio 4.0+ & LangChain*
                        """
                    )
                    
                    with gr.Row():
                        vector_status_btn = gr.Button("检查向量存储状态 🔍", variant="secondary")
                        vector_status_output = gr.JSON(label="向量存储状态")
                    
                    def check_vector_status():
                        """检查向量存储状态"""
                        try:
                            status = self.rag_service.get_status()
                            return status
                        except Exception as e:
                            return {"error": str(e)}
                    
                    vector_status_btn.click(
                        check_vector_status,
                        None,
                        vector_status_output
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
