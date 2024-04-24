from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

# 1. The plant's family Latin name (cannot be empty)
# 2. The plant's genus Latin name (cannot be empty)
# 3. The plant's binomial nomenclature (cannot be empty)
# 4. The plant's English name (can be empty if not available)
# 5. The plant's English common names (return a list of up to three most common names like this: ["name1", "name2", "name3"]. Can be empty if not available.)
# 6. The plant's Chinese name (answer in Chinese, cannot be empty)
# 7. The plant's Chinese common names (return a list of up to three most common names like this: ["name1", "name2", "name3"]. Can be empty if not available.)
# 8. Diseases susceptible to this plant and the binomial nomenclature of related pathogens (cannot be empty, select the two most common, return in a dictionary of key-value
# pairs where the key is the disease and the value is the Latin name of the pathogen, like this: "disease1":"pathogen1".)
# 9. The suitable relative humidity range for cultivating this plant (in %, like "a%-b%".)
# 10. The suitable temperature range in Celsius for cultivating this plant (in Celsius, like "a℃-b℃".)
# 11. The key growth stages for cultivating this plant (select the two most accurate stages from "Germination, Seedling, Vegetative, Budding, Flowering, Pollination and Fertilization, Fruit Development and Seed Formation, Maturity, Dormancy", and create a list like this: ["Stage1", "Stage2"].)
# 12. The type of soil suitable for cultivating this plant (select the two most accurate types from 'Sandy Soil, Silty Soil, Clay Soil, Loamy Soil, Peaty Soil, Chalky Soil, Sandy Loam', and create a list like this: ["SoilType1", "SoilType2"].)
# 13. A brief description of the precautions to take when cultivating this plant.

# family_name: str = Field(title="Family Name", description="The plant's family Latin name (cannot be empty)")
#
# genus_name: str = Field(title="Genus Name", description="The plant's genus Latin name (cannot be empty)")
#
# binomial: str = Field(title="Binomial", description="The plant's binomial nomenclature (cannot be empty)")
#
# en_name: str = Field(title="En Name", description="The plant's English name (can be empty if not available)")
#
# en_common_names: List[str] = Field(title="En Common Names", description="The plant's English common names (return a list of up to three most common names like this: ['name1', 'name2', 'name3']. Can be empty if not available.)")
#
# cn_name: str = Field(title="Cn Name", description="The plant's Chinese name (answer in Chinese, cannot be empty)")
#
# cn_common_names: List[str] = Field(title="Cn Common Names", description="The plant's Chinese common names (return a list of up to three most common names like this: ['name1', 'name2', 'name3']. Can be empty if not available.)")
#
# diseases_and_pathogen: dict = Field(title="Diseases And Pathogen", description="Diseases susceptible to this plant and the binomial nomenclature of related pathogens (cannot be empty, select the two most common, return in a dictionary of key-value pairs where the key is the disease and the value is the Latin name of the pathogen, like this: 'disease1':'pathogen1'.)")
#
# suit_humidity: str = Field(title="Suit Humidity", description="The suitable relative humidity range for cultivating this plant (in %, like 'a%-b%'.)")
#
# suit_temperature: str = Field(title="Suit Temperature", description="The suitable temperature range in Celsius for cultivating this plant (in Celsius, like 'a℃-b℃'.)")
#
# ket_stages: List[str] = Field(title="Ket Stages", description="The key growth stages for cultivating this plant (select the two most accurate stages from 'Germination, Seedling, Vegetative, Budding, Flowering, Pollination and Fertilization, Fruit Development and Seed Formation, Maturity, Dormancy', and create a list like this: ['Stage1', 'Stage2'].)")
#
# suit_soil: str = Field(title="Suit Soil", description="The type of soil suitable for cultivating this plant (select the two most accurate types from 'Sandy Soil, Silty Soil, Clay Soil, Loamy Soil, Peaty Soil, Chalky Soil, Sandy Loam', and create a list like this: ['SoilType1', 'SoilType2'].)")
#
# caution: str = Field(title="Caution", description="A brief description of the precautions to take when cultivating this plant.")

# family_name: str = Field(title="Family Name")
# genus_name: str = Field(title="Genus Name")
# binomial: str = Field(title="Binomial")
# en_name: str = Field(title="En Name")
# en_common_names: List[str] = Field(title="En Common Names")
# cn_name: str = Field(title="Cn Name")
# cn_common_names: List[str] = Field(title="Cn Common Names")
# diseases_and_pathogen: dict = Field(title="Diseases And Pathogen")
# suit_humidity: str = Field(title="Suit Humidity")
# suit_temperature: str = Field(title="Suit Temperature")
# ket_stages: List[str] = Field(title="Ket Stages")
# suit_soil: str = Field(title="Suit Soil")
# caution: str = Field(title="Caution")


class PlantIntel(BaseModel):

    family_name: str = Field(
        title="Family Name", examples=["Poaceae"], description="cannot be empty"
    )

    genus_name: str = Field(
        title="Genus Name", examples=["Zea"], description="cannot be empty"
    )

    binomial: str = Field(
        title="Binomial", examples=["Zea mays"], description="cannot be empty"
    )

    en_name: str = Field(
        title="En Name", examples=["Corn"], description="can be empty if not available"
    )

    en_common_names: List[str] = Field(
        title="En Common Names",
        examples=[["Maize", "Sweetcorn", "Field corn"]],
        description="return a list of up to three most common names like this: ['name1', 'name2', 'name3']. Can be empty if not available.",
    )

    cn_name: str = Field(
        title="Cn Name",
        examples=["玉米"],
        description="answer in Chinese, cannot be empty",
    )

    cn_common_names: List[str] = Field(
        title="Cn Common Names",
        examples=[["玉米", "甜玉米", "玉米谷"]],
        description="return a list of up to three most common names like this: ['name1', 'name2', 'name3']. Can be empty if not available.",
    )

    diseases_and_pathogen: dict = Field(
        title="Diseases And Pathogen",
        examples=[
            {"Disease1": "Pathogen1", "Disease2": "Pathogen2", "Disease3": "Pathogen3"}
        ],
        description="cannot be empty, select the three most common diseases for this plant, return in a dictionary of key-value pairs where the key is the disease and the value is the Latin name of the pathogen, like this: 'disease1':'pathogen1'.",
    )

    suit_humidity: str = Field(
        title="Suit Humidity", examples=["50%-80%"], description="in %, like 'a%-b%'."
    )

    suit_temperature: str = Field(
        title="Suit Temperature",
        examples=["20℃-30℃"],
        description="in Celsius, like 'a℃-b℃'.",
    )

    ket_stages: List[str] = Field(
        title="Ket Stages",
        examples=[["Stage1", "Stage2", "Stage3"]],
        description="Choose three most suitable stages only from these items: 'Germination, Seedling, Vegetative, Budding, Flowering, Pollination and Fertilization, Fruit Development and Seed Formation, Maturity, Dormancy'. And create a 3-entry list with chosen items like this: ['Stage1', 'Stage2', 'Stage3'].",
    )

    suit_soil: List[str] = Field(
        title="Suit Soil",
        examples=[["SoilType1", "SoilType2", "SoilType3"]],
        description="Choose three most suitable types only from these items: 'Sandy Soil, Silty Soil, Clay Soil, Loamy Soil, Peaty Soil, Chalky Soil, Sandy Loam'. And create a 3-entry list with chosen items like this: ['SoilType1', 'SoilType2', 'SoilType3'].",
    )

    caution: str = Field(
        title="Caution",
        description="A brief description of the precautions to take when cultivating this plant.",
    )

    def to_dict(self):
        return {
            "family_name": self.family_name,
            "genus_name": self.genus_name,
            "binomial": self.binomial,
            "en_name": self.en_name,
            "en_common_names": self.en_common_names,
            "cn_name": self.cn_name,
            "cn_common_names": self.cn_common_names,
            "diseases_and_pathogen": self.diseases_and_pathogen,
            "suit_humidity": self.suit_humidity,
            "suit_temperature": self.suit_temperature,
            "ket_stages": self.ket_stages,
            "suit_soil": self.suit_soil,
            "caution": self.caution,
        }


plant_intel_parser: PydanticOutputParser = PydanticOutputParser(
    pydantic_object=PlantIntel
)

# 1. Family Name. The pathogen's family Latin name (cannot be empty)
# 2. Genus Name. The pathogen's genus Latin name (cannot be empty)
# 3. Binomial. The pathogen's binomial nomenclature (cannot be empty)
# 4. Cn Family Name. The pathogen's family Chinese name (answer in Chinese, cannot be empty)
# 5. Cn Genus Name. The pathogen's genus genus name (answer in Chinese, cannot be empty)
# 6. Cn Name. The pathogen's formal Chinese name (answer in Chinese, cannot be empty)


class PathogenIntel(BaseModel):
    binomial: str = Field(
        description="The pathogen's binomial nomenclature (cannot be empty)"
    )
    family_name: str = Field(
        description="The pathogen's family Latin name (cannot be empty)"
    )
    genus_name: str = Field(
        description="The pathogen's genus Latin name (cannot be empty)"
    )
    cn_family_name: str = Field(
        description="The pathogen's family Chinese name (answer in Chinese, cannot be empty)"
    )
    cn_genus_name: str = Field(
        description="The pathogen's genus genus name (answer in Chinese, cannot be empty)"
    )
    cn_name: str = Field(
        description="The pathogen's formal Chinese name (answer in Chinese, cannot be empty)"
    )

    def to_dict(self):
        return {
            "binomial": self.binomial,
            "family_name": self.family_name,
            "genus_name": self.genus_name,
            "cn_family_name": self.cn_family_name,
            "cn_genus_name": self.cn_genus_name,
            "cn_name": self.cn_name,
        }


pathogen_intel_parser: PydanticOutputParser = PydanticOutputParser(
    pydantic_object=PathogenIntel
)
