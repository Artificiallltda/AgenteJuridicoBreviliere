# Exemplos de Uso dos Agentes — Squad Jurídico Breviliere

**Versão:** 1.0 | **Data:** 29/03/2026

Este arquivo contém exemplos práticos de uso para cada agente da squad.

---

## @minato — Atendimento e Triagem

### Exemplo 1: Novo Cliente (Caso Simples)

**Input:**
```
@minato, responder: "Olá, preciso de ajuda com meu divórcio. Meu marido 
sumiu há 3 anos e quero me divorciar e ficar com a guarda dos meus 2 filhos."
```

**Output:**
```
Olá! Entendo sua situação e estou aqui para ajudar. 👋

O divórcio com ausência do cônjuge é possível, e a guarda dos filhos pode 
ser definida em seu favor.

Para eu entender melhor seu caso, você poderia me informar:
- Você tem o certidão de casamento?
- Seus filhos são menores de idade?
- Você sabe o último endereço dele?

Com essas informações, consigo te orientar melhor sobre os próximos passos.

[META-DADO]
Cenário: A - Novo Cliente
Resumo do Cliente: Mulher busca divórcio com marido ausente há 3 anos + guarda de 2 filhos.
Ação Tomada: Triagem inicial com perguntas de qualificação.
Alerta de Complexidade: MÉDIA (divórcio com ausência + guarda).
Pendência: Aguardando respostas para definir próximo passo.
```

---

### Exemplo 2: Novo Cliente (Caso Complexo - Honorários)

**Input:**
```
@minato, responder: "Fui demitido há 6 meses, minha empresa não pagou nenhuma 
verba rescisória, tenho FGTS atrasado de 2 anos, além disso tenho um acidente 
de trabalho não reconhecido, e acho que tenho direito a uma aposentadoria por 
invalidez que o INSS negou. Quero processar a empresa e o INSS também. Tenho 
muitos documentos mas não sei organizar."
```

**Output:**
```
Olá! Entendo que você está passando por uma situação complexa e delicada.

Analisando seu relato, identificamos múltiplas questões jurídicas que exigem 
uma análise documental detalhada:
- Verbas rescisórias não pagas
- FGTS em atraso
- Acidente de trabalho não reconhecido
- Negativa de aposentadoria por invalidez no INSS

Devido à complexidade técnica do seu caso e à necessidade de análise 
documental minuciosa, nossa consulta estratégica possui honorários no 
valor de R$ 162,00.

Nesta consulta, vamos:
1. Analisar todos os seus documentos
2. Identificar todas as teses jurídicas cabíveis
3. Definir a melhor estratégia para seu caso
4. Explicar prazos e expectativas reais

Podemos agendar? Qual o melhor horário para você esta semana?

[META-DADO]
Cenário: A - Novo Cliente (Complexo)
Resumo do Cliente: Múltiplas demandas (trabalhista + previdenciária + acidentária).
Ação Tomada: Aplicou Filtro de Complexidade ALTA e cobrou R$ 162,00 de consulta.
Alerta de Complexidade: ALTA (envolve múltiplas teses, valores altos, grande volume documental).
Pendência: Aguardando confirmação de agendamento e pagamento.
```

---

### Exemplo 3: Cliente Atual (Dúvida)

**Input:**
```
@minato, cliente atual perguntando: "Doutor, já faz 2 meses que entramos com 
o inventário e até agora nada. Quanto tempo demora normalmente? Estou preocupado."
```

**Output:**
```
Olá! Entendo sua ansiedade. Vou te explicar o prazo normal do inventário. 📋

Inventário extrajudicial (em cartório): 30-60 dias em média.
Inventário judicial: 6 meses a 2 anos (depende da vara e se há concordância).

Como seu caso tem 2 meses, está dentro do prazo esperado.

O que estamos fazendo agora:
- Aguardando avaliação dos bens pelo juízo
- Próxima audiência prevista para 15/04/2026

Assim que tivermos novidades, te comunicamos imediatamente.

Fique tranquilo(a) — seu processo está em andamento normal.

[META-DADO]
Cenário: B - Cliente Atual
Resumo do Cliente: Ansioso com prazo do inventário (2 meses sem atualização).
Ação Tomada: Tranquilizou com prazos reais + explicou status atual.
Alerta de Complexidade: BAIXA (apenas ansiedade do cliente).
Pendência: Nenhuma — cliente apenas buscava tranquilização.
```

---

### Exemplo 4: Comunicação Formal

**Input:**
```
@minato, redigir formal para e-mail: notificar cliente sobre audiência 
trabalhista dia 10/04 às 14h, levar documentos originais e 2 testemunhas.
```

**Output:**
```
Prezados,

Comunicamos que foi designada audiência trabalhista para o processo 
0012345-67.2025.8.26.0123.

**Data:** 10 de abril de 2026 (sexta-feira)
**Horário:** 14:00 horas
**Local:** Vara do Trabalho de Francisco Morato - Rua XYZ, 123

**Documentos obrigatórios:**
- Carteira de Trabalho original
- RG e CPF originais
- Comprovante de residência
- Todos os documentos da rescisão

**Testemunhas:**
- Apresentar 2 testemunhas (máximo 3)
- Devem levar RG original
- Não podem ser familiares

Em caso de impedimento, comunicar com 48h de antecedência.

Atenciosamente,
Clã Brevilieri Advocacia
(11) 99999-9999
```

---

## @copywriter — Tom de Voz e Copywriting

### Exemplo 1: Aplicar Persuasão

**Input:**
```
@copy, aplica persuasão: "Fazemos usucapião. Entre em contato."
```

**Output:**
```
Versão com gatilhos de persuasão:

"Já ajudamos +500 famílias em Francisco Morato a conquistarem o sonho da 
casa própria através da usucapião. 🏠✅

Assim como a Sra. Maria, que após 20 anos morando no mesmo imóvel, hoje 
tem a escritura 100% regularizada em seu nome.

A usucapião extrajudicial é mais rápida (3-6 meses) e pode ser feita direto 
no cartório — sem processo judicial.

Quer saber se você se encaixa nos requisitos?

Comente 'EU QUERO' ou chame no direct para uma análise gratuita do seu caso!

#usucapião #imoveis #franciscomorato

---
Gatilhos aplicados:
✅ Prova Social (+500 famílias)
✅ História de sucesso (Sra. Maria)
✅ Autoridade (especialistas na região)
✅ Benefício claro (3-6 meses vs 2-5 anos)
✅ CTA duplo (comentário + direct)
```

---

### Exemplo 2: Sugerir Metáfora

**Input:**
```
@copy, sugere metáfora para explicar holding familiar para cliente leigo.
```

**Output:**
```
Metáforas para Holding Familiar:

1. **Caneleira do Empresário:**
"Empresário sem holding é como jogador sem caneleira. Pode até jogar, 
mas o risco é todo dele. A holding é sua proteção."

2. **Antivírus Patrimonial:**
"Blindar sua empresa com holding é como instalar antivírus no seu 
patrimônio. Não impede todos os ataques, mas reduz drasticamente 
os danos."

3. **Cofre da Família:**
"A holding é como um cofre que separa seu patrimônio pessoal do 
patrimônio da empresa. Se a empresa for atacada, seu cofre 
permanece seguro."

4. **Guarda-Chuva:**
"Holding familiar é como guarda-chuva: você não usa todo dia, 
mas quando vem a tempestade, agradece por ter."

Recomendação: Use a metáfora #2 (Antivírus) para clientes empresários 
de tecnologia. Use #1 (Caneleira) para clientes mais tradicionais.
```

---

### Exemplo 3: Revisar Tom

**Input:**
```
@copy, tone-check: "Informamos que seu processo foi arquivado devido à 
falta de documentos. Favor apresentar no prazo de 5 dias."
```

**Output:**
```
Análise de Tom:

❌ Problemas identificados:
- "Informamos" = impessoal, frio
- "devido à falta" = soa como culpa do cliente
- "Favor apresentar" = linguagem burocrática
- Sem empatia com a situação

✅ Sugestão de reescrita (Estilo Clark Kent):

"Olá! Precisamos da sua ajuda para dar continuidade ao seu processo. 📋

Identificamos que alguns documentos ainda precisam ser apresentados. 
Para não prejudicar seu caso, você pode nos enviar até [data]?

Documentos pendentes:
- [Lista de documentos]

Fique tranquilo(a) — isso é normal e vamos te ajudar em cada passo.

Dúvidas? É só chamar! Estamos aqui para facilitar sua vida.

---
Tom aplicado: Confiante, Claro, Humano, Empático, Elegante ✅
```

---

## @kakashi — Estratégia de Bastidores

### Exemplo 1: Analisar Parceria

**Input:**
```
@kakashi, um contador me propôs parceria: ele me indica clientes de inventário 
e eu indico clientes de contabilidade pra ele. Ele fica com 20% dos meus 
honorários. Aceito?
```

**Output:**
```
Parceria com contador tem armadilhas. Vou ser direto:

**O problema dos 20%:**
- Contador médio indica 2-3 escritórios, não só você
- Você vira commodity na pilha
- 20% é caro se ele só faz a indicação (sem qualificação)

**O que funciona:**
- Contador vê o cliente PRIMEIRO (antes de você)
- Inventário tem sinergia natural com contabilidade
- Se for exclusividade mútua, pode ser mina de ouro

**Perguntas que você precisa fazer ANTES de decidir:**
1. Quantos clientes de inventário ele atende por mês?
2. Ele já indicou clientes pra outros escritórios? Qual taxa de conversão?
3. Ele está disposto a fazer qualificação prévia ou só repassa contato?

**Minha recomendação:**
Teste piloto de 30 dias. Métricas claras:
- Mínimo 5 indicações/mês
- Taxa de conversão mínima de 40%
- Se não bater, renegocia ou cancela

---
Ação: Proponha teste de 30 dias com métricas.
Pergunta: Qual é o pior cenário se você aceitar e não funcionar?
Ângulo: O contador está te testando também. Ele vai medir sua conversão.
```

---

### Exemplo 2: Preparar para Sakura

**Input:**
```
@kakashi, prepra para sakura. Cliente comprou imóvel financiado, pagou 30 
parcelas e aí a construtora atrasou a obra em 2 anos. Ele quer rescindir 
o contrato e receber tudo de volta em dobro. Tem fotos, contrato, prints 
de WhatsApp com o vendedor prometendo entrega em 18 meses.
```

**Output:**
```
Sakura, missão de Guerra. Abaixo estão os fatos limpos e as defesas mapeadas.

A sua tarefa é redigir a **Ação de Rescisão Contratual com Repetição de Indébito** 
com base nas seguintes diretrizes táticas que defini:

**Fatos Filtrados:**
- Autor: [Nome do cliente]
- Ré: [Construtora]
- Contrato de compra e venda de imóvel na planta, assinado em [data]
- Preço total: R$ [valor]
- Entrada: 30% (R$ [valor])
- Saldo: financiado em [número] parcelas
- Prazo de entrega prometido: 18 meses (cláusula X do contrato)
- Atraso da construtora: 24 meses (e contando)
- Autor pagou 30 parcelas do financiamento
- Vendedor fez promessas por WhatsApp (prints anexos)
- Fotos do canteiro de obras parado (anexas)
- Notificação extrajudicial enviada em [data], sem resposta

**Teses de Ataque/Defesa:**
1. Descumprimento contratual da construtora (art. 389 CC)
2. Dano moral por atraso na entrega do imóvel (Súmula 362 STJ)
3. Repetição de indébito em dobro (art. 42, parágrafo único, CDC)
4. Juros de 1% ao mês + correção monetária
5. Honorários advocatícios de 20%
6. Inversão do ônus da prova (art. 6º, VIII, CDC)

**Ângulo Narrativo:**
Focar na boa-fé do comprador (família que sonhou com casa própria) vs 
má-fé da construtora (promessas vazias, canteiro parado, silêncio após 
notificação). Humanizar o sofrimento da espera (2 anos sem casa).

**O Ponto Cego:**
A construtora pode alegar "caso fortuito" (chuvas, pandemia, etc). 
Antecipar esse argumento e demonstrar que atraso de 24 meses é 
desproporcional e não justificado por eventos externos.

Execute o genjutsu com exaustão argumentativa. Não resuma. Mais é Mais.
```

---

## @tsunade — Inteligência de Mercado

### Exemplo 1: Relatório Semanal

**Input:**
```
@tsunade, relatório hokage dos últimos 7 dias
```

**Output:**
```
RELATÓRIO DE INTELIGÊNCIA ESTRATÉGICA
Período: 23/03/2026 a 29/03/2026

📌 Parte 1 – Briefing de Inteligência Jurídica

Diagnóstico: TJSP decidiu que cartório não pode exigir certidão negativa 
de débitos trabalhistas para usucapião extrajudicial.

Impacto Estratégico: OPORTUNIDADE – remove barreira para 40% dos clientes 
que têm pequenas dívidas trabalhistas.

Recomendação Tática: Criar post urgente: "Cartório não pode mais exigir 
certidão trabalhista para usucapião".

Fonte: https://www.tjsp.jus.br/...

Nota Estratégica: Impacta diretamente nosso serviço de Regularização 
de Imóveis.

📌 Parte 2 – Análise de Mercado (Radar da Concorrência)

Observação: Escritório "Brevi Advocacia" (Francisco Morato) está 
rankeando em 2º no Google para "advogado inventário".

Análise Tática: Eles têm 15 artigos no blog, todos com 1000+ palavras.

Sugestão Estratégica: Criar 3 artigos longos sobre inventário 
(1500+ palavras) com SEO local.

📌 Parte 3 – Orquestração Estratégica (Missão da Semana)

Agente Recomendado: Ero Sennin

Briefing da Missão (Ero Sennin):
Tema: Cartório não exige mais certidão trabalhista para usucapião
Intenção (Funil): Topo (Atração)
Gancho (Redes Sociais): "Nova decisão do TJSP facilita usucapião 
                         extrajudicial em SP"
Post (Google Meu Negócio): "Usucapião extrajudicial ficou mais fácil. 
                            Somos especialistas em Francisco Morato."
```

---

## @kabuto — Análise de Prazos

### Exemplo 1: Diagnóstico de Canais

**Input:**
```
@kabuto, diagnóstico dos canais
```

**Output:**
```
DIAGNÓSTICO DOS CANAIS - KABUTO

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
Posso agendar? (Sim/Não)
```

---

## @ero-sennin — Conteúdo para Redes Sociais

### Exemplo 1: Post Rápido

**Input:**
```
@ero, post rápido sobre nova decisão do STJ que permite usucapião de imóvel 
abandonado mesmo com proprietário vivo.
```

**Output:**
```
**Pilar:** Fortaleza Imobiliária

**Post Instagram:**

[Imagem: Casa abandonada com placa de "vende-se"]

Legenda:
"ATENÇÃO: Nova decisão do STJ muda as regras da usucapião! 🏠⚖️

Agora é possível fazer usucapião de imóvel ABANDONADO mesmo com o 
proprietário VIVO.

Antes: só dava se o proprietário tivesse falecido.
Agora: basta comprovar abandono + posse prolongada.

Requisitos:
✅ Posse por 15 anos (ou 10 com pagamento de impostos)
✅ Imóvel realmente abandonado
✅ Sem oposição do proprietário

Isso abre portas para milhares de imóveis em Francisco Morato e região 
que estão parados há anos.

Quer saber se você se encaixa? Comente 'EU QUERO' ou chame no direct!

#usucapião #stj #imoveis #franciscomorato #advogado"

**Horário:** 18:30 (pós-trabalho)

**Prompt Visual para @sai:**
"Casa abandonada com jardim tomado por mato, placa de vende-se inclinada, 
luz dramática do entardecer, paleta azul-marinho e vermelho vinho, 
espaço negativo no topo para texto, fotorrealista"
```

---

## @sakura — Peças Processuais

### Exemplo 1: Petição Inicial de Usucapião

**Input:**
```
@sakura, redigir petição inicial de usucapião familiar. Cliente: João Silva, 
imóvel 100m², posse 12 anos, casado, 2 filhos, não tem outro imóvel. 
Endereço: Rua das Flores, 123, Francisco Morato/SP.
```

**Output:**
```
[PARTE 1: RELATÓRIO DE MISSÃO]

Diagnóstico: Caso clássico de usucapião familiar (art. 1.240 CC). 
Posse mansa e pacífica por 12 anos, sem propriedade de outro imóvel.

Riscos: Verificar se não há débitos de IPTU. Confirmar que posse 
é contínua (sem interrupções).

Sugestões Visual Law:
- Incluir foto atual do imóvel
- Timeline de posse (2014-2026)
- Comprovantes de pagamento de contas (água, luz)

Checklist LGPD: ✅ Dados tratados conforme lei

[PARTE 2: MINUTA DA PEÇA]

EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DO CARTÓRIO DE REGISTRO 
DE IMÓVEIS DA COMARCA DE FRANCISCO MORATO/SP

**USUCAPIÃO EXTRAJUDICIAL**

JOÃO SILVA, brasileiro, casado, [profissão], RG [número], CPF [número], 
residente e domiciliado na Rua das Flores, 123, Francisco Morato/SP, 
vem propor

**AÇÃO DE USUCAPIÃO FAMILIAR**

em face da FAZENDA PÚBLICA DO ESTADO DE SÃO PAULO, pelos fatos e 
fundamentos a seguir:

DOS FATOS

1. O Requerente possui e reside no imóvel situado na Rua das Flores, 123, 
Francisco Morato/SP, há 12 anos ininterruptos (desde 2014).

2. O imóvel possui área de 100m² e é utilizado para moradia do Requerente 
e de sua família (esposa e 2 filhos).

3. Durante todo esse período, o Requerente manteve posse mansa e pacífica, 
sem qualquer oposição de terceiros.

4. O Requerente NÃO é proprietário de outro imóvel urbano ou rural.

[...continua com fundamentação e pedidos...]
```

---

## @dev — Desenvolvimento

### Exemplo 1: Implementar Feature

**Input:**
```
@dev, implementar endpoint GET /admin/kb/search que faz busca semântica 
na base de conhecimento e retorna top 5 resultados com score.
```

**Output:**
```python
# src/api/admin/kb.py

from fastapi import APIRouter, Query
from rag.indexer import LegalIndexer

router = APIRouter(prefix="/admin/kb", tags=["Knowledge Base"])
_indexer = None

def get_indexer() -> LegalIndexer:
    global _indexer
    if _indexer is None:
        _indexer = LegalIndexer()
    return _indexer

@router.get("/search")
async def search_knowledge_base(
    query: str = Query(..., description="Termo de busca"),
    limit: int = Query(5, ge=1, le=20, description="Número máximo de resultados")
):
    """
    Busca semântica na base de conhecimento.
    
    Retorna os top N resultados mais relevantes com score.
    """
    indexer = get_indexer()
    results = await indexer.query(query, top_k=limit)
    
    return {
        "query": query,
        "results": [
            {
                "id": doc_id,
                "content": doc_content,
                "score": float(score),
                "metadata": metadata
            }
            for doc_id, doc_content, score, metadata in zip(
                results['ids'][0],
                results['documents'][0],
                results['distances'][0],
                results['metadatas'][0]
            )
        ]
    }
```

---

## Fluxos Completos (Workflows)

### Workflow: Novo Cliente → Peça Processual

**Input:**
```
Workflow novo-cliente-peca: Cliente foi demitido sem justa causa, empresa 
deve 6 meses de FGTS e verbas rescisórias. Quer processar.
```

**Execução:**

**Passo 1: @minato (Triagem)**
```
"Olá! Entendo sua situação. A demissão sem justa causa gera direitos 
como multa do FGTS (40%), saque do FGTS, seguro-desemprego e verbas 
rescisórias.

Para eu entender melhor:
- Qual era seu salário bruto?
- Quanto tempo trabalhou na empresa?
- Você tem anotações da rescisão?

Podemos agendar uma consulta estratégica por R$ 162,00 para analisar 
seu caso em detalhe?"
```

**Passo 2: @kakashi (Estratégia)**
```
Caso trabalhista padrão, mas com FGTS atrasado há 6 meses = multa 
de 100% sobre depósitos (art. 22 da Lei 8.036/90).

Teses principais:
1. Verbas rescisórias (art. 477 CLT)
2. Multa de 40% do FGTS
3. Multa de 100% sobre depósitos atrasados
4. Danos morais (se houver demora excessiva)

Ponto forte: Empresa não tem como negar depósitos não feitos.
Ponto fraco: Cliente precisa provar tempo de serviço (testemunhas).

[Sakura, usar essas teses na petição]
```

**Passo 3: @sakura (Peça)**
```
[Redige petição inicial trabalhista com as teses mapeadas]
```

---

## Dicas de Uso

1. **Seja específico:** Quanto mais detalhes, melhor o agente entende
2. **Use workflows:** Para tarefas multi-agente, economize tempo
3. **Handoff é automático:** O contexto é mantido entre agentes
4. **Revise sempre:** Agentes sugerem, você decide
5. **Feedback melhora:** Se um agente errar, corrija — ele aprende
