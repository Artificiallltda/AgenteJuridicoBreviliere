"""
Agent Router — Sistema de Roteamento Inteligente entre Agentes

Este módulo gerencia o roteamento de mensagens e comandos para os agentes
especializados da Squad Jurídico Breviliere.

Responsabilidades:
1. Identificar o agente mais adequado para cada mensagem
2. Gerenciar handoffs entre agentes
3. Manter contexto durante transições
4. Aplicar regras de roteamento baseadas em palavras-chave
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class AgentCategory(Enum):
    FRONTLINE = "frontline"
    BACKOFFICE = "backoffice"
    CONTENT = "content"
    TECHNICAL = "technical"
    MANAGEMENT = "management"


@dataclass
class AgentConfig:
    """Configuração de um agente especializado."""
    id: str
    name: str
    role: str
    slashPrefix: str
    activation: List[str]
    category: AgentCategory
    priority: int
    description: str
    canHandle: List[str]
    handoffTo: List[str]


@dataclass
class RoutingResult:
    """Resultado do roteamento."""
    agent: AgentConfig
    confidence: float  # 0.0 a 1.0
    matchedKeyword: Optional[str]
    suggestedHandoff: Optional[List[str]]


class AgentRouter:
    """
    Sistema de roteamento inteligente entre agentes.
    
    Usa combinação de:
    1. Palavras-chave explícitas
    2. Menções de agente (@nome)
    3. Comandos com prefixo (*nome)
    4. Análise semântica básica do contexto
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.agents: Dict[str, AgentConfig] = {}
        self.keywords: Dict[str, List[str]] = {}
        self.default_agent: str = "minato"
        
        if config_path:
            self.load_config(config_path)
        else:
            self._load_default_config()
    
    def _load_default_config(self):
        """Carrega configuração padrão dos agentes."""
        self.agents = {
            "minato": AgentConfig(
                id="minato",
                name="Minato",
                role="Atendimento e Triagem de Clientes",
                slashPrefix="minato",
                activation=["@minato", "*minato", "/minato"],
                category=AgentCategory.FRONTLINE,
                priority=1,
                description="Primeiro ponto de contato com clientes e leads.",
                canHandle=["novo cliente", "triagem", "agendamento", "dúvida de cliente"],
                handoffTo=["kakashi", "sakura"]
            ),
            "copywriter": AgentConfig(
                id="copywriter",
                name="Copywriter",
                role="Tom de Voz e Copywriting Estratégico",
                slashPrefix="copy",
                activation=["@copy", "*copy", "/copy", "@copywriter"],
                category=AgentCategory.FRONTLINE,
                priority=2,
                description="Guardião do tom de voz da Brev.",
                canHandle=["revisão de tom", "copywriting", "persuasão", "metáforas"],
                handoffTo=["ero-sennin"]
            ),
            "kakashi": AgentConfig(
                id="kakashi",
                name="Kakashi",
                role="Estrategista de Bastidores",
                slashPrefix="kakashi",
                activation=["@kakashi", "*kakashi", "/kakashi"],
                category=AgentCategory.BACKOFFICE,
                priority=3,
                description="Estratégia pura. Advogado do diabo.",
                canHandle=["estratégia", "análise de cenário", "parcerias", "prepara para sakura"],
                handoffTo=["sakura"]
            ),
            "tsunade": AgentConfig(
                id="tsunade",
                name="Tsunade",
                role="Inteligência de Mercado e Conversão",
                slashPrefix="tsunade",
                activation=["@tsunade", "*tsunade", "/tsunade", "@hokage"],
                category=AgentCategory.BACKOFFICE,
                priority=4,
                description="Relatórios de inteligência.",
                canHandle=["relatório semanal", "inteligência", "jurisprudência", "concorrentes"],
                handoffTo=["ero-sennin"]
            ),
            "kabuto": AgentConfig(
                id="kabuto",
                name="Kabuto",
                role="Análise de Dados Processuais",
                slashPrefix="kabuto",
                activation=["@kabuto", "*kabuto", "/kabuto"],
                category=AgentCategory.BACKOFFICE,
                priority=5,
                description="Varredura de e-mails judiciais.",
                canHandle=["diagnóstico de canais", "prazos críticos", "certidões"],
                handoffTo=[]
            ),
            "ero-sennin": AgentConfig(
                id="ero-sennin",
                name="Ero Sennin",
                role="Conteúdo para Redes Sociais",
                slashPrefix="ero",
                activation=["@ero", "*ero", "/ero", "@ero-sennin"],
                category=AgentCategory.CONTENT,
                priority=6,
                description="Copywriting para redes sociais.",
                canHandle=["post", "roteiro de vídeo", "artigo", "conteúdo educativo"],
                handoffTo=["sai"]
            ),
            "sai": AgentConfig(
                id="sai",
                name="Sai",
                role="Geração de Imagens",
                slashPrefix="sai",
                activation=["@sai", "*sai", "/sai"],
                category=AgentCategory.CONTENT,
                priority=7,
                description="Direção de arte visual.",
                canHandle=["gerar imagem", "direção de arte", "prompt visual"],
                handoffTo=[]
            ),
            "sakura": AgentConfig(
                id="sakura",
                name="Sakura",
                role="Peças Processuais",
                slashPrefix="sakura",
                activation=["@sakura", "*sakura", "/sakura"],
                category=AgentCategory.TECHNICAL,
                priority=8,
                description="Redação de peças processuais.",
                canHandle=["petição", "contestação", "recurso", "peça processual"],
                handoffTo=[]
            ),
            "dev": AgentConfig(
                id="dev",
                name="Dev",
                role="Desenvolvedor Python Sênior",
                slashPrefix="dev",
                activation=["@dev", "*dev", "/dev"],
                category=AgentCategory.TECHNICAL,
                priority=9,
                description="Implementação de features e correção de bugs.",
                canHandle=["implementar", "bug", "teste", "code review"],
                handoffTo=["qa"]
            ),
            "qa": AgentConfig(
                id="qa",
                name="QA",
                role="Especialista de QA",
                slashPrefix="qa",
                activation=["@qa", "*qa", "/qa"],
                category=AgentCategory.TECHNICAL,
                priority=10,
                description="Testes unitários e de integração.",
                canHandle=["criar testes", "cobertura", "validação"],
                handoffTo=[]
            ),
            "pm": AgentConfig(
                id="pm",
                name="PM",
                role="Product Manager",
                slashPrefix="pm",
                activation=["@pm", "*pm", "/pm"],
                category=AgentCategory.MANAGEMENT,
                priority=11,
                description="Gestão de produto e backlog.",
                canHandle=["backlog", "priorização", "roadmap", "épicos"],
                handoffTo=[]
            )
        }
        
        # Mapeamento de palavras-chave por agente
        self.keywords = {
            "minato": ["cliente", "lead", "agendar", "consulta", "honorários", "responder", "triagem"],
            "copywriter": ["tom de voz", "revisar", "persuasão", "copy", "metáfora", "texto"],
            "kakashi": ["estratégia", "analisar", "parceria", "negociação", "decisão", "prepara para sakura"],
            "tsunade": ["relatório", "inteligência", "jurisprudência", "concorrentes", "oportunidade", "hokage"],
            "kabuto": ["prazo", "e-mail", "certidão", "honorários", "diagnóstico", "canais"],
            "ero-sennin": ["post", "instagram", "vídeo", "roteiro", "conteúdo", "redes sociais"],
            "sai": ["imagem", "visual", "gerar", "foto", "arte", "prompt visual"],
            "sakura": ["peça", "petição", "contestação", "recurso", "processual", "memorial"],
            "dev": ["implementar", "bug", "feature", "código", "teste", "python"],
            "qa": ["teste", "cobertura", "validar", "pytest"],
            "pm": ["backlog", "priorizar", "roadmap", "épico", "story", "produto"]
        }
    
    def load_config(self, config_path: str):
        """Carrega configuração de arquivo YAML."""
        import yaml
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Parse agents from config
        for agent_data in config.get('squad', {}).get('agents', []):
            category = AgentCategory(agent_data.get('category', 'frontline'))
            agent = AgentConfig(
                id=agent_data['id'],
                name=agent_data['name'],
                role=agent_data['role'],
                slashPrefix=agent_data['slashPrefix'],
                activation=agent_data.get('activation', []),
                category=category,
                priority=agent_data.get('priority', 99),
                description=agent_data.get('description', ''),
                canHandle=agent_data.get('canHandle', []),
                handoffTo=agent_data.get('handoffTo', [])
            )
            self.agents[agent.id] = agent
        
        # Parse keywords
        routing_config = config.get('routing', {})
        self.keywords = routing_config.get('keywords', {})
        self.default_agent = routing_config.get('default', 'minato')
    
    def route(self, message: str, context: Optional[Dict] = None) -> RoutingResult:
        """
        Roteia uma mensagem para o agente mais adequado.
        
        Args:
            message: Mensagem do usuário
            context: Contexto opcional (histórico, estado atual, etc.)
        
        Returns:
            RoutingResult com agente selecionado e metadados
        """
        message_lower = message.lower()
        
        # 1. Verificar menção explícita de agente (@nome ou *nome)
        explicit_agent = self._check_explicit_mention(message_lower)
        if explicit_agent:
            return RoutingResult(
                agent=self.agents[explicit_agent],
                confidence=1.0,
                matchedKeyword="menção explícita",
                suggestedHandoff=self.agents[explicit_agent].handoffTo
            )
        
        # 2. Verificar palavras-chave
        best_match = self._check_keywords(message_lower)
        if best_match:
            agent_id, keyword, confidence = best_match
            return RoutingResult(
                agent=self.agents[agent_id],
                confidence=confidence,
                matchedKeyword=keyword,
                suggestedHandoff=self.agents[agent_id].handoffTo
            )
        
        # 3. Fallback para agente padrão
        return RoutingResult(
            agent=self.agents[self.default_agent],
            confidence=0.3,
            matchedKeyword=None,
            suggestedHandoff=self.agents[self.default_agent].handoffTo
        )
    
    def _check_explicit_mention(self, message: str) -> Optional[str]:
        """Verifica se há menção explícita de agente."""
        # Padrão: @nome ou *nome ou /nome
        patterns = [
            r'@(\w+)',
            r'\*(\w+)',
            r'/(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                mentioned = match.group(1)
                # Verificar se o nome mencionado corresponde a um agente
                for agent_id, agent in self.agents.items():
                    if mentioned == agent_id or mentioned == agent.slashPrefix:
                        return agent_id
        
        return None
    
    def _check_keywords(self, message: str) -> Optional[Tuple[str, str, float]]:
        """
        Verifica palavras-chave na mensagem.
        
        Returns:
            Tuple (agent_id, keyword, confidence) ou None
        """
        matches = []
        
        for agent_id, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in message:
                    # Calcular confiança baseada no tamanho da keyword
                    # Keywords mais longas = mais específicas = mais confiança
                    confidence = min(0.5 + (len(keyword) / 50), 0.9)
                    matches.append((agent_id, keyword, confidence))
        
        if not matches:
            return None
        
        # Retornar o match com maior confiança
        return max(matches, key=lambda x: x[2])
    
    def get_agent(self, agent_id: str) -> Optional[AgentConfig]:
        """Obtém configuração de um agente específico."""
        return self.agents.get(agent_id)
    
    def list_agents(self, category: Optional[AgentCategory] = None) -> List[AgentConfig]:
        """Lista todos os agentes, opcionalmente filtrados por categoria."""
        if category:
            return [a for a in self.agents.values() if a.category == category]
        return list(self.agents.values())
    
    def suggest_handoff(self, from_agent: str, context: Optional[Dict] = None) -> List[str]:
        """Sugere agentes para handoff baseado no agente atual."""
        agent = self.agents.get(from_agent)
        if not agent:
            return []
        return agent.handoffTo
    
    def get_workflow(self, workflow_name: str) -> Optional[List[Dict]]:
        """
        Obtém definição de um workflow.
        
        Workflows predefinidos:
        - novo-cliente-peca
        - inteligencia-conteudo
        - atendimento-estrategia-peca
        """
        workflows = {
            "novo-cliente-peca": [
                {"agent": "minato", "action": "triagem e qualificação"},
                {"agent": "kakashi", "action": "estratégia e tese (gatilho sakura)"},
                {"agent": "sakura", "action": "redação da peça"}
            ],
            "inteligencia-conteudo": [
                {"agent": "tsunade", "action": "relatório de inteligência"},
                {"agent": "ero-sennin", "action": "criação de conteúdo"},
                {"agent": "sai", "action": "geração de imagens"}
            ],
            "atendimento-estrategia-peca": [
                {"agent": "minato", "action": "atendimento inicial"},
                {"agent": "kakashi", "action": "análise estratégica"},
                {"agent": "sakura", "action": "peça processual"}
            ]
        }
        return workflows.get(workflow_name)


# Singleton global
_router_instance: Optional[AgentRouter] = None


def get_router(config_path: Optional[str] = None) -> AgentRouter:
    """Obtém instância singleton do router."""
    global _router_instance
    if _router_instance is None:
        _router_instance = AgentRouter(config_path)
    return _router_instance
