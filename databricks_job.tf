# Arquivo: databricks_job.tf

resource "databricks_job_cluster" "job_cluster_definition" {
  job_cluster_key = "cluster_padrao"
  
  new_cluster {
    spark_version = "13.3.x-scala2.12"
    node_type_id  = "Standard_F4"
    num_workers   = 0
    custom_tags = {
      ResourceClass = "SingleNode"
    }

    libraries = [
      { maven { coordinates = "com.microsoft.azure:azure-eventhubs-spark_2.12:2.3.22" } },
      { maven { coordinates = "com.amazon.deequ:deequ:2.0.6-spark-3.4" } },
      { pypi  { package     = "pydeequ==1.1.0" } }
    ]

    spark_conf = {
      "spark.databricks.cluster.profile" = "singleNode"
      "spark.master" = "local[*]"
      "spark.hadoop.fs.azure.account.auth.type.${var.storage_account_name}.dfs.core.windows.net" = "OAuth"
      "spark.hadoop.fs.azure.account.oauth.provider.type.${var.storage_account_name}.dfs.core.windows.net" = "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider"
      "spark.hadoop.fs.azure.account.oauth2.client.id.${var.storage_account_name}.dfs.core.windows.net" = var.client_id
      "spark.hadoop.fs.azure.account.oauth2.client.secret.${var.storage_account_name}.dfs.core.windows.net" = var.client_secret
      "spark.hadoop.fs.azure.account.oauth2.client.endpoint.${var.storage_account_name}.dfs.core.windows.net" = "https://login.microsoftonline.com/${var.tenant_id}/oauth2/token"
    }

    spark_env_vars = {
      EVENT_HUB_CONNECTION_STRING = var.eh_connection_string
      SPARK_VERSION               = "3.5"
    }
  }
}

# Define o Job com todas as tarefas
resource "databricks_job" "pipeline_de_anomalias_bundle" {
  name = "[BUNDLE] Pipeline de Anomalias Financeiras"
  
  # Referencia o cluster que acabamos de definir
  job_cluster {
    job_cluster_key = databricks_job_cluster.job_cluster_definition.job_cluster_key
  }

  task {
    task_key = "Atualizar_Perfis_Batch"
    job_cluster_key = databricks_job_cluster.job_cluster_definition.job_cluster_key
    notebook_task {
      notebook_path = "notebooks/03_batch_profiling.ipynb"
    }
  }

  task {
    task_key = "Detectar_Alertas_Streaming"
    depends_on {
      task_key = "Atualizar_Perfis_Batch"
    }
    job_cluster_key = databricks_job_cluster.job_cluster_definition.job_cluster_key
    notebook_task {
      notebook_path = "notebooks/02_realtime_alerts.ipynb"
    }
  }

  task {
    task_key = "Validar_Qualidade_Dados"
    depends_on {
      task_key = "Detectar_Alertas_Streaming"
    }
    job_cluster_key = databricks_job_cluster.job_cluster_definition.job_cluster_key
    notebook_task {
      notebook_path = "notebooks/04_data_quality_checks.ipynb"
    }
  }


}