"""
Exportador de dados de contratos para CSV
"""
import os
import csv
import json
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic


class CSVExporter:
    """Exporta dados de contratos para formato CSV estruturado"""

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Inicializa o exportador

        Args:
            anthropic_api_key: Chave da API Anthropic (opcional)
        """
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.anthropic = Anthropic(api_key=self.api_key)
        else:
            self.anthropic = None

    def extract_structured_data(
        self,
        contract_text: str,
        contract_id: str
    ) -> Dict:
        """
        Extrai dados estruturados do texto do contrato usando Claude

        Args:
            contract_text: Texto do contrato
            contract_id: ID do contrato

        Returns:
            Dict com dados estruturados
        """
        if not self.anthropic:
            raise ValueError("API Key do Anthropic não configurada")

        prompt = f"""
        Analise o seguinte contrato de aluguel e extraia as informações em formato JSON estruturado.

        Estrutura esperada:
        {{
            "contract_id": "{contract_id}",
            "arrendador": {{
                "nome": "nome completo ou empresa",
                "documento": "DNI/CIF/NIF",
                "endereco": "endereço completo"
            }},
            "arrendatarios": [
                {{
                    "nome": "nome completo",
                    "documento": "DNI/NIE",
                    "endereco": "endereço"
                }}
            ],
            "imovel": {{
                "endereco": "endereço completo",
                "superficie": "metros quadrados",
                "ref_catastral": "referência catastral",
                "tipo": "apartamento/casa/etc"
            }},
            "condicoes_economicas": {{
                "renda_mensal": "valor em euros (apenas número)",
                "gastos_comuns_mensal": "valor em euros",
                "gastos_comuns_anual": "valor em euros",
                "ibi_mensal": "valor em euros",
                "ibi_anual": "valor em euros",
                "fianca": "valor ou descrição"
            }},
            "duracao": {{
                "prazo": "duração do contrato",
                "data_inicio": "data no formato DD/MM/YYYY",
                "data_fim": "data no formato DD/MM/YYYY"
            }}
        }}

        Contrato:
        {contract_text[:8000]}

        Retorne APENAS o JSON, sem texto adicional.
        """

        try:
            message = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            # Limpar possível markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            data = json.loads(response_text.strip())
            return data

        except Exception as e:
            print(f"Erro ao extrair dados: {e}")
            return self._get_empty_structure(contract_id)

    def _get_empty_structure(self, contract_id: str) -> Dict:
        """Retorna estrutura vazia"""
        return {
            "contract_id": contract_id,
            "arrendador": {},
            "arrendatarios": [],
            "imovel": {},
            "condicoes_economicas": {},
            "duracao": {}
        }

    def flatten_contract_data(self, contract_data: Dict) -> Dict:
        """
        Achata a estrutura hierárquica para formato tabular

        Args:
            contract_data: Dados estruturados do contrato

        Returns:
            Dict achatado
        """
        flattened = {
            "contract_id": contract_data.get("contract_id", ""),

            # Arrendador
            "arrendador_nome": contract_data.get("arrendador", {}).get("nome", ""),
            "arrendador_documento": contract_data.get("arrendador", {}).get("documento", ""),
            "arrendador_endereco": contract_data.get("arrendador", {}).get("endereco", ""),

            # Primeiro arrendatário
            "arrendatario_1_nome": "",
            "arrendatario_1_documento": "",
            "arrendatario_1_endereco": "",

            # Segundo arrendatário (se existir)
            "arrendatario_2_nome": "",
            "arrendatario_2_documento": "",
            "arrendatario_2_endereco": "",

            # Imóvel
            "imovel_endereco": contract_data.get("imovel", {}).get("endereco", ""),
            "imovel_superficie": contract_data.get("imovel", {}).get("superficie", ""),
            "imovel_ref_catastral": contract_data.get("imovel", {}).get("ref_catastral", ""),
            "imovel_tipo": contract_data.get("imovel", {}).get("tipo", ""),

            # Condições econômicas
            "renda_mensal": contract_data.get("condicoes_economicas", {}).get("renda_mensal", ""),
            "gastos_comuns_mensal": contract_data.get("condicoes_economicas", {}).get("gastos_comuns_mensal", ""),
            "gastos_comuns_anual": contract_data.get("condicoes_economicas", {}).get("gastos_comuns_anual", ""),
            "ibi_mensal": contract_data.get("condicoes_economicas", {}).get("ibi_mensal", ""),
            "ibi_anual": contract_data.get("condicoes_economicas", {}).get("ibi_anual", ""),
            "fianca": contract_data.get("condicoes_economicas", {}).get("fianca", ""),

            # Duração
            "prazo": contract_data.get("duracao", {}).get("prazo", ""),
            "data_inicio": contract_data.get("duracao", {}).get("data_inicio", ""),
            "data_fim": contract_data.get("duracao", {}).get("data_fim", ""),
        }

        # Preencher arrendatários
        arrendatarios = contract_data.get("arrendatarios", [])
        if len(arrendatarios) > 0:
            flattened["arrendatario_1_nome"] = arrendatarios[0].get("nome", "")
            flattened["arrendatario_1_documento"] = arrendatarios[0].get("documento", "")
            flattened["arrendatario_1_endereco"] = arrendatarios[0].get("endereco", "")

        if len(arrendatarios) > 1:
            flattened["arrendatario_2_nome"] = arrendatarios[1].get("nome", "")
            flattened["arrendatario_2_documento"] = arrendatarios[1].get("documento", "")
            flattened["arrendatario_2_endereco"] = arrendatarios[1].get("endereco", "")

        return flattened

    def export_to_csv(
        self,
        contracts_data: List[Dict],
        output_file: str = "contratos_exportados.csv"
    ):
        """
        Exporta lista de contratos para CSV

        Args:
            contracts_data: Lista de dados estruturados de contratos
            output_file: Nome do arquivo de saída
        """
        if not contracts_data:
            print("Nenhum dado para exportar")
            return

        # Achatar todos os contratos
        flattened_data = [self.flatten_contract_data(contract) for contract in contracts_data]

        # Criar DataFrame e exportar
        df = pd.DataFrame(flattened_data)
        df.to_csv(output_file, index=False, encoding="utf-8")

        print(f"Exportados {len(contracts_data)} contratos para {output_file}")
        print(f"\nColunas: {list(df.columns)}")

        return df

    def export_to_json(
        self,
        contracts_data: List[Dict],
        output_file: str = "contratos_exportados.json"
    ):
        """
        Exporta contratos para JSON

        Args:
            contracts_data: Lista de dados de contratos
            output_file: Nome do arquivo de saída
        """
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(contracts_data, f, indent=2, ensure_ascii=False)

        print(f"Exportados {len(contracts_data)} contratos para {output_file}")


if __name__ == "__main__":
    # Exemplo de uso
    exporter = CSVExporter()
    print("CSVExporter inicializado")
