import json

from neo4j import GraphDatabase
from .extracter import add_pathogen
from django.conf import settings

from .output_parsers import PathogenIntel


# 定义一个函数用于创建Neo4j事务
def create_neo4j_transaction():
    driver = GraphDatabase.driver(
        settings.NEO4J_URL, auth=("neo4j", settings.NEO4J_PASSWORD)
    )
    return driver.session()


def create_crop(tx, crop_data):
    try:
        # 创建 Crop 节点
        tx.run(
            "MERGE (c:Crop {Binomial: $Binomial, EnglishName: $EnglishName, "
            "EnglishCommonNames: $EnglishCommonNames, ChineseName: $ChineseName, "
            "ChineseCommonNames: $ChineseCommonNames, SuitHumidity: $SuitHumidity, "
            "SuitTemperature: $SuitTemperature, Caution: $Caution})",
            Binomial=crop_data["binomial"],
            EnglishName=crop_data["en_name"],
            EnglishCommonNames=crop_data["en_common_names"],
            ChineseName=crop_data["cn_name"],
            ChineseCommonNames=crop_data["cn_common_names"],
            SuitHumidity=crop_data["suit_humidity"],
            SuitTemperature=crop_data["suit_temperature"],
            Caution=crop_data["caution"],
        )

        # 连接到 Genus
        tx.run(
            "MATCH (c:Crop {Binomial: $Binomial}), "
            "(g:Genus {GenusName: $GenusName}) "
            "MERGE (c)-[:BELONGS_TO]->(g)",
            Binomial=crop_data["binomial"],
            GenusName=crop_data["genus_name"],
        )

        # 连接到 SoilType 和 GrowthStages
        for soil in crop_data["suit_soil"]:
            tx.run(
                "MATCH (c:Crop {Binomial: $Binomial}), "
                "(s:SoilType {Name: $Name}) "
                "MERGE (c)-[:SUITABLE_FOR]->(s)",
                Binomial=crop_data["binomial"],
                Name=soil,
            )

        for stage in crop_data["ket_stages"]:
            tx.run(
                "MATCH (c:Crop {Binomial: $Binomial}), "
                "(g:GrowthStages {Stage: $Stage}) "
                "MERGE (c)-[:HAS_KEY_STAGE]->(g)",
                Binomial=crop_data["binomial"],
                Stage=stage,
            )

        # 检查并连接 Pathogens
        for disease, pathogen in crop_data["diseases_and_pathogen"].items():
            result = tx.run(
                "OPTIONAL MATCH (p:Pathogen {Binomial: $Binomial}) "
                "RETURN p IS NOT NULL as exists",
                Binomial=pathogen,
            )
            exists = result.single()[0]
            if not exists:
                pathogen_data = add_pathogen(pathogen)

                if isinstance(pathogen_data, PathogenIntel):
                    pathogen_dict = pathogen_data.to_dict()
                elif isinstance(pathogen_data, str):
                    # 如果是字符串，你可以将其解析为字典
                    try:
                        pathogen_dict = json.loads(pathogen_data)
                    except json.JSONDecodeError:
                        # 处理解析失败的情况
                        pathogen_dict = {}
                else:
                    # 处理其他情况
                    pathogen_dict = {}
                create_pathogen_nodes(tx, pathogen_dict)

                tx.run(
                    "MATCH (c:Crop {Binomial: $CropBinomial}) "
                    "MATCH (p:Pathogen {Binomial: $PathogenBinomial}) "
                    "MERGE (c)-[r:SUSCEPTIBLE_TO {disease: $Disease}]->(p)",
                    CropBinomial=crop_data["binomial"],
                    PathogenBinomial=pathogen,
                    Disease=disease,
                )
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")


def create_pathogen_nodes(tx, pathogen_data):
    try:
        # 创建或匹配 Family 节点
        tx.run(
            "MERGE (f:Family {FamilyName: $FamilyName, ChineseFamilyName: $ChineseFamilyName})",
            FamilyName=pathogen_data["family_name"],
            ChineseFamilyName=pathogen_data["cn_family_name"],
        )

        # 创建或匹配 Genus 节点
        tx.run(
            "MERGE (g:Genus {GenusName: $GenusName, ChineseGenusName: $ChineseGenusName})",
            GenusName=pathogen_data["genus_name"],
            ChineseGenusName=pathogen_data["cn_genus_name"],
        )

        # 创建或匹配 Pathogen 节点
        tx.run(
            "MERGE (p:Pathogen {Binomial: $Binomial, ChineseName: $ChineseName})",
            Binomial=pathogen_data["binomial"],
            ChineseName=pathogen_data["cn_name"],
        )

        # 建立关系（如果需要的话）
        tx.run(
            "MATCH (f:Family {FamilyName: $FamilyName}), (g:Genus {GenusName: $GenusName}), (p:Pathogen {Binomial: $Binomial}) "
            "MERGE (p)-[:BELONGS_TO]->(g) "
            "MERGE (g)-[:PART_OF]->(f)",
            FamilyName=pathogen_data["family_name"],
            GenusName=pathogen_data["genus_name"],
            Binomial=pathogen_data["binomial"],
        )

    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")


# 创建或更新 Genus 和 Family 节点，并建立它们之间的 PART_OF 关系
def create_genus_family_in_neo4j(tx, crop):
    try:
        tx.run(
            """
            MERGE (f:Family {FamilyName: $family_name, ChineseFamilyName: $chinese_family_name})
            MERGE (g:Genus {GenusName: $genus_name, ChineseGenusName: $chinese_genus_name})
            MERGE (g)-[:PART_OF]->(f)
            """,
            {
                "family_name": crop.family_name,
                "chinese_family_name": crop.chinese_family_name,
                "genus_name": crop.genus_name,
                "chinese_genus_name": crop.chinese_genus_name,
            },
        )
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")


def query_dict(tx, plant):
    try:
        cypher_query = """
        MATCH (c:Crop {Binomial: $binomial})
        OPTIONAL MATCH (c)-[:BELONGS_TO]->(g:Genus)
        OPTIONAL MATCH (g)-[:PART_OF]->(f:Family)
        OPTIONAL MATCH (c)-[:SUITABLE_FOR]->(s:SoilType)
        OPTIONAL MATCH (c)-[:HAS_KEY_STAGE]->(st:GrowthStages)
        OPTIONAL MATCH (c)-[r:SUSCEPTIBLE_TO]->(p:Pathogen)
        RETURN
            c.Binomial AS binomial,
            c.EnglishName AS en_name,
            c.EnglishCommonNames AS en_common_names,
            c.ChineseName AS cn_name,
            c.ChineseCommonNames AS cn_common_names,
            c.SuitHumidity AS suit_humidity,
            c.SuitTemperature AS suit_temperature,
            c.Caution AS caution,
            f.FamilyName AS family_name,
            g.GenusName AS genus_name,
            COLLECT(s.Name) AS suit_soil,
            COLLECT(st.Stage) AS ket_stages,
            COLLECT({disease: r.disease, pathogen: p.Binomial}) AS diseases_and_pathogen
        """
        result = tx.run(cypher_query, {"binomial": plant})

        # Check if there are any records in the result
        for record in result:
            data = {
                "binomial": record["binomial"],
                "en_name": record["en_name"],
                "en_common_names": record["en_common_names"],
                "cn_name": record["cn_name"],
                "cn_common_names": record["cn_common_names"],
                "suit_humidity": record["suit_humidity"],
                "suit_temperature": record["suit_temperature"],
                "caution": record["caution"],
                "family_name": record["family_name"],
                "genus_name": record["genus_name"],
                "suit_soil": record["suit_soil"],
                "ket_stages": record["ket_stages"],
                "diseases_and_pathogen": record["diseases_and_pathogen"],
            }

            return data

        # If no records were found, return an appropriate message
        return "Crop does not exist or an error occurred."

    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")
