"""
EXEMPLO DE USO DO SISTEMA DE DIAGNÓSTICO CONDOMINIAL
Demonstra como carregar documentos e executar análise RAG
"""

import json
from diagnostico.chunking import chunk_convencao, chunk_norma, chunk_ata, chunk_contrato
from diagnostico.database import CondominioDatabase
from diagnostico.extractor import CondominioExtractor


def exemplo_completo():
    """Exemplo completo de uso do sistema"""

    print("="*60)
    print("SISTEMA DE DIAGNÓSTICO JURÍDICO CONDOMINIAL")
    print("RAG + ChromaDB + Claude AI")
    print("="*60)

    # 1. Inicializar banco de dados
    print("\n1️⃣  Inicializando ChromaDB...")
    db = CondominioDatabase(persist_directory="./chromadb_data")

    # 2. Exemplo de Convenção de Condomínio
    convencao_exemplo = """
CONVENÇÃO DO CONDOMÍNIO RESIDENCIAL EXEMPLO

TÍTULO I - DA CONSTITUIÇÃO E FINALIDADE

Art. 1º - O Condomínio Residencial Exemplo, inscrito no CNPJ 12.345.678/0001-90,
situado na Rua das Flores, nº 123, São Paulo/SP, CEP 01234-567, Matrícula nº 54.321
do 1º Registro de Imóveis, rege-se pela presente Convenção.

Art. 2º - O condomínio é composto por 80 unidades autônomas distribuídas em 4 blocos.

Art. 3º - As frações ideais são proporcionais à área privativa de cada unidade.

TÍTULO II - DA ADMINISTRAÇÃO

Art. 4º - A administração será exercida por um Síndico, eleito em Assembleia Geral
para mandato de 2 anos.

Art. 5º - Compete ao Síndico:
I - Representar o condomínio judicial e extrajudicialmente
II - Executar as deliberações da Assembleia
III - Prestar contas mensalmente

Art. 6º - As Assembleias Gerais Ordinárias realizar-se-ão anualmente no mês de março.

Art. 7º - O quórum para instalação em primeira convocação é de 2/3 dos condôminos.

TÍTULO III - DO USO E CONVIVÊNCIA

Art. 8º - É vedado o uso das unidades para atividades comerciais.

Art. 9º - As áreas comuns compreendem: salão de festas, piscina, playground,
quadra poliesportiva e sala de ginástica.

Art. 10º - A utilização do salão de festas depende de reserva prévia.

TÍTULO IV - DAS CONTRIBUIÇÕES E PENALIDADES

Art. 11º - As despesas ordinárias serão rateadas mensalmente entre os condôminos.

Art. 12º - O não pagamento das contribuições no prazo acarretará multa de 2%
e juros de 1% ao mês.

Art. 13º - O condômino que infringir normas da convenção estará sujeito a:
I - Advertência por escrito
II - Multa de até 5 vezes o valor da contribuição mensal
III - Suspensão do direito de uso das áreas comuns

Art. 14º - A aplicação de penalidades observará o princípio da proporcionalidade.
"""

    # 3. Processar e inserir convenção
    print("\n2️⃣  Processando convenção com chunking...")
    chunks_convencao = chunk_convencao(
        convencao_exemplo,
        metadata={
            "data_registro": "2020-01-15",
            "versao": "1.0"
        }
    )

    print(f"   ✓ Gerados {len(chunks_convencao)} chunks")

    print("\n3️⃣  Inserindo no ChromaDB...")
    db.add_chunks(
        chunks=chunks_convencao,
        condominio_id="COND_001",
        document_name="convencao_2020"
    )

    # 4. Adicionar exemplo de Regimento Interno
    regimento_exemplo = """
REGIMENTO INTERNO - CONDOMÍNIO RESIDENCIAL EXEMPLO

CAPÍTULO I - DAS DISPOSIÇÕES GERAIS

Art. 1º - Este regimento complementa a Convenção do Condomínio.

CAPÍTULO II - DO USO DAS ÁREAS COMUNS

Art. 2º - O horário de uso da piscina é das 8h às 22h.

Art. 3º - Crianças menores de 12 anos devem estar acompanhadas.

Art. 4º - É proibido som alto após as 22h.

CAPÍTULO III - DAS RESERVAS

Art. 5º - O salão de festas pode ser reservado com 30 dias de antecedência.

Art. 6º - Cada unidade tem direito a 2 reservas por mês.

Art. 7º - Taxa de limpeza: R$ 200,00

CAPÍTULO IV - DE ANIMAIS DE ESTIMAÇÃO

Art. 8º - São permitidos animais de pequeno porte.

Art. 9º - Obrigatório uso de coleira nas áreas comuns.

Art. 10º - Proprietário responde por danos causados pelo animal.
"""

    print("\n4️⃣  Processando regimento interno...")
    chunks_regimento = chunk_norma(
        regimento_exemplo,
        metadata={"tipo": "regimento_interno", "ano": 2021}
    )

    db.add_chunks(
        chunks=chunks_regimento,
        condominio_id="COND_001",
        document_name="regimento_interno_2021"
    )

    # 5. Adicionar exemplo de Ata de Assembleia
    ata_exemplo = """
ATA DA ASSEMBLEIA GERAL ORDINÁRIA
Condomínio Residencial Exemplo
Data: 15/03/2024

Às 19h do dia 15 de março de 2024, reuniram-se em Assembleia Geral Ordinária
os condôminos do Residencial Exemplo.

PAUTA:
1. Prestação de contas do exercício 2023
2. Eleição do novo síndico
3. Aprovação de obras de manutenção

DELIBERAÇÕES:

1. As contas foram aprovadas por unanimidade (80 votos favoráveis).

2. Eleito como novo síndico o Sr. João Silva (70 votos), para mandato de 2024-2026.

3. Aprovada obra de reforma da piscina no valor de R$ 50.000,00,
com 65 votos favoráveis e 15 contrários.

4. Aprovado aumento de 10% na taxa condominial para cobrir despesas de manutenção.

Encerramento às 21h30.
"""

    print("\n5️⃣  Processando ata de assembleia...")
    chunks_ata = chunk_ata(
        ata_exemplo,
        metadata={"data": "2024-03-15", "tipo": "assembleia_ordinaria"}
    )

    db.add_chunks(
        chunks=chunks_ata,
        condominio_id="COND_001",
        document_name="ata_assembleia_2024_03"
    )

    # 6. Estatísticas do banco
    print("\n6️⃣  Estatísticas do banco de dados:")
    stats = db.get_statistics()
    for collection, count in stats.items():
        print(f"   {collection}: {count} chunks")

    # 7. Testar busca semântica
    print("\n7️⃣  Testando busca semântica RAG...")
    print("\n   Query: 'Quais são as penalidades previstas?'")

    resultados = db.search(
        query="Quais são as penalidades previstas?",
        condominio_id="COND_001",
        n_results=3
    )

    for i, resultado in enumerate(resultados):
        print(f"\n   Resultado {i+1}:")
        print(f"   Tipo: {resultado['metadata']['doc_type']}")
        print(f"   Documento: {resultado['metadata']['document_name']}")
        print(f"   Conteúdo: {resultado['content'][:200]}...")

    # 8. Executar extração com Claude AI
    print("\n8️⃣  Executando diagnóstico com Claude AI...")
    print("   (Requer ANTHROPIC_API_KEY configurada)\n")

    extractor = CondominioExtractor(db)

    # Diagnóstico completo
    resultado = extractor.diagnostico_completo(
        condominio_id="COND_001",
        objetivo="REVISAO_CONFORMIDADE"
    )

    # 9. Salvar resultado
    output_file = "diagnostico_resultado.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print(f"\n9️⃣  Resultado salvo em: {output_file}")

    # 10. Exibir resumo
    print("\n"+"="*60)
    print("RESUMO DO DIAGNÓSTICO")
    print("="*60)

    if "error" not in resultado:
        # Fase 1
        if "fase1_identificacao" in resultado["fases"]:
            fase1 = resultado["fases"]["fase1_identificacao"]
            if "identificacao_registral" in fase1:
                print("\n📋 IDENTIFICAÇÃO:")
                print(f"   Denominação: {fase1['identificacao_registral'].get('denominacao', 'N/A')}")
                print(f"   CNPJ: {fase1['identificacao_registral'].get('cnpj', 'N/A')}")

        # Fase 2
        if "fase2_mapeamento" in resultado["fases"]:
            fase2 = resultado["fases"]["fase2_mapeamento"]
            if "problemas_identificados" in fase2:
                problemas = fase2["problemas_identificados"]
                print("\n⚠️  PROBLEMAS IDENTIFICADOS:")
                if problemas.get("conflitos_normativos"):
                    print(f"   Conflitos: {len(problemas['conflitos_normativos'])}")
                if problemas.get("lacunas"):
                    print(f"   Lacunas: {len(problemas['lacunas'])}")

        # Fase 3
        if "fase3_conformidade" in resultado["fases"]:
            fase3 = resultado["fases"]["fase3_conformidade"]
            if "problemas_criticos" in fase3:
                print(f"\n🔴 PROBLEMAS CRÍTICOS: {len(fase3['problemas_criticos'])}")
                for problema in fase3["problemas_criticos"]:
                    print(f"   - {problema}")

    print("\n"+"="*60)
    print("✅ Diagnóstico concluído com sucesso!")
    print("="*60+"\n")


def exemplo_busca_simples():
    """Exemplo simplificado de busca RAG"""

    print("\n" + "="*60)
    print("EXEMPLO DE BUSCA RAG SIMPLES")
    print("="*60 + "\n")

    db = CondominioDatabase()

    # Listar documentos disponíveis
    print("📚 Documentos no banco:")
    docs = db.list_documents(condominio_id="COND_001")
    for doc in docs:
        print(f"   - {doc['document_name']} ({doc['doc_type']})")

    # Buscar informações específicas
    print("\n🔍 Buscando: 'mandato do síndico'")
    results = db.search(
        query="mandato do síndico",
        condominio_id="COND_001",
        n_results=2
    )

    for i, result in enumerate(results):
        print(f"\n   Resultado {i+1}:")
        print(f"   {result['content']}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "simples":
        exemplo_busca_simples()
    else:
        exemplo_completo()
