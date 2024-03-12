from dotenv import load_dotenv
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

from utils.store_data import create_neo4j_transaction, query_dict

load_dotenv()
llm = ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0)

response_schema = [
    ResponseSchema(type="list", name="crop", description="作物名称实体"),
    ResponseSchema(type="list", name="pathogen", description="病原体名称实体"),
    ResponseSchema(type="list", name="soil", description="土壤类型名称实体"),
    ResponseSchema(type="list", name="growthStage", description="生长阶段名称实体"),
    ResponseSchema(type="char", name="question_type_code", description="问题类型代码"),
]

output_parser = StructuredOutputParser.from_response_schemas(response_schema)
format_instructions = output_parser.get_format_instructions()

# 以特定的土壤类型实体为重点，询问与其相关的非特定实体，问题类型代码及示例为：
# j: "白垩土适合哪些作物生长?"
#
# 以特定的作物生长阶段实体为重点，询问与其相关的非特定实体，问题类型代码及示例为：
# k: "果实发育和种子形成阶段对哪些作物较为关键？"

template = """
1.根据后续[]中的内容，了解不同类型问题的问题类型代码，问题类型代码是一个字符串,其值为a-n中任意一个字母或者为x。
[只关注于一种主要实体(代码a-k)
以特定的作物实体为重点，询问与其相关的非特定实体，问题类型代码及示例为：
a: "种植洋葱时要注意什么？"
b: "洋葱适合什么生长温度？"
c: "洋葱适合什么生长湿度？"
d: "洋葱是什么属的作物？"
e: "洋葱有哪些关键的生长阶段？"
f: "洋葱容易感染哪些病？"
g: "洋葱适合生长在什么土壤里？"

以特定的病原菌实体为重点，询问与其相关的非特定实体，问题类型代码及示例为：
h: "锈菌容易危害哪些作物?" or "哪些作物易受锈菌危害?"
i: "锈菌属于什么属?"

以特定的作物实体和另外一种特定的实体为重点(代码l-n)，询问他们两者之间是否存在关系，问题类型代码及示例为：
l: "洋葱适合生长在白垩土里吗？"
m: "洋葱容易受到锈菌感染吗？"
n: "果实发育和种子形成阶段对洋葱关键吗？"

不属于以上任何一种问题，问题代码为x。

注意：“土壤”，“阶段”等词不是特定的实体，而是一类实体的泛称。
]
2.从用户输入中，提取实体内容以及用户输入语句整体的问题代码。
3.根据用户输入抽取，不要推理。
4.注意json格式，在json中不要出现//

\n{format_instructions}

用户输入: {input}

输出:
"""

prompt = PromptTemplate(
    template=template,
    partial_variables={"format_instructions": format_instructions},
    input_variables=["input"],
)

chain = LLMChain(llm=llm, prompt=prompt)


def parse_query(query_sentence):
    llm_output = chain.run(input=query_sentence)
    return output_parser.parse(llm_output)


# {'crop': ['洋葱'], 'pathogen': [], 'soil': [], 'growthStage': ['果实发育阶段'], 'question_type_code': 'n'}
def query_pathogen(session, pathogen):
    pass


def generate_answer(parsed_query):
    code = parsed_query["question_type_code"]
    if code == question_type_dict["undetected_question"]:
        return "x"

    if code in question_type_dict["pathogen_center_question"]:
        try:
            with create_neo4j_transaction() as session:
                search_results = query_pathogen(session, parsed_query["pathogen"])
                # 没有检索到合适的结果
                if isinstance(search_results, str):
                    return "x"
                else:
                    if (
                        code == "h"
                    ):  # "锈菌容易危害哪些作物?" or "哪些作物易受锈菌危害?"
                        return "ans"
                    else:  # "锈菌属于什么属?"
                        return "ans"
        except Exception as e:
            # 发生异常时，返回错误信息
            print("Error in query_pathogen")
            raise

    crop_knowledge_dict = {}
    ans_str = ""
    try:
        with create_neo4j_transaction() as session:
            search_results = query_dict(session, parsed_query["crop"])
            # 没有检索到合适的结果
            if isinstance(search_results, str):
                return "x"
            else:
                crop_knowledge_dict = search_results
    except Exception as e:
        # 发生异常时，返回错误信息
        print("Error in query_dict")
        raise

    if code in question_type_dict["crop_center_question"]:
        if code == "a":  # 种植洋葱时要注意什么？
            ans_str = (
                "种植"
                + parsed_query["crop"]
                + "，应当注意："
                + crop_knowledge_dict["caution"]
            )
        elif code == "b":  # 洋葱适合什么生长温度
            ans_str = (
                parsed_query["crop"]
                + "适合的生长温度为"
                + crop_knowledge_dict["suit_temperature"]
            )
        elif code == "c":  # 洋葱适合什么生长湿度
            ans_str = (
                parsed_query["crop"]
                + "适合的生长湿度为"
                + crop_knowledge_dict["suit_humidity"]
            )
        elif code == "d":  # 洋葱是什么属的作物
            ans_str = (
                parsed_query["crop"]
                + "学名"
                + crop_knowledge_dict["binomial"]
                + "属于"
                + crop_knowledge_dict["family_name"]
                + "属"
                + crop_knowledge_dict["genus_name"]
                + "科"
            )
        elif code == "e":  # 洋葱有哪些关键的生长阶段
            ans_str = (
                parsed_query["crop"]
                + "有如下关键生长阶段"
                + str(crop_knowledge_dict["key_stages"])
            )
        elif code == "f":  # 洋葱容易感染哪些病
            ans_str = (
                parsed_query["crop"]
                + "易感病症及相关病原菌为"
                + str(crop_knowledge_dict["diseases_and_pathogen"])
            )
        else:  # 洋葱适合生长在什么土壤里
            ans_str = (
                parsed_query["crop"]
                + "适宜生长的土壤类型为"
                + str(crop_knowledge_dict["suit_soil"])
            )
    elif code in question_type_dict["double_entity_question"]:
        if code == "l":  # 洋葱适合生长在白垩土里吗
            if parsed_query["soil"] in crop_knowledge_dict["suit_soil"]:
                ans_str = parsed_query["crop"] + "适宜生长于" + parsed_query["soil"]
            else:
                ans_str = parsed_query["crop"] + "不适宜生长于" + parsed_query["soil"]
        elif code == "m":  # 洋葱容易受到锈菌感染吗
            if (
                parsed_query["pathogen"]
                in crop_knowledge_dict["diseases_and_pathogen"].values()
            ):
                ans_str = (
                    parsed_query["crop"] + "容易受" + parsed_query["pathogen"] + "感染"
                )
            else:
                ans_str = (
                    parsed_query["crop"]
                    + "不容易受"
                    + parsed_query["pathogen"]
                    + "感染"
                )
        else:  # 果实发育和种子形成阶段对洋葱关键吗
            pass
    else:
        ans_str = "x"

    return ans_str


question_type_dict = {
    "crop_center_question": ["a", "b", "c", "d", "e", "f", "g"],
    "pathogen_center_question": ["h", "i"],
    "double_entity_question": ["l", "m", "n"],
    "undetected_question": "x",
}

"""
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
		"key_stages": record["key_stages"],
		"diseases_and_pathogen": record["diseases_and_pathogen"],
	}
"""
