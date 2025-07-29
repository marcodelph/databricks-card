# Pipeline Híbrido de Detecção de Anomalias Financeiras

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

## 📖 Resumo

Este projeto consiste na construção de um pipeline de detecção de fraude em tempo real, demonstrando uma arquitetura de dados moderna e escalável na nuvem. Utilizando o **Microsoft Azure**, o pipeline ingere um fluxo contínuo de transações simuladas via **Azure Event Hubs**. O processamento e a transformação dos dados são orquestrados pelo **Azure Databricks**, que emprega **PySpark** e **Spark Structured Streaming** para aplicar a arquitetura Medallion (`raw`, `core`, `analytics`) sobre o **Delta Lake**. A detecção de anomalias é feita com uma abordagem híbrida, combinando regras de negócio em tempo real com a criação de perfis de usuário em batch.