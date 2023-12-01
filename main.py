from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db_connection import connect_to_db
app = FastAPI()

# Добавление CORS middleware для разрешения запросов с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Обработчик для получения статуса производства по регионам
@app.get("/get_production_status_by_region")
def get_production_status_by_region():
    # Установка соединения с базой данных
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            # SQL запрос для статистики производства по регионам
            sql = """
            SELECT sr.name AS region_name, 
                   SUM(CASE WHEN cc.id_status = 1 THEN 1 ELSE 0 END) AS open_count,
                   SUM(CASE WHEN cc.id_status = 2 THEN 1 ELSE 0 END) AS closed_count,
                   FLOOR(AVG(DATEDIFF(cc.data_close, cc.data_reg)) / 30) AS avg_lifespan
            FROM c_address ca
            INNER JOIN spr_regions sr ON ca.id_gerion = sr.kode_reg
            INNER JOIN c_company cc ON ca.id = cc.id
            GROUP BY sr.name
            """
            # Выполнение запроса
            cursor.execute(sql)
            # Получение результатов
            result = cursor.fetchall()
            # Возвращение данных в формате JSON
            return {"production_status_by_region": result}
    finally:
        # Закрытие соединения с базой данных после выполнения запроса
        connection.close()

# Обработчик для получения компаний по типам тканей
@app.get("/fabric_companies_by_fabric")
def get_fabric_companies():
    # Установка соединения с базой данных
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            # SQL запрос для получения информации о компаниях по типам тканей
            sql = """
            SELECT sv.name AS fabric_name, COUNT(cv.id_vid_tkani) AS company_count
            FROM cs_vid_tkani cv
            INNER JOIN spr_vid_tkani sv ON cv.id_vid_tkani = sv.id
            GROUP BY sv.name
            """
            # Выполнение запроса
            cursor.execute(sql)
            result = cursor.fetchall()
            return {"fabric_companies_data": result}
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        connection.close()
# Обработчик для получения статистики естественного прироста компаний по годам и регионам

@app.get("/natural_growth_by_year_and_region/{region_id}")
def get_natural_growth(region_id):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT sr.name AS region_name,
                   YEAR(cc.data_reg) AS registration_year,
                   SUM(CASE WHEN cc.id_status = 1 THEN 1 ELSE 0 END) AS opened_count,
                   SUM(CASE WHEN cc.id_status = 2 THEN 1 ELSE 0 END) AS closed_count
            FROM c_address ca
            INNER JOIN spr_regions sr ON ca.id_gerion = sr.kode_reg
            INNER JOIN c_company cc ON ca.id = cc.id
            WHERE sr.kode_reg = %s
            GROUP BY sr.name, YEAR(cc.data_reg)
            ORDER BY region_name, registration_year
            """
            cursor.execute(sql, (region_id,))
            result = cursor.fetchall()
            return {"natural_growth_by_year_and_region": result}
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        connection.close()

