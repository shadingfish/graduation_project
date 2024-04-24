from dotenv import load_dotenv
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import (
    PromptTemplate,
)
from langchain.chains import LLMChain
import logging

logger = logging.getLogger(__name__)

from utils.store_data import create_neo4j_transaction, query_dict, cn_query_dict

load_dotenv()
llm = ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0)

# 直接向GPT-3.5提问的模板
normal_prompt = PromptTemplate(
    template="""
    请使用中文回答
    输入 question: {input}
    输出 direct Answer: (Provide a straightforward string answer)
    """,
    input_variables=["input"],
)


# 进行复杂的检索语句解析模板
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

string_template = """
1.根据后续[]中的内容，了解不同类型问题的问题类型代码，问题类型代码是一个字符串,其值为a-n中任意一个字母或者为x。
[只关注于一种主要实体(代码a-k)。
对于每个问题代码我会给出一些例子，但必须注意这些例子并不是唯一的答案。
问题里的实体可以是任意符合语义的名词，只要问题的结构符合代码即可，比如"种植洋葱时要注意什么？"或和"玉米的种植有什么注意事项"都属于代码a。

以特定的作物实体为重点，询问与其相关的非特定实体，问题类型代码及示例为：
a: "种植洋葱时要注意什么？", "甜玉米的种植有什么要注意的点", "种植大豆有什么注意事项"
b: "洋葱适合什么生长温度？", "小麦在什么温度下生长适宜", "水稻适合在什么温度下生长", "种植马铃薯的适宜温度是多少"
c: "洋葱适合什么生长湿度？", "大麦在什么湿度下生长适宜", "甘蔗适合在什么湿度下生长", "种植甜菜的适宜湿度是多少"
d: "洋葱是什么属的作物？", "棉花属于哪个分类学属", "哪个种属下包含油菜", "植物学中棕榈属于哪个种"
e: "洋葱有哪些关键的生长阶段？", "哪些生长阶段对烟草是关键的", "种植豌豆时最重要的阶段是什么", "花生的培育过程中关键的生长阶段有哪些"
f: "洋葱容易感染哪些病？", "卷心菜有哪些易染的病害", "种西兰花时要提防哪些病", "菠菜爱得哪些病"
g: "洋葱适合生长在什么土壤里？", "什么土壤适合胡萝卜生长", "种植柑橘什么类型的土地最合适", "苹果生长的适宜土质是什么"

以特定的病原菌实体为重点，询问与其相关的非特定实体，问题类型代码及示例为：
h: "锈菌容易危害哪些作物?", "哪些作物易受马铃薯疫霉危害?", "高粱黑粉菌喜欢侵害哪些植物", "枯萎镰刀菌的常见宿主有哪些"
i: "锈菌属于什么属?", "灰葡萄孢属于哪个分类学属", "哪个种属下包含黄曲霉", "黄萎病菌是哪个属的"

以特定的作物实体和另外一种特定的实体为重点(代码l-n)，询问他们两者之间是否存在关系，问题类型代码及示例为：
l: "洋葱适合生长在白垩土里吗？", "适合使用泥炭土培育香蕉吗", "种植辣椒用砂壤土合适吗", "西瓜喜欢生长在沙质土壤中吗"
m: "洋葱容易受到锈菌感染吗？", "黄瓜容易被黑粉菌侵染吗", "烟草花叶病毒容易寄生燕麦吗", "杏仁爱感染青枯病菌吗"
n: "果实发育和种子形成阶段对洋葱关键吗？", "授粉和受精阶段是种植姜的重要阶段吗", "芒果的生长过程中成熟阶段关键吗", "开花阶段对芦笋的影响大么"

不属于以上任何一种问题，问题代码为x。

注意：“土壤”，“阶段”等词不是特定的实体，而是一类实体的泛称。
]
2.从用户输入中，提取实体内容以及用户输入语句整体的问题代码。
3.根据用户输入抽取，不要推理。
4.注意json格式，在json中不要出现//

\n{format_instructions}

输入 input: {input}
输出 direct Answer: (Provide a straightforward array answer)
"""

prompt = PromptTemplate(
    # examples=examples,
    template=string_template,
    partial_variables={"format_instructions": format_instructions},
    input_variables=["input"],
)

# example_prompt = StringPromptTemplate(
#     template=string_template
# )
#
# prompt = FewShotPromptTemplate(
#     examples=examples,
#     example_prompt=example_prompt,
#     suffix="input: {input}",
#     partial_variables={"format_instructions": format_instructions},
#     input_variables=["input"],
# )

question_type_dict = {
    "crop_center_question": ["a", "b", "c", "d", "e", "f", "g"],
    "pathogen_center_question": ["h", "i"],
    "double_entity_question": ["l", "m", "n"],
    "undetected_question": "x",
}


def query_gpt(query_sentence):
    print("Directly querying")
    normal_chain = normal_prompt | llm
    ans = normal_chain.invoke({"input": query_sentence})
    return ans.content


def parse_query(query_sentence):
    print("In parse_query")
    chain = LLMChain(llm=llm, prompt=prompt)
    if query_sentence == "":
        return ""
    llm_output = chain.run(input=query_sentence)
    return output_parser.parse(llm_output)


# {'crop': ['洋葱'], 'pathogen': [], 'soil': [], 'growthStage': ['果实发育阶段'], 'question_type_code': 'n'}
def query_pathogen(session, pathogen):
    pass


def generate_answer(parsed_query):
    print("In generate_answer")
    print(parsed_query)
    code = parsed_query["question_type_code"]
    if code == question_type_dict["undetected_question"]:
        print("Check if question is undetected")
        return "x", []

    if code in question_type_dict["pathogen_center_question"]:
        print("Check pathogen center question")
        try:
            with create_neo4j_transaction() as session:
                search_results = query_pathogen(session, parsed_query["pathogen"])
                # 没有检索到合适的结果
                if isinstance(search_results, str):
                    return "x", []
                else:
                    if (
                        code == "h"
                    ):  # "锈菌容易危害哪些作物?" or "哪些作物易受锈菌危害?"
                        return "ans", []
                    else:  # "锈菌属于什么属?"
                        return "ans", []
        except Exception as e:
            # 发生异常时，返回错误信息
            print("Error in query_pathogen")
            raise

    crop_knowledge_dict = {}
    ans_str = ""
    try:
        with create_neo4j_transaction() as session:
            search_results = cn_query_dict(session, parsed_query["crop"][0])
            print(search_results)
            # 没有检索到合适的结果
            if isinstance(search_results, str):
                print("No suitable results in neo4j")
                return "x", []
            else:
                crop_knowledge_dict = search_results
    except Exception as e:
        # 发生异常时，返回错误信息
        print("Error in query_dict")
        raise

    print("Successfully fetched neo4j data (crop_knowledge_dict)")
    if code in question_type_dict["crop_center_question"]:
        print("Generating crop_center question...")
        if code == "a":  # 种植洋葱时要注意什么？
            print(parsed_query["crop"][0])
            print(crop_knowledge_dict[0]["caution"])
            ans_str = "种植{}，应当注意：{}".format(
                parsed_query["crop"][0], crop_knowledge_dict[0]["caution"]
            )
        elif code == "b":  # 洋葱适合什么生长温度
            ans_str = "{}适合的生长温度为{}".format(
                parsed_query["crop"][0], crop_knowledge_dict[0]["suit_temperature"]
            )
        elif code == "c":  # 洋葱适合什么生长湿度
            ans_str = "{}适合的生长湿度为{}".format(
                parsed_query["crop"][0], crop_knowledge_dict[0]["suit_humidity"]
            )
        elif code == "d":  # 洋葱是什么属的作物
            ans_str = "{}学名{}属于{}属{}科".format(
                parsed_query["crop"][0],
                crop_knowledge_dict[0]["binomial"],
                crop_knowledge_dict[0]["family_name"],
                crop_knowledge_dict[0]["genus_name"],
            )
        elif code == "e":  # 洋葱有哪些关键的生长阶段
            ans_str = "{}有如下关键生长阶段{}".format(
                parsed_query["crop"][0], str(crop_knowledge_dict[0]["key_stages"])
            )
        elif code == "f":  # 洋葱容易感染哪些病
            ans_str = "{}易感病症及相关病原菌为{}".format(
                parsed_query["crop"][0],
                str(crop_knowledge_dict[0]["diseases_and_pathogen"]),
            )
        else:  # 洋葱适合生长在什么土壤里
            ans_str = "{}适宜生长的土壤类型为{}".format(
                parsed_query["crop"][0], str(crop_knowledge_dict[0]["suit_soil"])
            )
    elif code in question_type_dict["double_entity_question"]:
        if code == "l":  # 洋葱适合生长在白垩土里吗
            if parsed_query["soil"][0] in crop_knowledge_dict[0]["suit_soil"]:
                ans_str = "{}适宜生长于{}".format(
                    parsed_query["crop"][0], parsed_query["soil"][0]
                )
            else:
                ans_str = "{}不适宜生长于{}".format(
                    parsed_query["crop"][0], parsed_query["soil"][0]
                )
        elif code == "m":  # 洋葱容易受到锈菌感染吗
            if any(
                parsed_query["pathogen"][0] in disease["pathogen"]
                for disease in crop_knowledge_dict[0]["diseases_and_pathogen"]
            ):
                ans_str = "{}容易受{}感染".format(
                    parsed_query["crop"][0], parsed_query["pathogen"][0]
                )
            else:
                ans_str = "{}不容易受{}感染".format(
                    parsed_query["crop"][0], parsed_query["pathogen"][0]
                )
        else:  # 果实发育和种子形成阶段对洋葱关键吗
            if parsed_query["growthStage"][0] in crop_knowledge_dict[0]["key_stages"]:
                ans_str = "{}阶段对{}关键".format(
                    parsed_query["growthStage"][0], parsed_query["crop"][0]
                )
            else:
                ans_str = "{}阶段对{}不关键".format(
                    parsed_query["growthStage"][0], parsed_query["crop"][0]
                )
    else:
        ans_str = "x"

    print(f"Finish generating answer: {ans_str}")

    return ans_str, crop_knowledge_dict


# """
# 	data = {
# 		"binomial": record["binomial"],
# 		"en_name": record["en_name"],
# 		"en_common_names": record["en_common_names"],
# 		"cn_name": record["cn_name"],
# 		"cn_common_names": record["cn_common_names"],
# 		"suit_humidity": record["suit_humidity"],
# 		"suit_temperature": record["suit_temperature"],
# 		"caution": record["caution"],
# 		"family_name": record["family_name"],
# 		"genus_name": record["genus_name"],
# 		"suit_soil": record["suit_soil"],
# 		"key_stages": record["key_stages"],
# 		"diseases_and_pathogen": record["diseases_and_pathogen"],
# 	}
# """

# 以特定的作物实体为重点，询问与其相关的非特定实体，问题类型代码及示例为：
# a: "种植洋葱时要注意什么？", "甜玉米的种植有什么要注意的点", "种植大豆有什么注意事项"
# b: "小麦适合什么生长温度？", "洋葱适合什么生长温度？"
# c: "洋葱适合什么生长湿度？"
# d: "洋葱是什么属的作物？"
# e: "洋葱有哪些关键的生长阶段？"
# f: "洋葱容易感染哪些病？"
# g: "洋葱适合生长在什么土壤里？"
#
# 以特定的病原菌实体为重点，询问与其相关的非特定实体，问题类型代码及示例为：
# h: "锈菌容易危害哪些作物?" or "哪些作物易受锈菌危害?"
# i: "锈菌属于什么属?"
#
# 以特定的作物实体和另外一种特定的实体为重点(代码l-n)，询问他们两者之间是否存在关系，问题类型代码及示例为：
# l: "洋葱适合生长在白垩土里吗？"
# m: "洋葱容易受到锈菌感染吗？"
# n: "果实发育和种子形成阶段对洋葱关键吗？"

# 以特定的作物实体为重点，询问与其相关的非特定实体，问题类型代码及示例为：
# a: "种植洋葱时要注意什么？", "甜玉米的种植有什么要注意的点", "种植大豆有什么注意事项"
# b: "洋葱适合什么生长温度？", "小麦在什么温度下生长适宜", "水稻适合在什么温度下生长", "种植马铃薯的适宜温度是多少"
# c: "洋葱适合什么生长湿度？", "大麦在什么湿度下生长适宜", "甘蔗适合在什么湿度下生长", "种植甜菜的适宜湿度是多少"
# d: "洋葱是什么属的作物？", "棉花属于哪个分类学属", "哪个种属下包含油菜", "植物学中棕榈属于哪个种"
# e: "洋葱有哪些关键的生长阶段？", "哪些生长阶段对烟草是关键的", "种植豌豆时最重要的阶段是什么", "花生的培育过程中关键的生长阶段有哪些"
# f: "洋葱容易感染哪些病？", "卷心菜有哪些易染的病害", "种西兰花时要提防哪些病", "菠菜爱得哪些病"
# g: "洋葱适合生长在什么土壤里？", "什么土壤适合胡萝卜生长", "种植柑橘什么类型的土地最合适", "苹果生长的适宜土质是什么"
#
# 以特定的病原菌实体为重点，询问与其相关的非特定实体，问题类型代码及示例为：
# h: "锈菌容易危害哪些作物?", "哪些作物易受马铃薯疫霉危害?", "高粱黑粉菌喜欢侵害哪些植物", "枯萎镰刀菌的常见宿主有哪些"
# i: "锈菌属于什么属?", "灰葡萄孢属于哪个分类学属", "哪个种属下包含黄曲霉", "黄萎病菌是哪个属的"
#
# 以特定的作物实体和另外一种特定的实体为重点(代码l-n)，询问他们两者之间是否存在关系，问题类型代码及示例为：
# l: "洋葱适合生长在白垩土里吗？", "适合使用泥炭土培育香蕉吗", "种植辣椒用砂壤土合适吗", "西瓜喜欢生长在沙质土壤中吗"
# m: "洋葱容易受到锈菌感染吗？", "黄瓜容易被黑粉菌侵染吗", "烟草花叶病毒容易寄生燕麦吗", "杏仁爱感染青枯病菌吗"
# n: "果实发育和种子形成阶段对洋葱关键吗？", "授粉和受精阶段是种植姜的重要阶段吗", "芒果的生长过程中成熟阶段关键吗", "开花阶段对芦笋的影响大么"
