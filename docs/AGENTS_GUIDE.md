# Guia de Agentes — Squad Jurídico Breviliere

**Versão:** 2.0 | **Data:** 29/03/2026

---

## 📋 Visão Geral

A Squad Jurídico Breviliere é composta por **11 agentes especializados**, organizados em 5 categorias:

| Categoria | Agentes | Função |
|---|---|---|
| **Frontline** | @minato, @copywriter | Atendimento direto e comunicação |
| **Backoffice** | @kakashi, @tsunade, @kabuto | Estratégia e inteligência |
| **Content** | @ero-sennin, @sai | Criação de conteúdo e visuais |
| **Technical** | @sakura, @dev, @qa | Peças processuais e desenvolvimento |
| **Management** | @pm | Gestão de produto |

---

## 🎯 Agentes Detalhados

### 1. @minato — Atendimento e Triagem

**Quando usar:**
- Novo cliente entrando em contato
- Triagem de demanda jurídica
- Agendamento de consultas
- Responder dúvidas de clientes
- Atualização de status para clientes
- Comunicação formal (ofícios, e-mails)

**Comandos:**
```
@minato *responder-cliente {mensagem}
@minato *triagem {caso}
@minato *atualizar-status {cliente}
@minato *redigir-formal {tipo}
@minato *qualificar-lead {mensagem}
```

**Exemplo de uso:**
```
Kage: "@minato, novo cliente mandou: 'Fui demitido sem justa causa após 15 anos. 
Tenho direito a quê?'"

Minato: [Resposta Pura para o cliente]
"Olá! Entendo sua situação. A demissão sem justa causa gera direitos como multa 
do FGTS, saque do FGTS, seguro-desemprego e verbas rescisórias.

Para eu te orientar melhor, você poderia me contar:
- Qual era seu salário bruto?
- Você tem anotações da sua rescisão?

Com essas informações, consigo te explicar melhor seus direitos. Podemos agendar 
uma consulta estratégica por R$ 162,00?"

[META-DADO]
Cenário: A - Novo Cliente
Resumo do Cliente: Demitido sem justa causa após 15 anos, busca orientação sobre direitos.
Ação Tomada: Aplicou Regra do Cofre Fechado (informou existência de direitos, reteve detalhes).
Alerta de Complexidade: BAIXA (caso trabalhista padrão).
Pendência: Aguardando confirmação de agendamento.
```

---

### 2. @copywriter — Tom de Voz e Copywriting

**Quando usar:**
- Revisar tom de mensagens e prompts
- Aplicar técnicas de persuasão
- Criar metáforas jurídicas
- Validar templates de comunicação
- Garantir conformidade com estilo "Clark Kent"

**Comandos:**
```
@copy *review-prompts
@copy *rewrite {arquivo}
@copy *tone-check {mensagem}
@copy *create-template {situação}
@copy *apply-persuasion {texto}
@copy *add-metaphor {tema}
```

**Exemplo de uso:**
```
Kage: "@copy, aplica persuasão nesse texto: 'Contrate nossos serviços para 
regularizar seu imóvel.'"

Copywriter: "Aqui está a versão com gatilhos de Cialdini:

'Já ajudamos +500 famílias a regularizarem seus imóveis em Francisco Morato e 
região. Assim como o Sr. João, que após 20 anos sem escritura, hoje tem seu 
apartamento 100% regularizado.

Agende uma análise gratuita do seu caso e descubra como a usucapião pode ser 
a solução para você também.'

Gatilhos aplicados:
- Prova Social (+500 famílias)
- História de sucesso (Sr. João)
- Autoridade (especialistas na região)
- CTA claro (agende análise)"
```

---

### 3. @kakashi — Estratégia de Bastidores

**Quando usar:**
- Analisar parcerias e negociações
- Decisões políticas do escritório
- Reconstruir teses jurídicas
- Preparar briefing para peças processuais
- Advogado do diabo em ideias

**Comandos:**
```
@kakashi *analisar-estrategia {cenário}
@kakashi *debater-ideia {proposta}
@kakashi *reconstruir-tese {tese}
@kakashi *prepara-para-sakura {caso}
@kakashi *leitura-intencao {mensagem}
```

**Exemplo de uso:**
```
Kage: "@kakashi, penso em fazer parceria com escritório de contabilidade para 
indicar clientes de inventário. O que acha?"

Kakashi: "Parceria com contabilidade é faca de dois gumes.

**Riscos:**
- Contador pode indicar 3 escritórios, não só você
- Você vira commodity na pilha de indicações
- Perde controle do funnel de vendas

**Oportunidade:**
- Se for exclusividade mútua, pode ser mina de ouro
- Contador vê o cliente primeiro (antes do advogado)
- Inventário tem sinergia natural com contabilidade

**Pergunta:** O contador já indicou clientes pra você antes? Qual taxa de 
conversão?

**Ação:** Teste por 30 dias com 1 contador. Meça conversão antes de escalar.

**Ângulo:** E se o contador começar a fazer inventário simplificado ele mesmo?

---
Ação: Proponha teste piloto de 30 dias.
Pergunta: Qual métrica define sucesso dessa parceria?
Ângulo: O contador está te testando também."
```

---

### 4. @tsunade — Inteligência de Mercado

**Quando usar:**
- Relatório semanal de jurisprudência
- Monitorar concorrentes locais
- Identificar oportunidades de conteúdo
- Alertas de decisões importantes
- Planejamento de missão semanal

**Comandos:**
```
@tsunade *relatorio-hokage [periodo]
@tsunade *monitorar-concorrentes
@tsunade *buscar-jurisprudencia {tema}
@tsunade *identificar-oportunidade
@tsunade *recomendar-agente {contexto}
```

**Exemplo de uso:**
```
Kage: "@tsunade, relatório hokage dessa semana"

Tsunade: "RELATÓRIO DE INTELIGÊNCIA ESTRATÉGICA
Período: 23/03/2026 a 29/03/2026

📌 Parte 1 – Briefing de Inteligência Jurídica

Diagnóstico: STJ decidiu que é nula cláusula de contrato bancário que prevê 
juros abusivos em financiamento de veículo, mesmo com contrato assinado.

Impacto Estratégico: OPORTUNIDADE – centenas de clientes em Francisco Morato 
podem ter ação revisional.

Recomendação Tática: Criar post educativo sobre revisão de financiamento.

Fonte: https://www.stj.jus.br/...

📌 Parte 2 – Análise de Mercado

Observação: Escritório 'Silva Advocacia' (Franco da Rocha) está rankeando em 
1º no Google para 'advogado usucapião'.

Análise Tática: Eles usam artigos semanais no blog.

Sugestão Estratégica: Criar 2 artigos/semana sobre usucapião com SEO local.

📌 Parte 3 – Missão da Semana

Agente Recomendado: Ero Sennin

Briefing:
Tema: Revisão de Financiamento de Veículo
Intenção: Topo de funil (atração)
Gancho: 'Pagando prestação de carro com juros abusivos? Você pode ter direito 
         à revisão.'"
```

---

### 5. @kabuto — Análise de Prazos

**Quando usar:**
- Varredura de e-mails judiciais
- Identificar prazos críticos
- Certidões de honorários
- Calcular vencimento de prazos

**Comandos:**
```
@kabuto *diagnostico-canais
@kabuto *listar-prazos {periodo}
@kabuto *buscar-certidoes {periodo}
@kabuto *calcular-prazo {data} {tipo}
@kabuto *criar-lembrete {processo} {prazo}
```

**Exemplo de uso:**
```
Kage: "@kabuto, diagnóstico dos canais"

Kabuto: "DIAGNÓSTICO DOS CANAIS - KABUTO

Kage, a varredura nos canais de comunicação foi concluída.

1. CERTIDÕES DE HONORÁRIOS EXPEDIDAS:
Proc. 0012345-67.2025.8.26.0123: Certidão de honorários disponível.
Proc. 0098765-43.2024.8.26.0456: Certidão de honorários disponível.

2. PRAZOS CRÍTICOS IDENTIFICADOS:
Proc. 0011122-33.2025.8.26.0789: Intimação para Contestação.
Vencimento estimado em 10/04/2026.
Proc. 0044455-66.2024.8.26.0321: Intimação para Manifestação sobre cálculos.
Vencimento estimado em 05/04/2026.

PLANO DE AÇÃO:
Aguardando seu comando para criar os lembretes para os prazos críticos.
Posso agendar? (Sim/Não)"
```

---

### 6. @ero-sennin — Conteúdo para Redes Sociais

**Quando usar:**
- Criar posts para Instagram/Facebook
- Roteiros de vídeo (Reels/TikTok)
- Artigos para LinkedIn
- Conteúdo educativo jurídico
- Metáforas para explicação de conceitos

**Comandos:**
```
@ero *post-rapido {tema}
@ero *roteiro-semanal
@ero *roteiro-video {tema}
@ero *sugerir-metfora {tema}
@ero *conectar-pilar {tema}
@ero *reaproveitar {conteudo}
```

**Exemplo de uso:**
```
Kage: "@ero, post rápido sobre usucapião extrajudicial"

Ero Sennin: "**Pilar:** Fortaleza Imobiliária

**Post Instagram:**

[Imagem: Cartório moderno com documentos]

Legenda:
"Você sabia que agora é possível fazer usucapião direto no cartório, sem 
processo judicial? 🏠✅

A usucapião extrajudicial é mais rápida (3-6 meses vs 2-5 anos) e mais barata.

Mas atenção: só serve para casos sem impugnação (ninguém contestando).

Somos especialistas em usucapião em Francisco Morato e região.

Quer saber se seu caso se encaixa? Comente 'EU QUERO' ou chame no direct! 👇

#usucapião #imoveis #franciscomorato #advogado"

**Horário:** 18:30 (pós-trabalho)

**Prompt Visual para @sai:**
"Cartório moderno, documentos sobre balcão de mármore, luz natural, paleta 
azul-marinho e branco, espaço negativo no topo para texto, fotorrealista"
```

---

### 7. @sai — Geração de Imagens

**Quando usar:**
- Gerar imagens para posts
- Direção de arte visual
- Prompts visuais para IA
- Otimizar imagens para redes sociais

**Comandos:**
```
@sai *gerar-imagem {prompt}
@sai *ajustar-palette {imagem} {cor}
@sai *criar-variacoes {imagem} [n]
@sai *otimizar-social {imagem}
```

**Exemplo de uso:**
```
Kage: "@sai, gerar imagem para post de usucapião"

Sai: [Imagem gerada]

Prompt usado:
"Casa antiga com jardim, luz suave do amanhecer, atmosfera de renovação, 
paleta azul-marinho e vermelho vinho, composição assimétrica com espaço 
negativo no canto superior direito, fotorrealista, estilo Hiroshi Yoshida 
contemporâneo"
```

---

### 8. @sakura — Peças Processuais

**Quando usar:**
- Redigir petições iniciais
- Contestações
- Recursos (apelação, agravo)
- Memoriais
- Peças processuais em geral

**Comandos:**
```
@sakura *redigir-peca {tipo} {caso}
@sakura *revisar-peca {arquivo}
@sakura *buscar-jurisprudencia {tema}
@sakura *aplicar-visual-law {peca}
@sakura *checklist-lgpd {documento}
```

**Exemplo de uso:**
```
Kage: "@sakura, redigir petição inicial de usucapião extrajudicial. 
Cliente: Maria Silva, imóvel residencial 120m², posse 15 anos, sem oposição."

Sakura: "[PARTE 1: RELATÓRIO DE MISSÃO]

Diagnóstico: Caso clássico de usucapião familiar (art. 1.240 CC). Posse 
mansa e pacífica por 15 anos, sem propriedade de outro imóvel.

Riscos: Verificar se não há débitos de IPTU ou condomínio.

Sugestões Visual Law:
- Incluir mapa do imóvel
- Timeline de posse
- Fotos atuais do imóvel

Checklist LGPD: ✅ Dados sensíveis tratados

[PARTE 2: MINUTA DA PEÇA]

EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DO CARTÓRIO DE...

[MARIA SILVA], brasileira, [...], vem propor AÇÃO DE USUCAPIÃO EXTRAJUDICIAL 
em face de [FAZENDA PÚBLICA DO ESTADO DE SÃO PAULO], pelos fatos e fundamentos 
a seguir...

DOS FATOS

A Requerente possui e reside no imóvel há 15 anos ininterruptos...

DO DIREITO

Art. 1.240 do Código Civil:
"Aquele que possuir, como sua, área urbana de até duzentos e cinquenta metros 
quadrados, por cinco anos ininterruptamente e sem oposição, utilizando-a para 
sua moradia ou de sua família, adquirir-lhe-á o domínio, desde que não seja 
proprietário de outro imóvel urbano ou rural."
(Fonte: http://www.planalto.gov.br/ccivil_03/_ato2007-2010/2002/lei/l10406.htm)

DOS PEDIDOS

Diante do exposto, requer:
a) A citação da Fazenda Pública...
b) A procedência total da ação para declarar a usucapião...
c) A expedição de mandado de registro ao Cartório de Imóveis...
```

---

### 9. @dev — Desenvolvedor Python

**Quando usar:**
- Implementar novas features
- Corrigir bugs
- Criar testes
- Code review
- Atualizar dependências

**Comandos:**
```
@dev *implement {feature}
@dev *fix {bug}
@dev *add-tests {módulo}
@dev *review-code {arquivo}
```

---

### 10. @qa — QA Specialist

**Quando usar:**
- Criar testes unitários
- Medir cobertura de testes
- Validar grafos LangGraph
- Configurar CI/CD

**Comandos:**
```
@qa *create-suite {módulo}
@qa *check-coverage
@qa *validate-graph {grafo}
```

---

### 11. @pm — Product Manager

**Quando usar:**
- Priorizar backlog
- Definir roadmap
- Criar épicos e stories
- Alinhar valor negócio vs técnico

**Comandos:**
```
@pm *priorizar-backlog
@pm *criar-epico {tema}
@pm *criar-story {epico}
@pm *roadmap
```

---

## 🔄 Workflows entre Agentes

### Workflow: Novo Cliente → Peça Processual

```
1. @minato → Triagem e qualificação do cliente
2. @kakashi → Estratégia e tese (gatilho sakura)
3. @sakura → Redação da peça processual
```

**Como ativar:**
```
Kage: "Workflow novo-cliente-peca para caso de usucapião da Maria Silva"
```

---

### Workflow: Inteligência → Conteúdo

```
1. @tsunade → Relatório de inteligência
2. @ero-sennin → Criação de conteúdo
3. @sai → Geração de imagens
```

**Como ativar:**
```
Kage: "Workflow inteligencia-conteudo para jurisprudência de usucapião"
```

---

### Workflow: Atendimento → Estratégia → Peça

```
1. @minato → Atendimento inicial
2. @kakashi → Análise estratégica
3. @sakura → Peça processual
```

**Como ativar:**
```
Kage: "Workflow atendimento-estrategia-peca para cliente trabalhista"
```

---

## 📊 Matriz de Roteamento

| Palavra-chave | Agente | Confiança |
|---|---|---|
| "cliente", "agendar", "consulta" | @minato | Alta |
| "tom de voz", "revisar texto" | @copywriter | Alta |
| "estratégia", "parceria", "decisão" | @kakashi | Alta |
| "relatório", "jurisprudência" | @tsunade | Alta |
| "prazo", "e-mail judicial" | @kabuto | Alta |
| "post", "instagram", "vídeo" | @ero-sennin | Alta |
| "imagem", "visual", "arte" | @sai | Alta |
| "peça", "petição", "recurso" | @sakura | Alta |
| "bug", "implementar", "teste" | @dev | Alta |
| "teste", "cobertura" | @qa | Alta |
| "backlog", "priorizar" | @pm | Alta |

---

## 🎯 Dicas de Uso

1. **Use menções explícitas** quando souber qual agente quer: `@sakura, redija...`
2. **Deixe o router decidir** quando não tiver certeza: apenas descreva a tarefa
3. **Use workflows** para tarefas multi-agente
4. **Handoff automático** é sugerido quando um agente completa sua parte
5. **Contexto é mantido** entre handoffs — não precisa repetir informações

---

## 🚀 Ativação Rápida

```bash
# Listar todos os agentes
*list-agents

# Ver status de um agente
*agent-status {nome}

# Ativar workflow
*workflow {nome}

# Forçar roteamento para agente específico
@{agente} {comando}
```
