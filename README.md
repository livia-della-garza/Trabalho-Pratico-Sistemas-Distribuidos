# Assistente Acadêmico Inteligente

## Problema abordado

O Assistente Acadêmico Inteligente é um sistema desenvolvido para auxiliar estudantes, professores e servidores no acesso rápido e automatizado às informações acadêmicas da pós-graduação do DCC.

O sistema utiliza documentos institucionais oficiais como base de conhecimento, permitindo responder perguntas relacionadas a:

- Regulamentos dos programas do PPGCC;
- Instruções Normativas (IN’s);
- Resoluções;
- Formulários acadêmicos;
- Rotinas acadêmicas ;

A proposta busca reduzir o tempo gasto na busca manual por informações e facilitar o acesso às normas e rotinas acadêmicas de forma centralizada, inteligente e acessível.

---

## Tecnologias utilizadas

- **Linguagem**: Python 3.14.5
- **Bibliotecas**:
    - Ollama v0.23.1
    - Langchain
    - FastMCP v3.3.1
- **Banco de dados**:
    - **Vetorial**: ChromaDB 1.5.9
    - **Relacional**: 
- **Frontend**: Streamlit 1.57.0

---

## Arquitetura do sistema

![Arquitetura do sistema](/docs/diagrams/architecture/architecture.png)

---

## Componentes

### Interface

**Usuário** — Pessoa que usa o chatbot. Envia a pergunta em texto livre e lê a resposta na tela.

**Frontend** — Aplicação com a qual o usuário conversa. Mostra o histórico da conversa, envia a pergunta ao MCP e exibe a resposta recebida.


### Gateway

**MCP** — Camada entre o frontend e os microsserviços. O frontend só fala com o MCP. O MCP recebe a pergunta, decide qual microsserviço chamar (após o roteamento) e devolve a resposta ao frontend. Os microsserviços não são expostos diretamente à interface.


### Microsserviço de roteamento

Responsável por classificar a pergunta antes do tratamento definitivo. O resultado é **FIM** (resposta pronta, sem buscar normas) ou **RAG** (precisa consultar as normas indexadas).

- **Embedding** — Converte a pergunta em vetor numérico. Esse vetor é comparado com exemplos de perguntas já classificadas como FIM ou RAG, armazenados no banco vetorial.
- **Banco vetorial** — Contém os exemplos usados na classificação. Para cada pergunta nova, o serviço obtém o score de similaridade com cada rota e escolhe a de maior score como decisão.
- **Banco relacional** — Grava a pergunta, a decisão (FIM ou RAG) e dados de auditoria. Não armazena a resposta final ao usuário; serve para histórico e análise do roteamento.


### Microsserviço de resposta padrão

Atende perguntas classificadas como **FIM**: saudações, orientações genéricas, pedidos fora do escopo das normas ou casos com texto de resposta já definido.

- **Resposta padrão** — Componente que monta a resposta. Usa regras e templates definidos no próprio serviço (por exemplo, mensagem de boas-vindas ou aviso de escopo). O texto da resposta não é lido do banco relacional.
- **Banco relacional** — Grava a pergunta, a resposta enviada ao usuário e metadados da interação, para histórico e métricas do atendimento FIM.


### Microsserviço de RAG

Atende perguntas classificadas como **RAG**: o usuário quer informação baseada nas normas e documentos de pós-graduação da UFLA.

- **Embedding** — Gera o vetor da pergunta e busca no banco vetorial os trechos de normas mais próximos do sentido da pergunta.
- **Banco vetorial** — Armazena as normas e documentos já fragmentados e indexados. A busca retorna os trechos que serão usados como contexto na geração da resposta.
- **LLM** — Recebe a pergunta e os trechos encontrados, e produz a resposta em texto corrido para o usuário. É o único ponto da arquitetura em que a resposta é gerada por modelo de linguagem.
- **Banco relacional** — Grava a pergunta, a resposta gerada e metadados da interação, após a LLM concluir. Mesmo papel de histórico que nos demais microsserviços.

---

## Fluxo de dados (diagramas de sequência)

### Fluxo completo

![Fluxo de dados geral](/docs/diagrams/sequence/orchestration-sequence.svg)

### Roteamento

![Fluxo do roteamento](/docs/diagrams/sequence/routing-service-sequence.svg)

### RAG

![Fluxo do RAG](/docs/diagrams/sequence/rag-service-sequence.svg)

### Resposta padrão

![Fluxo da resposta](/docs/diagrams/sequence/fallback-response-service-sequence.svg)