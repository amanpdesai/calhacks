import pymysql  
import openai

# Connect to the SingleStore database
connection = pymysql.connect(
    host='svc-f90325a9-8b27-495d-a436-7cb5c7764c62-dml.aws-oregon-3.svc.singlestore.com',
    user='admin',
    password='Flj3M3k6N1of0CXLuR73YiPRMkf9JiTj',
    database='instructions'
)

# Function to create a chat log table for a specific step
def create_chat_log_table(step_name, translation):
    with connection.cursor() as cursor:
        # Ensure table names have no spaces or special characters (e.g., replace spaces with underscores)
        step_name = step_name.replace(" ", "_")
        
        # Create table with three columns: Speaker, Message, and Translation (using backticks)
        sql = f"""
        CREATE TABLE IF NOT EXISTS  (
            Speaker VARCHAR(50),
            Message TEXT,
        );
        """
        cursor.execute(sql)
        connection.commit()
        print(f"Table '{step_name}' created successfully!")

        # Insert the translation into the Translation column (only one row, with translation in the Translation column)
        cursor.execute(f"INSERT INTO `{step_name}` (Speaker, Message, Translation) VALUES (%s, %s, %s)", ('Chat', 'Simplified translation provided by Chat', translation))
        connection.commit()
        print(f"Translation added to table '{step_name}' : {translation}")

openai.api_key = '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'

# Function to get the simplified translation of a medical procedure step
def get_simplified_instruction(step_instruction):
    prompt = f"""
    Please simplify the following medical procedure step into a more convenient and understandable instruction for the user:
    
    Step: {step_instruction}
    """

    # Use the `gpt-3.5-turbo` model (you can change this to gpt-4 if available)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "You are a helpful assistant that simplifies medical instructions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,  # Limit the response length
        temperature=0.7  # Controls creativity; adjust as necessary
    )
    
    # Extract and return the simplified instruction from the response
    simplified_instruction = response['choices'][0]['message']['content'].strip()
    print(f"Simplified instruction generated: {simplified_instruction}")  # Print statement to confirm translation
    return simplified_instruction

# Example usage:
step_name = "Boil the Egg"  # Hardcoded step name
instruction = get_simplified_instruction(step_name)
create_chat_log_table(step_name, instruction)

# Close the connection after operations are complete
connection.close()
