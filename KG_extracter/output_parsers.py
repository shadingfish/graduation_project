from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List


class PlantIntel(BaseModel):
    family_name: str = Field(examples=['Poaceae'], description="Item 1. The plant's family Latin name")
    genus_name: str = Field(examples=['Zea'], description="Item 2. The plant's genus Latin name")
    binomial: str = Field(examples=['Zea mays'], description="Item 3. The plant's species name in binomial nomenclature")
    en_name: str = Field(examples=['Corn'], description="Item 4. The plant's English name")
    en_common_names: List[str] = Field(examples=[['Maize', 'Sweetcorn', 'Field corn']], description="Item 5. A str list of the plant's English common names")
    cn_name: str = Field(examples=['玉米'], description="Item 6. The plant's Chinese name")
    cn_common_names: List[str] = Field(examples=[['玉米', '甜玉米', '玉米谷']], description="Item 7. A list of the plant's Chinese common names")
    diseases_and_pathogen: dict = Field(examples=[{"Northern corn leaf blight": "Exserohilum turcicum", "Gray leaf spot": "Cercospora zeae-maydis"}], description="Item 8. A key-value pair dict of selected diseases susceptible to this plant and the related pathogens named in binomial nomenclature")
    suit_humidity: str = Field(examples=["50%-80%"], description="Item 9. The suitable relative humidity range for cultivating this plant")
    suit_temperature: str = Field(examples=["20℃-30℃"], description="Item 10. The suitable temperature range in Celsius for cultivating this plant")
    ket_stages: List[str] = Field(examples=[['Germination', 'Vegetative']], description="Item 11. A list of selected key growth stages for cultivating this plant")
    suit_soil: str = Field(examples=[['Loamy Soil', 'Sandy Loam']], description="Item 12. A list of selected types of soil suitable for cultivating this plant")
    # family_name: str = Field(description="Item 1. The plant's family Latin name")
    # genus_name: str = Field(description="Item 2. The plant's genus Latin name")
    # binomial: str = Field(description="Item 3. The plant's species name in binomial nomenclature")
    # en_name: str = Field(description="Item 4. The plant's English name")
    # en_common_names: List[str] = Field(description="Item 5. A str list of the plant's English common names")
    # cn_name: str = Field(description="Item 6. The plant's Chinese name")
    # cn_common_names: List[str] = Field(description="Item 7. A list of the plant's Chinese common names")
    # diseases_and_pathogen: dict = Field(description="Item 8. A key-value pair dict of selected diseases susceptible to this plant and the related pathogens named in binomial nomenclature")
    # suit_humidity: str = Field(description="Item 9. The suitable relative humidity range for cultivating this plant")
    # suit_temperature: str = Field(description="Item 10. The suitable temperature range in Celsius for cultivating this plant")
    # ket_stages: List[str] = Field(description="Item 11. A list of selected key growth stages for cultivating this plant")
    # suit_soil : str = Field(description="Item 12. A list of selected types of soil suitable for cultivating this plant")
    
    
    # family_name: str = Field(description="The plant's family Latin name")
    # genus_name: str = Field(description="The plant's genus Latin name")
    # binomial: str = Field(description="The plant's species name in binomial nomenclature")
    # en_name: str = Field(description="The plant's English name")
    # en_common_names: List[str] = Field(description="A str list of the plant's English common names")
    # cn_name: str = Field(description="6. The plant's Chinese name")
    # cn_common_names: List[str] = Field(description="A list of the plant's Chinese common names")
    # diseases_and_pathogen: dict = Field(description="A key-value pair dict of selected diseases susceptible to this plant and the related pathogens named in binomial nomenclature")
    # suit_humidity: str = Field(description="The suitable relative humidity range for cultivating this plant")
    # suit_temperature: str = Field(description="The suitable temperature range in Celsius for cultivating this plant")
    # ket_stages: List[str] = Field(description="A list of selected key growth stages for cultivating this plant")
    # suit_soil : str = Field(description="A list of selected types of soil suitable for cultivating this plant")

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
            "suit_soil": self.suit_soil
        }


plant_intel_parser: PydanticOutputParser = PydanticOutputParser(
    pydantic_object=PlantIntel
)

