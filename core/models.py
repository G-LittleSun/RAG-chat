"""
模型管理模块
封装LangChain和Ollama的交互逻辑
"""
from typing import Generator, List, Dict
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

from .config import config


class ChatModel:
    """
    聊天模型管理类
    职责：专注于与Ollama模型的交互，不管理会话状态
    """
    
    def __init__(self):
        self.llm = Ollama(
            model=config.ollama_model,
            base_url=config.ollama_base_url
        )
        
        # 创建提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", config.system_prompt),
            ("human", "{input}")
        ])
        
        # 构建链
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def generate_response(self, message: str, context: str = None) -> str:
        """
        生成普通响应
        
        Args:
            message: 用户消息
            context: 可选的上下文信息（用于RAG）
            
        Returns:
            生成的响应文本
        """
        try:
            # 如果有上下文，将其添加到消息中
            if context:
                enhanced_message = f"基于以下文档内容回答问题：\n\n{context}\n\n问题：{message}"
            else:
                enhanced_message = message
                
            response = self.chain.invoke({"input": enhanced_message})
            return response
        except Exception as e:
            return f"生成响应时发生错误：{str(e)}"
    
    def generate_stream_response(self, message: str, context: str = None) -> Generator[str, None, None]:
        """
        生成流式响应 -> Generator[str, None, None].优点：用户可以立即看到部分响应，类似 ChatGPT 的打字机效果
        
        Args:
            message: 用户消息
            context: 可选的上下文信息（用于RAG）
            
        Yields:
            响应文本块
        """
        try:
            # 如果有上下文，将其添加到消息中
            if context:
                enhanced_message = f"基于以下文档内容回答问题：\n\n{context}\n\n问题：{message}"
            else:
                enhanced_message = message
                
            for chunk in self.chain.stream({"input": enhanced_message}):
                yield chunk
        except Exception as e:
            yield f"生成响应时发生错误：{str(e)}"
    
    def generate_with_history(self, message: str, history: List[Dict[str, str]]) -> str:
        """
        基于历史记录生成响应
        
        Args:
            message: 用户消息
            history: 历史对话记录
            
        Returns:
            生成的响应文本
        """
        history_length = config.select_history_length
        # 构建包含历史的上下文
        context_parts = []
        for msg in history[-history_length:]:  # 只取最近N条历史
            role = "用户" if msg["role"] == "user" else "助手"
            context_parts.append(f"{role}: {msg['content']}")
        
        if context_parts:
            context = "对话历史：\n" + "\n".join(context_parts) + f"\n\n当前问题：{message}"
        else:
            context = message
            
        return self.generate_response(context)
    
    def generate_stream_with_history(self, message: str, history: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        基于历史记录生成流式响应
        
        Args:
            message: 用户消息
            history: 历史对话记录
            
        Yields:
            响应文本块
        """
        history_length = config.select_history_length

        # 构建包含历史的上下文
        context_parts = []
        for msg in history[-history_length:]:  # 只取最近N条历史
            role = "用户" if msg["role"] == "user" else "助手"
            context_parts.append(f"{role}: {msg['content']}")
        
        if context_parts:
            context = "对话历史：\n" + "\n".join(context_parts) + f"\n\n当前问题：{message}"
        else:
            context = message
            
        yield from self.generate_stream_response(context)


class ChatSession:
    """
    聊天会话管理类
    职责：管理会话状态、历史记录，协调模型调用
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.model = ChatModel()  # 依赖ChatModel进行实际的模型调用
        self.history: List[Dict[str, str]] = []
        
    def add_message(self, role: str, content: str):
        """添加消息到历史记录"""
        self.history.append({
            "role": role, 
            "content": content,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        
        # 限制历史记录长度
        if len(self.history) > config.max_history_length:
            self.history = self.history[-config.max_history_length:]
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取聊天历史"""
        return self.history.copy()  # 返回副本，避免外部修改
    
    def clear_history(self):
        """清空聊天历史"""
        self.history.clear()
    
    def get_history_summary(self) -> str:
        """获取历史记录摘要"""
        if not self.history:
            return "暂无对话历史"
        
        user_messages = len([msg for msg in self.history if msg["role"] == "user"])
        assistant_messages = len([msg for msg in self.history if msg["role"] == "assistant"])
        
        return f"会话包含 {user_messages} 条用户消息和 {assistant_messages} 条助手回复"
    
    def chat(self, message: str) -> str:
        """
        进行对话
        
        Args:
            message: 用户消息
            
        Returns:
            AI响应
        """
        # 添加用户消息到历史
        self.add_message("user", message)
        
        # 使用模型生成响应（考虑历史记录）
        if config.streaming:
            # 如果配置为流式，收集所有块
            response_chunks = []
            for chunk in self.model.generate_stream_with_history(message, self.history[:-1]):
                response_chunks.append(chunk)
            response = "".join(response_chunks)
        else:
            response = self.model.generate_with_history(message, self.history[:-1])
        
        # 添加AI响应到历史
        self.add_message("assistant", response)
        
        return response
    
    def chat_stream(self, message: str) -> Generator[str, None, None]:
        """
        进行流式对话
        
        Args:
            message: 用户消息
            
        Yields:
            AI响应文本块
        """
        # 添加用户消息到历史
        self.add_message("user", message)
        
        # 生成并收集AI响应
        response_chunks = []
        try:
            for chunk in self.model.generate_stream_response(message):
                response_chunks.append(chunk)
                yield chunk
        except Exception as e:
            error_msg = f"生成响应时发生错误: {str(e)}"
            yield error_msg
            response_chunks.append(error_msg)
        
        # 添加完整响应到历史
        full_response = "".join(response_chunks)
        self.add_message("assistant", full_response)
    
    def chat_with_context(self, message: str, context: str) -> str:
        """
        基于上下文进行对话（用于RAG）
        
        Args:
            message: 用户消息
            context: 检索到的文档上下文
            
        Returns:
            AI响应
        """
        # 添加用户消息到历史
        self.add_message("user", message)
        
        # 使用模型生成基于上下文的响应
        response = self.model.generate_response(message, context)
        
        # 添加AI响应到历史
        self.add_message("assistant", response)
        
        return response
    
    def chat_stream_with_context(self, message: str, context: str) -> Generator[str, None, None]:
        """
        基于上下文进行流式对话（用于RAG）
        
        Args:
            message: 用户消息
            context: 检索到的文档上下文
            
        Yields:
            AI响应文本块
        """
        # 添加用户消息到历史
        self.add_message("user", message)
        
        # 生成并收集AI响应
        response_chunks = []
        try:
            for chunk in self.model.generate_stream_response(message, context):
                response_chunks.append(chunk)
                yield chunk
        except Exception as e:
            error_msg = f"生成响应时发生错误: {str(e)}"
            yield error_msg
            response_chunks.append(error_msg)
        
        # 添加完整响应到历史
        full_response = "".join(response_chunks)
        self.add_message("assistant", full_response)


class OllamaModelManager:
    """
    Ollama模型管理器
    职责：管理多个模型实例，提供模型切换等高级功能
    """
    
    def __init__(self):
        self.models: Dict[str, ChatModel] = {}
        self.current_model = config.ollama_model
        
    def get_model(self, model_name: str = None) -> ChatModel:
        """
        获取指定模型实例
        
        Args:
            model_name: 模型名称，如果为None则使用当前模型
            
        Returns:
            ChatModel实例
        """
        model_name = model_name or self.current_model
        
        if model_name not in self.models:
            # 临时创建新模型实例
            # 注意：这里需要动态创建配置，因为每个模型可能有不同配置
            self.models[model_name] = ChatModel()
            
        return self.models[model_name]
    
    def switch_model(self, model_name: str):
        """
        切换当前使用的模型
        
        Args:
            model_name: 要切换到的模型名称
        """
        self.current_model = model_name
        
    def list_available_models(self) -> List[str]:
        """
        列出可用的模型
        
        Returns:
            可用模型名称列表
        """
        # 这里可以调用Ollama API获取可用模型列表
        # 暂时返回常用模型
        return ["deepseek-r1:1.5b", "llama2", "codellama", "mistral"]
    
    def get_model_info(self, model_name: str = None) -> Dict[str, str]:
        """
        获取模型信息
        
        Args:
            model_name: 模型名称，如果为None则使用当前模型
            
        Returns:
            模型信息字典
        """
        model_name = model_name or self.current_model
        return {
            "name": model_name,
            "status": "loaded" if model_name in self.models else "not_loaded",
            "current": model_name == self.current_model
        }
    
    def clear_model_cache(self, model_name: str = None):
        """
        清除模型缓存
        
        Args:
            model_name: 要清除的模型名称，如果为None则清除所有
        """
        if model_name:
            if model_name in self.models:
                del self.models[model_name]
        else:
            self.models.clear()