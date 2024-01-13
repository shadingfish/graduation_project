# 目前我的Neo4j数据库里有这几个节点
# 1.Crop
# 属性	数据类型	描述	示例值
# ID	INT	唯一标识符	1, 2, 3...
# Binomial STRING	拉丁文二名	"Vaccinium corymbosum"
# EnglishName 英文名"Blueberry"
# EnglishCommonNames 英文常见名 List[str] ["Blueberry", "Huckleberry", "Whortleberry"]
# ChineseName	STRING	中文名	"蓝莓"
# ChineseCommonNames List[str] 中文常见名 ["蓝莓", "越橘", "越橘莓"]
# SuitHumidity	STRING	适宜湿度	"40%-60%"
# SuitTemperature	STRING	适宜温度	"15°C-25°C"
# Caution	STRING	特别注 意事项	"需避免过量灌溉", "需防治稻瘟病"
#
# 2. Family
# FamilyName 拉丁文科名
# ChineseFamilyName 中文科名
#
# 3.Genus
# GenusName 拉丁文科名
# ChineseGenusName 中文科名
#
# 4.Pathogen
# Bnomial STRING	拉丁文二名	"Monilinia vaccinii-corymbosi"
# ChineseName STRING	 中文名
#
# 5. SoilType
# 两个字段，中英文的土壤类型名，总共只有下列值：'Sandy Soil, Silty Soil, Clay Soil, Loamy Soil, Peaty Soil, Chalky Soil, Sandy Loam'
#
# 6. GrowthStages
# 两个字段，中英文的生长阶段名，总共只有下列值：'Germination, Seedling, Vegetative, Budding, Flowering, Pollination and Fertilization, Fruit Development and Seed Formation, Maturity, Dormancy'
#
#
# 我从GPT里询问得到的数据是这样的：
# {"family_name": "Ericaceae", "genus_name": "Vaccinium", "binomial": "Vaccinium corymbosum", "en_name": "Blueberry", "en_common_names": ["Blueberry", "Huckleberry", "Whortleberry"], "cn_name": "蓝莓", "cn_common_names": ["蓝莓", "越橘", "越橘莓"], "diseases_and_pathogen": {"Blueberry Scorch": "Blueberry scorch virus", "Mummy Berry": "Monilinia vaccinii-corymbosi", "Phomopsis Twig Blight": "Phomopsis vaccinii"}, "suit_humidity": "40%-60%", "suit_temperature": "15°C-25°C", "ket_stages": ["Germination", "Vegetative", "Flowering"], "suit_soil": ["Sandy Soil", "Loamy Soil", "Sandy Loam"], "caution": "Protect from birds and other animals that may eat the berries."}
#
# 我该怎么初始化Neo4j，并把这个数据保存到neo4j里
