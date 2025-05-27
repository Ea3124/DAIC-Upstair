from openai import OpenAI  # openai==1.52.2
import json
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("UPSTAGE_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.upstage.ai/v1"
)
 
# Step 1: Setup and define the function
# This is an example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def print_gpa(gpa: float):
    scholarship = "없음"
    if gpa == None:
        gpa = 0
    elif gpa >3.5:
        scholarship = "부산 장학금"
    elif gpa >3.0:
        scholarship = "부산대 장학금"
    elif gpa >2.5:
        scholarship = "금정구 장학금"
    elif gpa >2.0:
        scholarship = "학교 장학금"
    else:
        scholarship = "없다"
    return scholarship
 
def print_location(location: str):
    if location == None:
        location = "Unknown"
    elif location == "부산":
        location = "부산대학교"
    elif location == "금정구":
        location = "금정구청"
    else:
        location = "부산대학교"
    return location

# Step 2: Send the query and available functions to the model
def run_conversation():
    messages = [
        {
            "role": "user",
            "content": "금정구 거주자가 GPA 3.5 이상으로 받을 수 있는 장학금이 뭐야?",
        }
    ]
 
    tools = [
        {
            "type": "function",
            "function": {
                "name": "print_gpa",
                "description": "GPA 조건에 맞는 데이터베이스 출력을 만드는 쿼리 내장 함수",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "gpa": {
                            "type": "number",
                            "description": "GPA 조건",
                        },
                    },
                    "required": ["gpa"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "print_location",
                "description": "Location 조건에 맞는 데이터베이스 출력을 만드는 쿼리 내장 함수",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location 조건",
                        },
                    },
                    "required": ["location"],
                },
            },
        },
    ]
 
    # Step 3: Check if the model has requested a function call
    # The model identifies that the query requires external data (e.g., real-time weather) and decides to call a relevant function, such as a weather API.
    response = client.chat.completions.create(
        model="solar-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
 
    # Step 4: Execute the function call
    # The JSON response from the model may not always be valid, so handle errors appropriately
    if tool_calls:
        available_functions = {
            "print_gpa": print_gpa,
            "print_location": print_location,
        }  # You can define multiple functions here as needed
        messages.append(response_message)  # Add the assistant's reply to the conversation history
 
        # Step 5: Process each function call and provide the results to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            # 함수에 따른 인자 전달
            if function_name == "print_gpa":
                function_response = function_to_call(
                    gpa=function_args.get("gpa")
                )
            elif function_name == "print_location":
                function_response = function_to_call(
                    location=function_args.get("location")
                )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # Append the function response to the conversation history
 
        # Step 6: Generate a new response from the model using the updated conversation history
        second_response = client.chat.completions.create(
            model="solar-mini",
            messages=messages,
        )
        return second_response  # Return the final response from the model
 
response = run_conversation()
print(response.choices[0].message.content)