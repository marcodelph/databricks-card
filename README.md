# Pipeline Híbrido de Detecção de Anomalias Financeiras

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)


## 📖 1. Resumo

Este projeto consiste na construção de um pipeline de detecção de fraude em tempo real, demonstrando uma arquitetura de dados moderna e escalável na nuvem. Utilizando o **Microsoft Azure**, o pipeline ingere um fluxo contínuo de transações simuladas via **Azure Event Hubs**. O processamento e a transformação dos dados são orquestrados pelo **Azure Databricks**, que emprega **PySpark** e **Spark Structured Streaming** para aplicar a arquitetura Medallion (`raw`, `core`, `analytics`) sobre o **Delta Lake**. A detecção de anomalias é feita com uma abordagem híbrida, combinando regras de negócio em tempo real com a criação de perfis de usuário em batch.

## 🎯 2. O Problema de Negócio

Sistemas tradicionais de detecção de fraude frequentemente se baseiam em regras estáticas (ex: "toda transação acima de R$ 5.000 é suspeita"). Essa abordagem gera muitos falsos positivos e não captura anomalias sutis, pois o que é "normal" para um usuário pode ser altamente anômalo para outro. Este projeto resolve esse problema através da detecção contextual e individualizada.

## 🏗️ 3. A Solução Arquitetural

A solução foi desenhada sobre dois padrões de arquitetura de dados líderes de mercado:

* **Arquitetura Híbrida (Lambda Simplificada):** Combina um pipeline **batch** para análises profundas e criação de perfis de usuário com um pipeline **streaming** para enriquecimento e alertas em tempo real.
* **Arquitetura Medallion:** Organiza os dados em camadas de qualidade progressiva (`raw`, `core`, `analytics`) dentro do Data Lake, garantindo governança e rastreabilidade.

## 🔀 4. Fluxo do Pipeline de Dados

A jornada do dado através do pipeline ocorre em quatro etapas principais:

1.  **Ingestão (Streaming):** Um script Python (`producer.py`) simula um fluxo contínuo de transações, com anomalias contextuais injetadas, e as publica no **Azure Event Hubs**.
2.  **Camada Raw:** Um notebook Spark Streaming (`01_streaming_ingestion`) consome os dados do Event Hubs, faz uma limpeza mínima e os persiste em formato Delta na camada `raw` do Data Lake, criando uma fonte da verdade imutável.
3.  **Camada Core:** Um notebook Spark **Batch** (`03_batch_profiling`), orquestrado por um **Databricks Job** diário, lê os dados da camada `raw` e cria perfis de comportamento para cada usuário (gasto médio, desvio padrão, etc.), salvando o resultado na camada `core`.
4.  **Camada Analytics:** Um segundo notebook Spark Streaming (`02_realtime_alerts`) lê as novas transações da camada `raw` e as enriquece em tempo real, através de um **stream-table join** com os perfis da camada `core`. Se uma transação desvia significativamente do perfil do usuário, um alerta é gerado na camada `analytics`.

## 🛠️ 5. Stack de Tecnologias

| Categoria | Ferramenta/Serviço | Propósito |
| :--- | :--- | :--- |
| **Plataforma Cloud** | Microsoft Azure | Provedor de todos os serviços de nuvem. |
| **Ingestão de Streaming** | Azure Event Hubs | Serviço de mensageria para receber o fluxo de dados. |
| **Armazenamento** | Azure Data Lake Storage Gen2 | Data Lake central para as camadas `raw`, `core`, `analytics`. |
| **Processamento** | Azure Databricks | Plataforma unificada para execução de jobs **PySpark** (incluindo o **Hive Metastore** para gerenciamento de metadados). |
| **Formato dos Dados** | Delta Lake | Formato de tabela que traz transações ACID ao Data Lake. |
| **Segurança** | Azure Key Vault & Microsoft Entra ID | Gestão de segredos e controle de acesso via Service Principal. |
| **Conceitos Fundamentais**| Apache Hadoop | O projeto aplica os conceitos do ecossistema Hadoop em um paradigma moderno: o **ADLS Gen2** como substituto do HDFS para armazenamento distribuído e o **Spark** como motor de processamento. |
| **Linguagens** | Python & SQL | Linguagens usadas para o produtor e para os notebooks Spark. |
| **Dev Tools** | Git & GitHub | Versionamento de código. |

## 🚀 6. Conceitos de DevOps e Boas Práticas

Este projeto foi construído com foco em práticas profissionais de engenharia de software e DevOps:

* **Segurança e Governança Robusta (SecOps):** A comunicação entre Databricks e Data Lake é autenticada via **Microsoft Entra ID (Service Principal)**, seguindo o **Princípio do Menor Privilégio** e aplicando uma **governança de dados robusta** com papéis RBAC específicos. Segredos são centralizados e gerenciados de forma segura no **Azure Key Vault**.
* **Otimização de Custos (FinOps):** Todas as decisões de infraestrutura foram tomadas com o custo em mente: uso do tier **Standard** do Databricks, cluster **Single Node** que é desligado automaticamente (`auto-terminate`), e uso do gatilho **`trigger(availableNow=True)`** para economizar recursos de computação.
* **Automação e Orquestração (DevOps/DataOps):** O pipeline foi projetado para ser totalmente automatizado. Os notebooks são orquestrados via **Databricks Jobs**, com o job batch rodando em um cronograma diário, demonstrando práticas de **DevOps** para o ciclo de vida dos dados.

