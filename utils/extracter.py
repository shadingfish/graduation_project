from langchain_core.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import LLMChain
import json
from .output_parsers import (
    plant_intel_parser,
    PlantIntel,
    pathogen_intel_parser,
    PathogenIntel,
)

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")


def parse_output(output):
    lines = output.split("\n")
    data = {}

    # 普通字段的解析
    data["family_name"] = lines[0].split(". ")[1].strip()
    data["genus_name"] = lines[1].split(". ")[1].strip()
    data["binomial"] = lines[2].split(". ")[1].strip()
    data["en_name"] = lines[3].split(". ")[1].strip()

    # 处理单引号的问题，并解析字符串表示的列表和字典
    data["en_common_names"] = json.loads(
        lines[4].split(". ", 1)[1].replace("'", '"').strip()
    )
    data["cn_name"] = lines[5].split(". ")[1].strip()
    data["cn_common_names"] = json.loads(
        lines[6].split(". ", 1)[1].replace("'", '"').strip()
    )
    data["diseases_and_pathogen"] = json.loads(
        lines[7].split(". ", 1)[1].replace("'", '"').strip()
    )
    data["suit_humidity"] = lines[8].split(". ")[1].strip()
    data["suit_temperature"] = lines[9].split(". ")[1].strip()
    data["ket_stages"] = json.loads(
        lines[10].split(". ", 1)[1].replace("'", '"').strip()
    )
    data["suit_soil"] = json.loads(
        lines[11].split(". ", 1)[1].replace("'", '"').strip()
    )
    data["caution"] = json.loads(lines[12].split(". ", 1)[1].replace("'", '"').strip())

    return data


def judge(word: str) -> str:
    judge_template = """Please help me determine if the word {word} is a plant species. I want your answer to be only
    a word. If it is, please return exactly the word 'yes'. If it is not, please return exactly the word 'no'"""

    judge_prompt_template = PromptTemplate(
        input_variables=["word"],
        template=judge_template,
    )

    chain = LLMChain(llm=llm, prompt=judge_prompt_template)
    chain_result = chain.run(word=word)
    return chain_result


def extract(plant: str) -> str or PlantIntel:
    print("In asking Langchain about information of " + plant)
    extract_template = """
    Firstly, please help me determine if the word {plant} is a plant. For example "Rock" is not a plant. "Tobacco", "banana" and "Triticum aestivum" are all plants.
    Plants named using binomial nomenclature always meet the input requirements, so you must process such plants.
    
    If it is not, please return exactly the word 'no'. If it is, please implement following steps.
    
    Please provide information about the plant {plant}. Combine the {format_instruction} and following instruction to construct your answer.
    You should only give the answer to each item without introduction sentence like "The plant's family Latin name:" ot title like "Genus Name:".
    Don't give me an answer with items like "properties", "description" and "examples". Just give me a clean answer in the format of given examples in {format_instruction}.
    Remember that examples are just for your reference to get right format and accurate answer should be case-specific.
    The return content should be a dictionary, not a dictionary string.
    Following 13 items are the data fields you need to include.
    
    1. Family Name: The plant's family Latin name
    2. Genus Name: The plant's genus Latin name
    3. Binomial: The plant's binomial nomenclature
    4. En Name: The plant's English name
    5. En Common Names: The plant's English common names
    6. Cn Name: The plant's Chinese name
    7. Cn Common Names: The plant's Chinese common names
    8. Diseases And Pathogen: Three diseases most susceptible to this plant and the binomial nomenclature of related pathogens
    9. Suit Humidity: The suitable relative humidity range for cultivating this plant
    10. Suit Temperature: The suitable temperature range in Celsius for cultivating this plant
    11. Ket Stages: The key growth stages for cultivating this plant. Select three most suitable stages only from these items: 'Germination, Seedling, Vegetative, Budding, Flowering, Pollination and Fertilization, Fruit Development and Seed Formation, Maturity, Dormancy' to create a 3-entry list.
    12. Suit Soil: The type of soil suitable for cultivating this plant. Select three most suitable types only from these items: 'Sandy Soil, Silty Soil, Clay Soil, Loamy Soil, Peaty Soil, Chalky Soil, Sandy Loam'  to create a 3-entry list.
    13. Caution: A brief description of the precautions to take when cultivating this plant
    
    """
    # \n{format_instruction}

    extract_prompt_template = PromptTemplate(
        input_variables=["plant"],
        template=extract_template,
        partial_variables={
            "format_instruction": plant_intel_parser.get_format_instructions()
        },
    )

    chain = LLMChain(llm=llm, prompt=extract_prompt_template)
    chain_result = chain.run(plant=plant)
    print(chain_result)
    return chain_result


def add_pathogen(patho: str) -> PathogenIntel:
    add_pathogen_template = """
    Please provide the following information about the pathogen {pathogen}, with the content in parentheses indicating the context you need to consider. You should only give the answer to each item without introductive sentence like "The pathogen's family Latin name:".
    
    \n{format_instruction}
    
    The return content should be a dictionary, not a dictionary string.
    """

    add_pathogen_prompt_template = PromptTemplate(
        input_variables=["pathogen"],
        template=add_pathogen_template,
        partial_variables={
            "format_instruction": pathogen_intel_parser.get_format_instructions()
        },
    )

    chain = LLMChain(llm=llm, prompt=add_pathogen_prompt_template)
    chain_result = chain.run(pathogen=patho)
    print("chain_result")
    print(chain_result)
    return chain_result


if __name__ == "__main__":
    print("Hello LangChain!")
    result = extract(plant="blueberry")
    if result == "no" or len(result) < 50:
        print("The given word is not a plant. Result: " + result)
    else:
        # result = parse_output(result)
        print(result)

    # result = add_pathogen(patho='Exserohilum turcicum')
    # print("result")
    # print(result)

# {"family_name": "Ericaceae", "genus_name": "Vaccinium", "binomial": "Vaccinium corymbosum", "en_name": "Blueberry", "en_common_names": ["Blueberry", "Huckleberry", "Whortleberry"], "cn_name": "蓝莓", "cn_common_names": ["蓝莓", "越橘", "越橘莓"], "diseases_and_pathogen": {"Blueberry Scorch": "Blueberry scorch virus", "Mummy Berry": "Monilinia vaccinii-corymbosi", "Phomopsis Twig Blight": "Phomopsis vaccinii"}, "suit_humidity": "40%-60%", "suit_temperature": "15°C-25°C", "ket_stages": ["Germination", "Vegetative", "Flowering"], "suit_soil": ["Sandy Soil", "Loamy Soil", "Sandy Loam"], "caution": "Protect from birds and other animals that may eat the berries."}
