# -*- coding: utf-8 -*-
"""
MarketScope - 搜索服务模块

职责：
1. 提供统一的行业搜索接口
2. 支持 Tavily 和其他搜索引擎
3. 搜索结果缓存和格式化
4. 多维度行业分析搜索
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from itertools import cycle
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from config import Config

logger = logging.getLogger(__name__)

# Transient network errors (retryable)
_SEARCH_TRANSIENT_EXCEPTIONS = (
    requests.exceptions.SSLError,
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(_SEARCH_TRANSIENT_EXCEPTIONS),
    # 简化日志，不使用 before_sleep=before_sleep_log(logger, logging.WARNING)
)
def _post_with_retry(url: str, *, headers: Dict[str, str], json: Dict[str, Any], timeout: int) -> requests.Response:
    """POST with retry on transient SSL/network errors."""
    return requests.post(url, headers=headers, json=json, timeout=timeout)


@dataclass
class SearchResult:
    """搜索结果数据类"""
    title: str
    snippet: str  # 摘要
    url: str
    source: str  # 来源网站
    published_date: Optional[str] = None
    
    def to_text(self) -> str:
        """转换为文本格式"""
        date_str = f" ({self.published_date})" if self.published_date else ""
        return f"【{self.source}】{self.title}{date_str}\n{self.snippet}"


@dataclass 
class SearchResponse:
    """搜索响应"""
    query: str
    results: List[SearchResult]
    provider: str  # 使用的搜索引擎
    success: bool = True
    error_message: Optional[str] = None
    search_time: float = 0.0  # 搜索耗时（秒）
    
    def to_context(self, max_results: int = 5) -> str:
        """将搜索结果转换为可用于 AI 分析的上下文"""
        if not self.success or not self.results:
            return f"搜索 '{self.query}' 未找到相关结果。"
        
        lines = [f"【{self.query} 搜索结果】（来源：{self.provider}）"]
        for i, result in enumerate(self.results[:max_results], 1):
            lines.append(f"\n{i}. {result.to_text()}")
        
        return "\n".join(lines)


class BaseSearchProvider(ABC):
    """搜索引擎基类"""
    
    def __init__(self, api_keys: List[str], name: str):
        """
        初始化搜索引擎
        
        Args:
            api_keys: API Key 列表（支持多个 key 负载均衡）
            name: 搜索引擎名称
        """
        self._api_keys = api_keys
        self._name = name
        self._key_cycle = cycle(api_keys) if api_keys else None
        self._key_usage: Dict[str, int] = {key: 0 for key in api_keys}
        self._key_errors: Dict[str, int] = {key: 0 for key in api_keys}
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def is_available(self) -> bool:
        """检查是否有可用的 API Key"""
        return bool(self._api_keys)
    
    def _get_next_key(self) -> Optional[str]:
        """
        获取下一个可用的 API Key（负载均衡）
        
        策略：轮询 + 跳过错误过多的 key
        """
        if not self._key_cycle:
            return None
        
        # 最多尝试所有 key
        for _ in range(len(self._api_keys)):
            key = next(self._key_cycle)
            # 跳过错误次数过多的 key（超过 3 次）
            if self._key_errors.get(key, 0) < 3:
                return key
        
        # 所有 key 都有问题，重置错误计数并返回第一个
        logger.warning(f"[{self._name}] 所有 API Key 都有错误记录，重置错误计数")
        self._key_errors = {key: 0 for key in self._api_keys}
        return self._api_keys[0] if self._api_keys else None
    
    def _record_success(self, key: str) -> None:
        """记录成功使用"""
        self._key_usage[key] = self._key_usage.get(key, 0) + 1
        # 成功后减少错误计数
        if key in self._key_errors and self._key_errors[key] > 0:
            self._key_errors[key] -= 1
    
    def _record_error(self, key: str) -> None:
        """记录错误"""
        self._key_errors[key] = self._key_errors.get(key, 0) + 1
        logger.warning(f"[{self._name}] API Key {key[:8]}... 错误计数: {self._key_errors[key]}")
    
    @abstractmethod
    def _do_search(self, query: str, api_key: str, max_results: int, days: int = 7) -> SearchResponse:
        """执行搜索（子类实现）"""
        pass
    
    def search(self, query: str, max_results: int = 5, days: int = 7) -> SearchResponse:
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            max_results: 最大返回结果数
            days: 搜索最近几天的时间范围（默认7天）
            
        Returns:
            SearchResponse 对象
        """
        api_key = self._get_next_key()
        if not api_key:
            return SearchResponse(
                query=query,
                results=[],
                provider=self._name,
                success=False,
                error_message=f"{self._name} 未配置 API Key"
            )
        
        start_time = time.time()
        try:
            response = self._do_search(query, api_key, max_results, days=days)
            response.search_time = time.time() - start_time
            
            if response.success:
                self._record_success(api_key)
                logger.info(f"[{self._name}] 搜索 '{query}' 成功，返回 {len(response.results)} 条结果，耗时 {response.search_time:.2f}s")
            else:
                self._record_error(api_key)
            
            return response
            
        except Exception as e:
            self._record_error(api_key)
            elapsed = time.time() - start_time
            logger.error(f"[{self._name}] 搜索 '{query}' 失败: {e}")
            return SearchResponse(
                query=query,
                results=[],
                provider=self._name,
                success=False,
                error_message=str(e),
                search_time=elapsed
            )


class TavilySearchProvider(BaseSearchProvider):
    """
    Tavily 搜索引擎
    
    特点：
    - 专为 AI/LLM 优化的搜索 API
    - 免费版每月 1000 次请求
    - 返回结构化的搜索结果
    
    文档：https://docs.tavily.com/
    """
    
    def __init__(self, api_keys: List[str]):
        super().__init__(api_keys, "Tavily")
    
    def _do_search(self, query: str, api_key: str, max_results: int, days: int = 7) -> SearchResponse:
        """执行 Tavily 搜索"""
        try:
            from tavily import TavilyClient
        except ImportError:
            return SearchResponse(
                query=query,
                results=[],
                provider=self.name,
                success=False,
                error_message="tavily-python 未安装，请运行: pip install tavily-python"
            )
        
        try:
            client = TavilyClient(api_key=api_key)
            
            # 执行搜索（优化：使用advanced深度、限制最近几天）
            response = client.search(
                query=query,
                search_depth="advanced",  # advanced 获取更多结果
                max_results=max_results,
                include_answer=False,
                include_raw_content=False,
                days=days,  # 搜索最近天数的内容
            )
            
            # 记录原始响应到日志
            logger.info(f"[Tavily] 搜索完成，query='{query}', 返回 {len(response.get('results', []))} 条结果")
            
            # 解析结果
            results = []
            for item in response.get('results', []):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    snippet=item.get('content', '')[:500],  # 截取前500字
                    url=item.get('url', ''),
                    source=self._extract_domain(item.get('url', '')),
                    published_date=item.get('published_date'),
                ))
            
            return SearchResponse(
                query=query,
                results=results,
                provider=self.name,
                success=True,
            )
            
        except Exception as e:
            error_msg = str(e)
            # 检查是否是配额问题
            if 'rate limit' in error_msg.lower() or 'quota' in error_msg.lower():
                error_msg = f"API 配额已用尽: {error_msg}"
            
            return SearchResponse(
                query=query,
                results=[],
                provider=self.name,
                success=False,
                error_message=error_msg
            )
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """从 URL 提取域名作为来源"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain or '未知来源'
        except Exception:
            return '未知来源'


class SearchService:
    """
    搜索服务
    
    功能：
    1. 管理多个搜索引擎
    2. 自动故障转移
    3. 结果聚合和格式化
    4. 行业分析专用搜索
    """
    
    def __init__(
        self,
        tavily_keys: Optional[List[str]] = None,
        news_max_age_days: int = 7,
    ):
        """
        初始化搜索服务

        Args:
            tavily_keys: Tavily API Key 列表
            news_max_age_days: 搜索最大时效（天）
        """
        self._providers = []
        self.news_max_age_days = max(1, news_max_age_days)

        # 初始化搜索引擎（按优先级排序）
        # 1. Tavily（免费额度更多，每月 1000 次）
        if tavily_keys:
            self._providers.append(TavilySearchProvider(tavily_keys))
            logger.info(f"已配置 Tavily 搜索，共 {len(tavily_keys)} 个 API Key")
        elif Config.TAVILY_API_KEY:  # 默认使用配置中的API Key
            self._providers.append(TavilySearchProvider([Config.TAVILY_API_KEY]))
            logger.info("已配置 Tavily 搜索（使用配置中的API Key）")

        if not self._providers:
            logger.warning("未配置任何搜索引擎 API Key，搜索功能将不可用")

        # In-memory search result cache: {cache_key: (timestamp, SearchResponse)}
        self._cache: Dict[str, Tuple[float, 'SearchResponse']] = {}
        # Default cache TTL in seconds (10 minutes)
        self._cache_ttl: int = 600

    @property
    def is_available(self) -> bool:
        """检查是否有可用的搜索引擎"""
        return any(p.is_available for p in self._providers)

    def _cache_key(self, query: str, max_results: int, days: int) -> str:
        """Build a cache key from query parameters."""
        return f"{query}|{max_results}|{days}"

    def _get_cached(self, key: str) -> Optional['SearchResponse']:
        """Return cached SearchResponse if still valid, else None."""
        entry = self._cache.get(key)
        if entry is None:
            return None
        ts, response = entry
        if time.time() - ts > self._cache_ttl:
            del self._cache[key]
            return None
        logger.debug(f"Search cache hit: {key[:60]}...")
        return response

    def _put_cache(self, key: str, response: 'SearchResponse') -> None:
        """Store a successful SearchResponse in cache."""
        # Hard cap: evict oldest entries when cache exceeds limit
        _MAX_CACHE_SIZE = 500
        if len(self._cache) >= _MAX_CACHE_SIZE:
            now = time.time()
            # First pass: remove expired entries
            expired = [k for k, (ts, _) in self._cache.items() if now - ts > self._cache_ttl]
            for k in expired:
                del self._cache[k]
            # Second pass: if still over limit, evict oldest entries (FIFO)
            if len(self._cache) >= _MAX_CACHE_SIZE:
                excess = len(self._cache) - _MAX_CACHE_SIZE + 1
                oldest = sorted(self._cache.keys(), key=lambda k: self._cache[k][0])[:excess]
                for k in oldest:
                    del self._cache[k]
        self._cache[key] = (time.time(), response)

    def search(
        self,
        query: str,
        max_results: int = 5,
        days: int = None
    ) -> SearchResponse:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            days: 搜索时间范围（天）
            
        Returns:
            SearchResponse 对象
        """
        if days is None:
            days = self.news_max_age_days
            
        # Check cache first
        cache_key = self._cache_key(query, max_results, days)
        cached = self._get_cached(cache_key)
        if cached is not None:
            logger.info(f"使用缓存搜索结果: {query}")
            return cached

        # 依次尝试各个搜索引擎
        for provider in self._providers:
            if not provider.is_available:
                continue
            
            response = provider.search(query, max_results, days=days)
            
            if response.success and response.results:
                logger.info(f"使用 {provider.name} 搜索成功")
                self._put_cache(cache_key, response)
                return response
            else:
                logger.warning(f"{provider.name} 搜索失败: {response.error_message}，尝试下一个引擎")
        
        # 所有引擎都失败
        return SearchResponse(
            query=query,
            results=[],
            provider="None",
            success=False,
            error_message="所有搜索引擎都不可用或搜索失败"
        )

    def search_market_size(self, industry: str) -> SearchResponse:
        """搜索市场规模数据"""
        query = f"{industry} 市场规模 市场数据 用户数量 增长率 行业报告"
        return self.search(query)

    def search_competitors(self, app_type: str) -> SearchResponse:
        """搜索竞争对手信息"""
        query = f"{app_type} 主要竞争对手 竞品分析 市场份额 产品对比"
        return self.search(query)

    def search_trends(self, industry: str) -> SearchResponse:
        """搜索行业趋势"""
        query = f"{industry} 行业趋势 发展方向 技术趋势 未来预测 政策影响"
        return self.search(query)

    def analyze_user_demand(self, app_type: str) -> SearchResponse:
        """分析用户需求"""
        query = f"{app_type} 用户痛点 需求变化 用户行为 满意度 反馈"
        return self.search(query)

    def search_comprehensive_intel(
        self,
        app_type: str,
        industry: str,
        max_searches: int = 5
    ) -> Dict[str, SearchResponse]:
        """
        多维度情报搜索（同时使用多个引擎、多个维度）
        
        搜索维度：
        1. 市场规模 - 市场数据和增长
        2. 竞争格局 - 竞争对手信息
        3. 发展趋势 - 技术和政策趋势
        4. 用户需求 - 用户行为和痛点
        5. 进入机会 - 市场机会和壁垒
        
        Args:
            app_type: APP类型
            industry: 行业
            max_searches: 最大搜索次数
            
        Returns:
            {维度名称: SearchResponse} 字典
        """
        results = {}
        search_count = 0

        search_dimensions = [
            {'name': 'market_size', 'query': f"{industry} 市场规模 增长率 用户基数 行业报告", 'desc': '市场规模'},
            {'name': 'competitors', 'query': f"{app_type} 竞争对手 竞品分析 市场份额 功能对比", 'desc': '竞争格局'},
            {'name': 'trends', 'query': f"{industry} 发展趋势 技术趋势 未来预测 政策影响", 'desc': '发展趋势'},
            {'name': 'user_demand', 'query': f"{app_type} 用户痛点 需求变化 用户行为 满意度", 'desc': '用户需求'},
            {'name': 'entry_opportunities', 'query': f"{industry} 市场进入机会 进入壁垒 差异化策略 风险因素", 'desc': '进入机会'},
        ]
        
        logger.info(f"开始多维度情报搜索: {app_type} ({industry})")
        
        # 轮流使用不同的搜索引擎
        provider_index = 0
        
        for dim in search_dimensions:
            if search_count >= max_searches:
                break
            
            # 选择搜索引擎（轮流使用）
            available_providers = [p for p in self._providers if p.is_available]
            if not available_providers:
                break
            
            provider = available_providers[provider_index % len(available_providers)]
            provider_index += 1
            
            logger.info(f"[情报搜索] {dim['desc']}: 使用 {provider.name}")
            
            response = provider.search(dim['query'], max_results=3, days=self.news_max_age_days)
            results[dim['name']] = response
            search_count += 1
            
            if response.success:
                logger.info(f"[情报搜索] {dim['desc']}: 获取 {len(response.results)} 条结果")
            else:
                logger.warning(f"[情报搜索] {dim['desc']}: 搜索失败 - {response.error_message}")
            
            # 短暂延迟避免请求过快
            time.sleep(0.5)
        
        return results

    def format_intel_report(self, intel_results: Dict[str, SearchResponse], app_type: str) -> str:
        """
        格式化情报搜索结果为报告
        
        Args:
            intel_results: 多维度搜索结果
            app_type: APP类型
            
        Returns:
            格式化的情报报告文本
        """
        lines = [f"【{app_type} 情报搜索结果】"]
        
        # 维度展示顺序
        display_order = ['market_size', 'competitors', 'trends', 'user_demand', 'entry_opportunities']
        
        for dim_name in display_order:
            if dim_name not in intel_results:
                continue
                
            resp = intel_results[dim_name]
            
            # 获取维度描述
            dim_desc = dim_name
            if dim_name == 'market_size': dim_desc = '📊 市场规模'
            elif dim_name == 'competitors': dim_desc = '⚔️ 竞争格局'
            elif dim_name == 'trends': dim_desc = '📈 发展趋势'
            elif dim_name == 'user_demand': dim_desc = '👥 用户需求'
            elif dim_name == 'entry_opportunities': dim_desc = '🚀 进入机会'
            
            lines.append(f"\n{dim_desc} (来源: {resp.provider}):")
            if resp.success and resp.results:
                # 增加显示条数
                for i, r in enumerate(resp.results[:4], 1):
                    date_str = f" [{r.published_date}]" if r.published_date else ""
                    lines.append(f"  {i}. {r.title}{date_str}")
                    # 如果摘要太短，可能信息量不足
                    snippet = r.snippet[:150] if len(r.snippet) > 20 else r.snippet
                    lines.append(f"     {snippet}...")
            else:
                lines.append("  未找到相关信息")
        
        return "\n".join(lines)


# === 便捷函数 ===
_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """获取搜索服务单例"""
    global _search_service
    
    if _search_service is None:
        _search_service = SearchService(
            tavily_keys=[Config.TAVILY_API_KEY] if Config.TAVILY_API_KEY else None,
            news_max_age_days=Config.NEWS_MAX_AGE_DAYS,
        )
    
    return _search_service


def reset_search_service() -> None:
    """重置搜索服务（用于测试）"""
    global _search_service
    _search_service = None


if __name__ == "__main__":
    # 测试搜索服务
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
    )
    
    # 手动测试（需要配置 API Key）
    service = get_search_service()
    
    if service.is_available:
        print("=== 测试行业新闻搜索 ===")
        response = service.search_market_size("社交媒体")
        print(f"搜索状态: {'成功' if response.success else '失败'}")
        print(f"搜索引擎: {response.provider}")
        print(f"结果数量: {len(response.results)}")
        print(f"耗时: {response.search_time:.2f}s")
        print("\n" + response.to_context())
    else:
        print("未配置搜索引擎 API Key，跳过测试")