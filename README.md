# Mini Warehouse + SQL + ML (DuckDB)

Szkielet repo pod ETL -> SQL -> ML.

## Struktura
- data/raw           # surowe pliki (symulacja GCS)
- data/interim       # dane po wstepnym czyszczeniu
- data/processed     # finalne tabelki/feature store
- warehouse          # plik bazy (DuckDB/SQLite)
- etl                # skrypty ETL
- sql/examples       # przykladowe zapytania SQL
- ml                 # trenowanie i ewaluacja ML
- artifacts          # zapisany model/raporty

## Jak dalej dzialac
1) Uzupelnij skrypty w etl/ i ml/.
2) Dodaj male sample CSV do data/raw/.
3) Commit & push.
