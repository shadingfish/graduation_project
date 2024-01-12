from typing import Any
from langchain_core.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import LLMChain
import json
from output_parsers import plant_intel_parser, PlantIntel

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")


def parse_output(output):
    lines = output.split('\n')
    data = {}

    # 普通字段的解析
    data['family_name'] = lines[0].split('. ')[1].strip()
    data['genus_name'] = lines[1].split('. ')[1].strip()
    data['binomial'] = lines[2].split('. ')[1].strip()
    data['en_name'] = lines[3].split('. ')[1].strip()

    # 处理单引号的问题，并解析字符串表示的列表和字典
    data['en_common_names'] = json.loads(lines[4].split('. ', 1)[1].replace("'", "\"").strip())
    data['cn_name'] = lines[5].split('. ')[1].strip()
    data['cn_common_names'] = json.loads(lines[6].split('. ', 1)[1].replace("'", "\"").strip())
    data['diseases_and_pathogen'] = json.loads(lines[7].split('. ', 1)[1].replace("'", "\"").strip())
    data['suit_humidity'] = lines[8].split('. ')[1].strip()
    data['suit_temperature'] = lines[9].split('. ')[1].strip()
    data['ket_stages'] = json.loads(lines[10].split('. ', 1)[1].replace("'", "\"").strip())
    data['suit_soil'] = json.loads(lines[11].split('. ', 1)[1].replace("'", "\"").strip())

    return data

def judge(word: str) -> dict[str, Any]:

    judge_template = """Please help me determine if the word {word} is a plant species. I want your answer to be only
    a word. If it is, please return exactly the word 'yes'. If it is not, please return exactly the word 'no'"""

    judge_prompt_template = PromptTemplate(
        input_variables=["word"],
        template=judge_template,
    )

    chain = LLMChain(llm=llm, prompt=judge_prompt_template)
    chain_result = chain.invoke(input=word)
    return chain_result


def extract(plant: str):

    extract_template = '''
    Please provide the following information about the plant {plant}, with the content in parentheses indicating the context you need to consider. You should only give the answer to each item without introductive sentence like "The plant's family Latin name:".
    
    1. The plant's family Latin name (cannot be empty)
    2. The plant's genus Latin name (cannot be empty)
    3. The plant's binomial nomenclature (cannot be empty)
    4. The plant's English name (can be empty if not available)
    5. The plant's English common names (return a list of up to three most common names like this: ["name1", "name2", "name3"]. Can be empty if not available.)
    6. The plant's Chinese name (answer in Chinese, cannot be empty)
    7. The plant's Chinese common names (return a list of up to three most common names like this: ["name1", "name2", "name3"]. Can be empty if not available.)
    8. Diseases susceptible to this plant and the binomial nomenclature of related pathogens (cannot be empty, select the two most common, return in a dictionary of key-value
    pairs where the key is the disease and the value is the Latin name of the pathogen, like this: "disease1":"pathogen1".)
    9. The suitable relative humidity range for cultivating this plant (in %, like "a%-b%".)
    10. The suitable temperature range in Celsius for cultivating this plant (in Celsius, like "a℃-b℃".)
    11. The key growth stages for cultivating this plant (select the two most accurate stages from "Germination, Seedling, Vegetative, Budding, Flowering, Pollination and Fertilization, Fruit Development and Seed Formation, Maturity, Dormancy", and create a list like this: ["Stage1", "Stage2"].)
    12. The type of soil suitable for cultivating this plant (select the two most accurate types from 'Sandy Soil, Silty Soil, Clay Soil, Loamy Soil, Peaty Soil, Chalky Soil, Sandy Loam', and create a list like this: ["SoilType1", "SoilType2"].)

    '''
    # \n{format_instruction}
    
    judge_prompt_template = PromptTemplate(
        input_variables=["plant"],
        template=extract_template,
        # partial_variables={
        #     "format_instruction": plant_intel_parser.get_format_instructions()
        # },
    )

    chain = LLMChain(llm=llm, prompt=judge_prompt_template)
    chain_result = chain.invoke(input=plant)
    # print(chain_result)
    return chain_result


if __name__ == "__main__":
    print("Hello LangChain!")
    result = parse_output(extract(plant="Nicotiana tabacum")['text'])
    print(result)


