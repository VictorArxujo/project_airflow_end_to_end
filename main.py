import logging
from pathlib import Path
from dotenv import load_dotenv

from pipelines.current.extract import extract_current
from pipelines.current.transform import transform_current
from pipelines.current.load import load_current
from pipelines.forecast.extract import extract_forecast
from pipelines.forecast.transform import transform_forecast
from pipelines.forecast.load import load_forecast
from pipelines.pollution.extract import extract_pollution
from pipelines.pollution.transform import transform_pollution
from pipelines.pollution.load import load_pollution

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
load_dotenv(Path(__file__).resolve().parent / "config" / ".env")

CIDADES = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Brasília", "Londrina"]


def escolher_cidade() -> str:
    print("\n=== Cidades disponíveis ===")
    for i, c in enumerate(CIDADES, 1):
        print(f"  {i}. {c}")
    print("  0. Digitar outra cidade")
    escolha = input("\nEscolha o número da cidade: ").strip()
    if escolha == "0":
        return input("Digite o nome da cidade: ").strip()
    try:
        return CIDADES[int(escolha) - 1]
    except (ValueError, IndexError):
        print("Opção inválida, usando Londrina.")
        return "Londrina"


def escolher_pipeline() -> str:
    print("\n=== Pipelines disponíveis ===")
    print("  1. Tempo atual (current)")
    print("  2. Previsão (forecast)")
    print("  3. Poluição (pollution)")
    print("  4. Todos")
    return input("\nEscolha o pipeline: ").strip()


def pipeline(city: str, tipo: str):
    # Contrato: extract → str | transform → list[dict] | load → int
    try:
        if tipo in ("1", "4"):
            logging.info(f"[current] Rodando para {city}")
            collected_at = extract_current(city=city)          # str
            records = transform_current(city=city, collected_at=collected_at)  # list[dict]
            load_current(records=records)                       # int
            print(f"✅ Current concluído para {city}")

        if tipo in ("2", "4"):
            logging.info(f"[forecast] Rodando para {city}")
            collected_at = extract_forecast(city=city)
            records = transform_forecast(city=city, collected_at=collected_at)
            load_forecast(records=records)
            print(f"✅ Forecast concluído para {city}")

        if tipo in ("3", "4"):
            logging.info(f"[pollution] Rodando para {city}")
            collected_at = extract_pollution(city=city)
            records = transform_pollution(city=city, collected_at=collected_at)
            load_pollution(records=records)
            print(f"✅ Pollution concluído para {city}")

    except Exception as e:
        logging.error(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    city = escolher_cidade()
    tipo = escolher_pipeline()
    pipeline(city=city, tipo=tipo)